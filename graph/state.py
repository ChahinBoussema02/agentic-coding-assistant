import operator
from typing import TypedDict, Annotated, List, Literal

class AgentState(TypedDict):
    # The raw user request — written once at invocation, never modified
    user_request: str

    # The Planner's structured spec — written once by planner_node
    plan: str

    # The Coder's generated code — overwritten each iteration with the latest version
    code: str

    # Reducer: each Reviewer pass APPENDS feedback instead of overwriting.
    # On iteration 3, the Coder sees all prior feedback history.
    review_feedback: Annotated[List[str], operator.add]

    # The Reviewer's verdict — the conditional edge reads this to route.
    # Literal is a static type hint only, NOT runtime enforcement.
    # Actual validation happens in the Reviewer's output parser (Phase 3).
    status: Literal["PENDING", "PASS", "FAIL"]

    # Loop counter — initialized at invocation via the run() function.
    # Compared against MAX_ITERATIONS to prevent infinite loops.
    iteration_count: int