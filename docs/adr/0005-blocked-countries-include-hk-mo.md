# ADR-0005: Treat Hong Kong and Macau as China in the blocked-country parameter

## Status

Accepted (retrospective, inferred 2026-11-13)

## Context

Geo-IP and many attestation sources report HK and MO as separate ISO codes. A test comment states that 28 CFR 202.208 folds both into "China".

## Decision

The `pres_prm_blocked_countries` parameter (overlay and profile) is CN, HK, MO, RU, IR, KP, CU, VE. Country codes are upper-cased before comparison. A dedicated test asserts HK is denied.

## Consequences

### Positive

- Closes an obvious bypass where a HK attestation would otherwise be allowed.

### Negative

- The list is a policy snapshot; it must be maintained by hand as the regulation changes.
- The legal reading is the author's, not legal advice (README "Honest limitations") — A-009.

## Alternatives considered

- Only CN (rejected; the test comment cites the regulation's definition).

## Evidence

- data/presence-propagation-overlay-catalog.json
- data/profiles/restricted-transaction-baseline.json
- tests/test_presence_gate.py::test_params_loaded_from_oscal and ::test_deny_hong_kong_is_china
- README.md (decision table row 5)
- commit 6d4c5cb
