# ADR-0003: Collapse every non-verified presence state to 'unknown' and fail closed for covered data

## Status

Accepted (retrospective, inferred 2026-11-13)

## Context

Presence can be absent, stale, unsigned, integrity-failed (jailbreak / mock location), or missing a country. The CISA keystone requirement (csr-1.5) asks firms to *prevent* country-of-concern access, which argues for denying when location cannot be established.

## Decision

`presence_verifier.verify()` returns exactly two statuses, `verified` or `unknown`, checking in order: assertion present, `integrity_ok`, non-empty signature, freshness (the stricter of the assertion's own `max_age_s` and the policy window), non-empty country. The enforcer denies covered-data calls when presence is not `verified`, citing `pres-1` and `csr-1.5`.

## Consequences

### Positive

- No partial-trust states to reason about; every failure mode has the same outcome.
- Stale delegations (the 26-hour Shanghai case) are denied even with a valid token.
- Each `unknown` carries human-readable reasons for the audit trail.

### Negative

- Signature verification is a stub: any non-empty signature (the default is the string `"stub"`) passes, so "unsigned fails closed" holds only for an empty/None signature (A-001).
- Fail-closed raises the chance of legitimate denials; the design relies on the responder's re-attest / break-glass guidance to manage that.

## Alternatives considered

- A `needs_approval` path for unknown presence (mentioned in docs/BRIEF.md; the constant exists in models.py but is never returned — A-003).
- Trusting network-verified location alone (not chosen; GPS outranks network evidence per the models.py comment).

## Evidence

- src/oscal_presence_gate/presence_verifier.py
- src/oscal_presence_gate/models.py (PresenceAssertion.is_fresh, PresenceResult)
- src/oscal_presence_gate/policy_enforcer.py (rule 4)
- tests/test_presence_gate.py (verifier tests)
- tests/test_shanghai_scenario.py
- commit 6d4c5cb
