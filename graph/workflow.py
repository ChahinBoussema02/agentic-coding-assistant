from langgraph.graph import StateGraph, END
from graph.state import AgentState
from agents.planner import planner_node
from agents.coder import coder_node
from agents.reviewer import reviewer_node
from config import MAX_ITERATIONS

def router(state: AgentState) -> str:
    """
    Conditional edge function. Inspects state and returns the name of the next node.
    This is the deterministic "Iterater" — pure Python, zero LLM calls, fully predictable.
    """
    # Success path — always check first
    if state["status"] == "PASS":
        return "end"
    
     # Loop guard — prevent infinite iteration on hard problems
    if state["iteration_count"] >= MAX_ITERATIONS:
        return "end"
    
    # Otherwise, the Reviewer found issues and we still have iterations left
    return "coder"

def build_workflow():
    """Constructs and compiles the LangGraph workflow."""

    # Step 1: Instantiate the graph with our state schema.
    # LangGraph uses the schema to know which fields exist and which have reducers.
    workflow = StateGraph(AgentState)

     # Step 2: Register each agent as a node.
    # The first argument is the node's name (used by edges to reference it).
    # The second is the function to execute when the node is reached.
    workflow.add_node("planner", planner_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("reviewer", reviewer_node)

    # Step 3: Define the entry point — where execution starts.
    workflow.set_entry_point("planner")

    # Step 4: Add the static (always-fires) edges.
    # Planner always goes to Coder. Coder always goes to Reviewer.
    workflow.add_edge("planner", "coder")
    workflow.add_edge("coder", "reviewer")

    # Step 5: Add the conditional edge after the Reviewer.
    # This is where the router function gets called.
    # The mapping dict translates the router's return string into actual node names.
    workflow.add_conditional_edges(
        "reviewer",
        router,
        {
            "coder": "coder",   # Router returns "coder" → loop back
            "end": END           # Router returns "end" → finish workflow
        }
    )

    # Step 6: Compile the graph into an executable workflow.
    return workflow.compile()

# Build once at module import time so we don't rebuild on every invocation
app = build_workflow()

    
