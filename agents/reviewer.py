import re
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgentState
from config import REVIEWER_MODEL

REVIEWER_SYSTEM_PROMPT = """You are a Senior Code Reviewer in an autonomous software development team. Your role is to evaluate generated Python code against its technical specification with rigor and precision.

YOUR CAPABILITIES AND BOUNDARIES:
1. You ONLY evaluate code. You MUST NOT rewrite or suggest replacement code.
2. You must check the code against EVERY requirement in the technical spec, including function signatures, return types, dependencies, and edge case handling.
3. Your verdict must be deterministic: PASS only if the code fully satisfies the spec. Otherwise, FAIL.
4. Do not include any internal reasoning, <think> tags, or preamble.

OUTPUT FORMAT:
You must respond using EXACTLY this Markdown format. No additional text before or after.

## VERDICT
PASS

## FEEDBACK
[If PASS: write "No issues found." If FAIL: list each issue as a separate bullet point. Be specific — reference function names, line behavior, or missing requirements.]

---
EXAMPLE (FAIL case):

## VERDICT
FAIL

## FEEDBACK
- The `validate_inputs` function is missing the type hints specified in the plan: should be `(num1: str, num2: str, operator: str) -> tuple[float, float, str]`.
- The `calculate` function does not raise a custom exception for division by zero as required; it raises a generic ValueError instead.
- The spec requires handling of inputs like '1.5.5', but the current implementation only catches generic ValueError without distinguishing this case.

---
EXAMPLE (PASS case):

## VERDICT
PASS

## FEEDBACK
No issues found.
"""

def reviewer_node(state: AgentState) -> dict:
    # Temperature 0.0 — judgments must be consistent.
    # Same code + same spec should always produce the same verdict.
    llm = ChatOllama(model=REVIEWER_MODEL, temperature=0.0)

    # Multi-input context: the Reviewer needs BOTH the spec and the code to evaluate.
    review_input = f"""## TECHNICAL SPEC\n{state['plan']}\n\n## GENERATED CODE\n{state['code']}"""
    messages = [
        SystemMessage(content=REVIEWER_SYSTEM_PROMPT),
        HumanMessage(content=review_input)
    ]

    response = llm.invoke(messages)

    # Strip think tags as usual
    raw_output = re.sub(r"<think>.*?</think>", "", response.content, flags=re.DOTALL).strip()

    # Parse the Reviewer's structured Markdown response.
    verdict_match = re.search(r"## VERDICT\s*(PASS|FAIL)", raw_output, re.IGNORECASE)
    feedback_match = re.search(r"## FEEDBACK\s*(.*)", raw_output, re.DOTALL)

    # Defensive fallback: if parsing fails, default to FAIL.
    # Better to retry an extra time than crash the graph or pass broken code.
    if verdict_match:
        status = verdict_match.group(1).upper()
    else:
        status = "FAIL"

    if feedback_match:
        feedback = feedback_match.group(1).strip()
    else:
        feedback = "Parser could not extract structured feedback. Reviewing model output may have deviated from the required format."

    return {
        "status": status,
        "review_feedback": [feedback]  # Wrapped in list because of the operator.add reducer
    }