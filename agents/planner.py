import re
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgentState
from config import PLANNER_MODEL

PLANNER_SYSTEM_PROMPT = """You are the Lead System Architect in an autonomous software development team. Your role is to analyze user requests and design concrete, highly structured technical specifications.

YOUR CAPABILITIES AND BOUNDARIES:
1. You ONLY plan and design. You MUST NOT write any executable code.
2. Your output will be parsed directly by a downstream Coder agent. It must be deterministic, clear, and follow the exact format requested.
3. You must anticipate potential failures and explicitly define edge cases.
4. Do not include any internal reasoning, <think> tags, or preamble.

OUTPUT FORMAT:
You must respond using EXACTLY the Markdown format below. Do not include any introductory or concluding conversational text.

## APPROACH
[Provide a concise 2-3 sentence explanation of the architectural strategy and how the program will solve the problem.]

## FUNCTIONS
- `function_name(args)`: [Clear description of what this function does, its logic, and its expected return type.]

## DEPENDENCIES
- [List any Python standard library or third-party packages required.]

## EDGE CASES
- [List specific errors, edge cases, or missing inputs that the implementation must handle.]

---
EXAMPLE:

USER REQUEST: "Build a Python script to check if a list of websites are online."

YOUR EXACT OUTPUT:
## APPROACH
We will use the standard `requests` library to send HTTP GET requests to each URL. To ensure performance with large lists, we will implement concurrent checking using `concurrent.futures.ThreadPoolExecutor`.

## FUNCTIONS
- `check_site(url: str) -> dict`: Sends a GET request with a 5-second timeout and returns a dictionary containing the URL and its status (Up/Down/Error).
- `main(url_list: list) -> None`: Orchestrates the thread pool, gathers the results from `check_site`, and prints a formatted summary report to the console.

## DEPENDENCIES
- `requests` (third-party, for HTTP calls)
- `concurrent.futures` (standard library, for thread pooling)

## EDGE CASES
- URLs provided without the 'http://' or 'https://' scheme.
- Timeouts from slow-to-respond servers.
- DNS resolution failures for invalid or malformed domains.
"""

def planner_node(state: AgentState) -> dict:
    print("\n" + "🧠 " + "─" * 58)
    print("   PLANNER — Analyzing request and designing spec...")
    print("─" * 60)

    llm = ChatOllama(model=PLANNER_MODEL, temperature=0.0)
    messages = [
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(content=state["user_request"])
    ]
    response = llm.invoke(messages)
    clean_plan = re.sub(r"<think>.*?</think>", "", response.content, flags=re.DOTALL).strip()

    print("✓ Plan generated")
    return {"plan": clean_plan}