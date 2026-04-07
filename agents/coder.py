import re
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgentState
from config import CODER_MODEL

CODER_SYSTEM_PROMPT = """You are an Expert Python Developer in an autonomous software development team. Your role is to write clean, production-quality Python code based strictly on the technical specification provided.

YOUR CAPABILITIES AND BOUNDARIES:
1. You ONLY write Python code. You MUST NOT add features, deviate from, or reinterpret the spec.
2. If review feedback is provided, you must address EVERY point in the feedback while keeping the code aligned with the original spec.
3. Your output must be ONLY a single Python code block. No explanations, no commentary, no markdown headers.
4. Do not include any internal reasoning, <think> tags, or preamble.

OUTPUT FORMAT:
Respond with ONLY the complete Python code. Do not wrap it in markdown code fences. Do not include any text before or after the code.

EXAMPLE OUTPUT:
import sys

def add(a, b):
    return a + b

def main():
    result = add(1, 2)
    print(result)

if __name__ == "__main__":
    main()
"""

def coder_node(state: AgentState) -> dict:
    llm = ChatOllama(model=CODER_MODEL, temperature=0.2)

    # --- Dynamic context assembly ---
    # Start with the plan — the Coder ALWAYS needs this.
    context = f"## TECHNICAL SPEC\n{state['plan']}"

    # If there's review feedback from prior iterations, append it.
    # On iteration 1, review_feedback is an empty list — this block is skipped.
    # On iteration 2+, the Coder sees exactly what the Reviewer flagged.
    if state.get("review_feedback"):
        feedback_history = "\n".join(
            f"--- Iteration {i+1} ---\n{fb}"
            for i, fb in enumerate(state["review_feedback"])
        )
        context += f"\n\n## REVIEW FEEDBACK (fix all issues below)\n{feedback_history}"

    messages = [
        SystemMessage(content=CODER_SYSTEM_PROMPT),
        HumanMessage(content=context)
    ]

    response = llm.invoke(messages)

    # Clean up: strip think tags and markdown code fences.
    # Local models love wrapping code in ```python ... ``` even when told not to.
    clean_code = re.sub(r"<think>.*?</think>", "", response.content, flags=re.DOTALL).strip()
    clean_code = re.sub(r"^```(?:python)?\n?", "", clean_code)
    clean_code = re.sub(r"\n?```$", "", clean_code).strip()

    # Increment the iteration count safely.
    # .get() with default 0 handles the edge case where the key doesn't exist yet.
    new_iteration = state.get("iteration_count", 0) + 1

    return {
        "code": clean_code,
        "iteration_count": new_iteration
    }