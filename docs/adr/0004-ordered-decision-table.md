# ADR-0004: Encode the gate as an ordered six-rule decision table

## Status

Accepted (retrospective, inferred 2026-11-13)

## Context

The article's argument is expressed as a decision table (README "The decision table"). Order matters: an unknown tool must be denied before anything else, and traffic that never reaches covered data should not be subject to location control at all.

## Decision

`policy_enforcer.decide()` evaluates, first match wins: (1) unknown tool → deny (`csr-1.3`, whitelist default); (2) tool not reaching covered data → allow, ordinary entitlements, no controls; (3) autonomous classification → allow, flagged `pres-4`, with the contract that output must not render to a human; (4) presence not verified → deny (`pres-1`, `csr-1.5`); (5) verified country in the blocked list → deny (`pres-2`, `csr-1.5`); (6) otherwise allow (`pres-1`, `pres-2`). Classification is by principal reachability, not grant type (PRES-4).

## Consequences

### Positive

- The code reads as the policy; each rule maps to control IDs that flow into evidence.
- Unit tests cover each row.

### Negative

- Autonomous traffic is allowed without any presence check; the delivery-surface gate that must stop it rendering to a human is only a reference component, not implemented (A-004).
- Whether a call is autonomous is supplied by the caller (`classification` argument), not derived, so a mislabelled call skips rules 4–5.

## Alternatives considered

- Applying presence checks to all tools (not chosen; README limits location control to covered data).
- Classifying by OAuth grant type (explicitly rejected by PRES-4 in the overlay catalog and the models.py comment).

## Evidence

- src/oscal_presence_gate/policy_enforcer.py
- src/oscal_presence_gate/models.py (HUMAN_DELEGATED / AUTONOMOUS)
- README.md (decision table)
- data/presence-propagation-overlay-catalog.json (pres-4)
- tests/test_presence_gate.py (enforcer tests)
- commit 6d4c5cb
