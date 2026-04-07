from agents.coder import coder_node
from agents.planner import planner_node
from agents.reviewer import reviewer_node

def run(user_request: str):
    """Minimal test harness — calls the Planner node directly."""

    # Simulate the initial state that the graph would normally provide
    state = {
        "user_request": user_request,
        "plan": "",
        "code": "",
        "review_feedback": [],
        "status": "PENDING",
        "iteration_count": 0
    }

    print("=" * 60)
    print("PLANNER INPUT:")
    print(f"  {user_request}")
    print("=" * 60)

    # Phase 1: Plan
    planner_result = planner_node(state)
    state.update(planner_result)


    print("\nPLANNER OUTPUT:")
    print("-" * 60)
    print(state["plan"])
    print("-" * 60)

    # Phase 2: Code
    coder_result = coder_node(state)
    state.update(coder_result)

    print("\nCODER OUTPUT:")
    print("-" * 60)
    print(state["code"])
    print("-" * 60)
    print(f"\nIteration count: {state['iteration_count']}")

    # Phase 3: Review
    # Manual merge for review_feedback because we're not in a graph yet —
    # the reducer only fires inside LangGraph. We simulate it here.
    review_result = reviewer_node(state)
    state["status"] = review_result["status"]
    state["review_feedback"] = state["review_feedback"] + review_result["review_feedback"]

    print("\nREVIEWER OUTPUT:")
    print("-" * 60)
    print(f"VERDICT: {state['status']}")
    print(f"\nFEEDBACK:")
    print(state["review_feedback"][-1])
    print("-" * 60)
    print(f"\nIteration count: {state['iteration_count']}")

if __name__ == "__main__":
    run("Build a Python command-line calculator that supports addition, subtraction, multiplication, and division.")
