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
    print("\n" + "🔍 " + "─" * 57)
    print("   REVIEWER — Evaluating code against spec...")
    print("─" * 60)

    llm = ChatOllama(model=REVIEWER_MODEL, temperature=0.0)
    review_input = f"""## TECHNICAL SPEC
{state['plan']}

## GENERATED CODE
{state['code']}"""

    messages = [
        SystemMessage(content=REVIEWER_SYSTEM_PROMPT),
        HumanMessage(content=review_input)
    ]
    response = llm.invoke(messages)

    raw_output = re.sub(r"<think>.*?</think>", "", response.content, flags=re.DOTALL).strip()

    verdict_match = re.search(r"##\s*VERDICT\s*\n\s*(PASS|FAIL)", raw_output, re.IGNORECASE)
    feedback_match = re.search(r"##\s*FEEDBACK\s*\n(.*)", raw_output, re.DOTALL)

    if verdict_match:
        status = verdict_match.group(1).upper()
    else:
        status = "FAIL"

    if feedback_match:
        feedback = feedback_match.group(1).strip()
    else:
        feedback = "Parser could not extract structured feedback."

    # Live verdict display — user sees the routing decision immediately
    status_icon = "✅" if status == "PASS" else "❌"
    print(f"{status_icon} Verdict: {status}")

    return {
        "status": status,
        "review_feedback": [feedback]
    }