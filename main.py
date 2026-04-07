import argparse
import os
from datetime import datetime
from graph.workflow import app
from config import MAX_ITERATIONS

OUTPUT_DIR = "output"


def write_output_file(code: str, status: str) -> str:
    """Write generated code to a timestamped file. Returns the file path."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = "generated" if status == "PASS" else "failed"
    filename = f"{prefix}_{timestamp}.py"
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "w") as f:
        f.write(code)

    return filepath


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

    final_state = app.invoke(initial_state)

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

    output_path = write_output_file(final_state["code"], final_state["status"])

    # --- Final status reporting with explicit failure mode detection ---
    print("\n" + "=" * 60)

    if final_state["status"] == "PASS":
        print(f"✅ FINAL STATUS: PASS — Code approved by Reviewer")
    elif final_state["iteration_count"] >= MAX_ITERATIONS:
        print(f"⚠️  FINAL STATUS: MAX ITERATIONS REACHED")
        print(f"   The Coder attempted {MAX_ITERATIONS} times without satisfying the Reviewer.")
        print(f"   The last generated code has been saved for inspection.")
    else:
        print(f"❌ FINAL STATUS: FAIL — Workflow terminated unexpectedly")

    print(f"   TOTAL ITERATIONS: {final_state['iteration_count']}")
    print(f"   OUTPUT FILE:      {output_path}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Agentic Multi-Agent Coding Assistant — Plan, code, and review autonomously using local LLMs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python main.py "Build a Python CLI calculator"
  python main.py "Create a script that processes CSV files and outputs JSON"
"""
    )
    parser.add_argument(
        "request",
        type=str,
        help="The coding task you want the agent system to solve (in quotes)."
    )
    args = parser.parse_args()

    run(args.request)


if __name__ == "__main__":
    main()