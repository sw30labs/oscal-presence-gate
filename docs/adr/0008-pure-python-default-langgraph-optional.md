# ADR-0008: Pure-Python sequential runtime by default; LangGraph as an optional extra; deterministic keyword planner

## Status

Accepted (retrospective, inferred 2026-11-13)

## Context

The demo and tests should run with zero API keys and minimal dependencies, while staying shaped like the LangGraph chassis of the sibling repos.

## Decision

`graph.run_sequential()` is the pure-Python runtime used by tests, the CLI demo, and (per its docstring) CI. `graph.build_langgraph()` compiles the same nodes as a `StateGraph` and needs the `[graph]` extra (`langgraph>=0.2.0`), raising a clear error otherwise. The planner is deterministic keyword routing (`dispute`, `customer`, `payment`, `account`, `client`, `chargeback` → covered-data tool; anything else → public report), described as swappable for an LLM planner.

## Consequences

### Positive

- Core dependencies are only `jsonschema` and `regex`.
- Tests are deterministic and offline.

### Negative

- The LangGraph path has no test and its presence node does not accept an injectable `now`, so parity between the two runtimes is unverified (A-006).
- Keyword routing is a demo stand-in, not a real planner.

## Alternatives considered

- LangGraph as a hard dependency (not chosen; README lists it as an optional extra).
- An LLM planner by default (rejected for the demo: "zero API keys").

## Evidence

- src/oscal_presence_gate/graph.py
- src/oscal_presence_gate/planner.py
- pyproject.toml (dependencies, optional-dependencies)
- QUICKSTART.md
- commit 6d4c5cb
