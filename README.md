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
├── main.py              # Entry point with CLI and output handling
├── config.py            # Model names and loop limits
├── requirements.txt
├── agents/
│   ├── planner.py       # Planner agent + system prompt
│   ├── coder.py         # Coder agent + system prompt
│   └── reviewer.py      # Reviewer agent + output parser
├── graph/
│   ├── state.py         # AgentState TypedDict (shared pipeline state)
│   └── workflow.py      # LangGraph graph definition + conditional edges
└── output/              # Generated code files (timestamped)
```

### Key Design Decisions

- **Shared state via TypedDict** — `AgentState` is the single source of truth passed through the entire graph. Each agent reads what it needs and writes only its own field.
- **Append-only feedback history** — `review_feedback` uses a LangGraph reducer (`operator.add`) so the Coder sees the full review history across all iterations, not just the last one.
- **Deterministic planning** — The Planner runs at `temperature=0.0`. Same input → same structured spec, every time.
- **`<think>` tag stripping** — Qwen3 sometimes leaks internal reasoning despite being instructed not to. The Planner strips these at the code level as a belt-and-suspenders defense.
- **Loop guard** — `MAX_ITERATIONS = 3` prevents the Coder→Reviewer loop from running indefinitely on hard problems.
- **Defensive parser fallback** — If the Reviewer's output can't be parsed, the system defaults to FAIL rather than silently passing broken code. Always fail closed, never open.

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
python main.py "Build a Python command-line calculator that supports addition, subtraction, multiplication, and division."
```

Pass any coding task as a quoted string. Generated code is written to the `output/` directory with a timestamp.

---

## Sample Run

```
$ python main.py "Build a Python function that checks if a string is a palindrome, ignoring spaces and capitalization."

============================================================
USER REQUEST:
  Build a Python function that checks if a string is a palindrome...
============================================================

🧠 ──────────────────────────────────────────────────────────
   PLANNER — Analyzing request and designing spec...
────────────────────────────────────────────────────────────
✓ Plan generated

⚙️  ─────────────────────────────────────────────────────────
   CODER — Iteration 1: Generating code...
────────────────────────────────────────────────────────────
✓ Code generated (3 lines)

🔍 ─────────────────────────────────────────────────────────
   REVIEWER — Evaluating code against spec...
────────────────────────────────────────────────────────────
✅ Verdict: PASS

============================================================
✅ FINAL STATUS: PASS — Code approved by Reviewer
   TOTAL ITERATIONS: 1
   OUTPUT FILE:      output/generated_20260407_173520.py
============================================================
```

When the Reviewer flags issues, the Coder incorporates the feedback and tries again — up to `MAX_ITERATIONS` times. Each iteration sees the full feedback history, not just the most recent critique.

---

## Known Limitations

This system uses **LLM-as-Judge** for code review, which works well for catching obvious logic errors but is fundamentally less reliable than deterministic validation. In testing, the Reviewer occasionally approves code with subtle issues — for example, missing imports for type hints referenced in function signatures, or edge cases the spec called out but the Coder handled implicitly rather than explicitly.

This is a known tradeoff of LLM-as-Judge architectures, especially when running on local 7B-class models. In a production setting, this layer would be augmented with deterministic checks: a linter pass (`pyflakes`, `ruff`), a type checker (`mypy`), and ideally execution of generated unit tests in a sandboxed environment. The LLM judge catches *semantic* gaps; the deterministic layer catches *syntactic* and *structural* ones. Together, they're stronger than either alone.

The architecture supports adding these layers without changing the agent code — they would simply become additional nodes in the graph, with their own conditional edges feeding into the existing feedback loop.

---

## Project Status

- [x] Phase 1 — Planner Agent
- [x] Phase 2 — Coder Agent
- [x] Phase 3 — Reviewer Agent with structured verdict parsing
- [x] Phase 4 — LangGraph orchestration with feedback loop
- [x] Phase 5 — CLI, live logging, file output, failure mode handling

---

## License

MIT