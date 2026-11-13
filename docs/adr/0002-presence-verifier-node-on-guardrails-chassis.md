# ADR-0002: Add a presence-verifier node to the oscal-agent-guardrails chassis; the tool runs only on explicit allow

## Status

Accepted (retrospective, inferred 2026-11-13)

## Context

Sibling repo `oscal-agent-guardrails` already gates which tools an agent may call with a Planner → Policy Enforcer → Responder flow. OAuth delegation propagates identity but not where the human principal is (README "The problem, in one scene"). docs/BRIEF.md describes this repo as "the same pattern" extended "with one new node".

## Decision

The pipeline is Planner → Presence Verifier → Policy Enforcer → (maybe) Tool → Responder, with an evidence emitter tapping decisions. The tool is executed only when the decision effect is `allow` ("tool runs only on explicit allow — never before the gate speaks"). The planner is treated as untrusted: "the control can't depend on the planner's honesty".

## Consequences

### Positive

- Reuses a known chassis; the only new concept is presence.
- The gate is independent of whichever planner produced the call.
- Tool side effects cannot happen before a decision.

### Negative

- The gate trusts that the `PresenceAssertion` attached to the call belongs to the principal; there is no binding check between `assertion.principal` and `call.principal` (A-008).
- The verifier and enforcer are separate functions, so callers that bypass `run_sequential`/`build_langgraph` must wire both themselves.

## Alternatives considered

- Putting the presence check inside the enforcer (not chosen; the brief and docstring call it out as a separate node).
- Network/IP geolocation at the API edge (rejected in the README: the datacenter IP says nothing about where the human is).

## Evidence

- src/oscal_presence_gate/graph.py
- src/oscal_presence_gate/presence_verifier.py (module docstring)
- src/oscal_presence_gate/planner.py (docstring)
- README.md (Architecture)
- docs/BRIEF.md (Layer 2)
- commit 6d4c5cb
