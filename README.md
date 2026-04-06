# Agentic Coding Assistant

A multi-agent software development pipeline that autonomously plans, writes, and reviews code — running entirely on local LLMs via Ollama. No API keys. No cloud. No cost.

---

## How It Works

The system is a LangGraph-orchestrated pipeline with three specialized agents that pass structured state between them in a feedback loop:

```
User Request
     │
     ▼
┌─────────────┐
│   Planner   │  Qwen3:14b — Analyzes the request and produces a structured
│             │  technical spec: approach, functions, dependencies, edge cases.
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Coder    │  DeepSeek-Coder-v2 — Implements the spec. On subsequent
│             │  iterations, incorporates the Reviewer's feedback.
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Reviewer   │  Qwen2.5-Coder:7b — Evaluates correctness, edge case handling,
│             │  and code quality. Returns PASS or FAIL with structured feedback.
└──────┬──────┘
       │
  PASS? ──► Output final code
  FAIL? ──► Back to Coder (max 3 iterations)
```

---

## Why This Architecture?

Most "AI coding assistant" projects are thin wrappers around a single LLM call. This project exists to demonstrate production-grade agentic design patterns:

- **Separation of concerns** — Each agent does one thing well. The Planner never writes code. The Coder never evaluates quality. This mirrors how real engineering teams operate.
- **Heterogeneous model assignment** — Instead of using one model for everything, each agent gets the model best suited to its task. This is how you'd architect a cost- and latency-optimized pipeline in production.
- **Deterministic orchestration** — The routing logic is plain Python, not an LLM. Control flow should be boring and predictable. LLMs generate; code decides.

---

## Architecture

```
agentic-coding-assistant/
├── main.py              # Entry point / test harness
├── config.py            # Model names and loop limits
├── requirements.txt
├── agents/
│   ├── planner.py       # Planner agent + system prompt
│   ├── coder.py         # Coder agent + system prompt
│   └── reviewer.py      # Reviewer agent + output parser
└── graph/
    ├── state.py          # AgentState TypedDict (shared pipeline state)
    └── workflow.py       # LangGraph graph definition + conditional edges
```

### Key Design Decisions

- **Shared state via TypedDict** — `AgentState` is the single source of truth passed through the entire graph. Each agent reads what it needs and writes only its own field.
- **Append-only feedback history** — `review_feedback` uses a LangGraph reducer (`operator.add`) so the Coder sees the full review history across all iterations, not just the last one.
- **Deterministic planning** — The Planner runs at `temperature=0.0`. Same input → same structured spec, every time.
- **`<think>` tag stripping** — Qwen3 sometimes leaks internal reasoning despite being instructed not to. The Planner strips these at the code level as a belt-and-suspenders defense.
- **Loop guard** — `MAX_ITERATIONS = 3` prevents the Coder→Reviewer loop from running indefinitely on hard problems.

---

## Tech Stack

| Layer | Tool |
|---|---|
| Orchestration | [LangGraph](https://github.com/langchain-ai/langgraph) |
| LLM Interface | [LangChain Ollama](https://python.langchain.com/docs/integrations/llms/ollama/) |
| Local LLM Runtime | [Ollama](https://ollama.com/) |
| Planner Model | `qwen3:14b` |
| Coder Model | `deepseek-coder-v2` |
| Reviewer Model | `qwen2.5-coder:7b` |

---

## Getting Started

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/) installed and running

### 1. Pull the required models

```bash
ollama pull qwen3:14b
ollama pull deepseek-coder-v2
ollama pull qwen2.5-coder:7b
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Run

```bash
python main.py
```

The default request in `main.py` is:

```python
run("Build a Python command-line calculator that supports addition, subtraction, multiplication, and division.")
```

Change it to any coding task you want the pipeline to solve.

---

## Project Status

- [x] Phase 1 — Planner Agent
- [ ] Phase 2 — Coder Agent
- [ ] Phase 3 — Reviewer Agent
- [ ] Phase 4 — LangGraph Orchestration
- [ ] Phase 5 — Polish & Documentation

---

## License

MIT