from agents.planner import planner_node

def run(user_request: str):
    """Minimal test harness — calls the Planner node directly."""

    # Simulate the initial state that the graph would normally provide
    initial_state = {
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

    # Call the planner node directly — same way LangGraph would
    result = planner_node(initial_state)

    print("\nPLANNER OUTPUT:")
    print("-" * 60)
    print(result["plan"])
    print("-" * 60)

if __name__ == "__main__":
    run("Build a Python command-line calculator that supports addition, subtraction, multiplication, and division.")
