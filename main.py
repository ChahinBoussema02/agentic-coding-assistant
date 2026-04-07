from graph.workflow import app


def run(user_request: str):
    initial_state = {
        "user_request": user_request,
        "plan": "",
        "code": "",
        "review_feedback": [],
        "status": "PENDING",
        "iteration_count": 0
    }

    print("=" * 60)
    print("USER REQUEST:")
    print(f"  {user_request}")
    print("=" * 60)

    # Invoke the compiled graph. LangGraph handles all execution and state merging.
    final_state = app.invoke(initial_state)

    # --- Report ---
    print("\n" + "=" * 60)
    print("FINAL PLAN")
    print("=" * 60)
    print(final_state["plan"])

    print("\n" + "=" * 60)
    print("FINAL CODE")
    print("=" * 60)
    print(final_state["code"])

    print("\n" + "=" * 60)
    print("REVIEW HISTORY")
    print("=" * 60)
    for i, feedback in enumerate(final_state["review_feedback"], 1):
        print(f"\n--- Review {i} ---")
        print(feedback)

    print("\n" + "=" * 60)
    print(f"FINAL STATUS: {final_state['status']}")
    print(f"TOTAL ITERATIONS: {final_state['iteration_count']}")
    print("=" * 60)


if __name__ == "__main__":
    run("Build a Python script that reads a CSV file of employee records (name, department, salary) and outputs a JSON summary showing the average salary per department, sorted from highest to lowest average.")