# ADR-0010: Every denial explains itself with reason, controls, correlation ID and a recovery path

## Status

Accepted (retrospective, inferred 2026-11-13)

## Context

The responder docstring states the rationale directly: users who understand why they were denied file fewer exemption tickets; the Shanghai test comment says "a silent 403 just breeds exemption tickets".

## Decision

`responder.respond()` returns tool output plus an allow note on allow; on any other effect it returns a message naming location-aware access control, the effect and reason, the short correlation ID, the control IDs, and two recovery paths: re-attest in the authenticator or use break-glass (which pages security).

## Consequences

### Positive

- Denials are actionable and traceable to the evidence record.

### Negative

- Denial text reveals the policy reason (e.g. the blocked country) to the end user; acceptable for this PoC, not reviewed as a disclosure question.

## Alternatives considered

- Generic 403 (rejected by the docstring rationale).

## Evidence

- src/oscal_presence_gate/responder.py
- tests/test_shanghai_scenario.py
- commit 6d4c5cb
