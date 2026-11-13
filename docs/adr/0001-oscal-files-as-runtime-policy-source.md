# ADR-0001: OSCAL files are the runtime policy source, with profile set-parameters overriding the overlay

## Status

Accepted (retrospective, inferred 2026-11-13)

## Context

The gate needs a blocked-country list, an attestation freshness window, a delegation TTL and a log-retention period. The project's thesis (README "OSCAL as the policy brain for WHERE, not just WHAT") is that location compliance should be "policy in, evidence out", so these values must be editable by compliance people without a code change.

## Decision

`policy_loader.load_params()` reads the four `pres_prm_*` parameters from `data/presence-propagation-overlay-catalog.json`, then applies the `modify.set-parameters` of `data/profiles/restricted-transaction-baseline.json` on top ("the baseline profile's set-parameters win on top — that being the whole point of profiles"). ISO 8601 durations are parsed to seconds (months approximated as 30 days, used only for retention). The policy version stamped on every decision is the overlay `metadata.version` plus the first 8 characters of the catalog UUID.

## Consequences

### Positive

- Changing the country list or window is an OSCAL edit (QUICKSTART: "Change the policy without touching code").
- Every decision cites the policy version that produced it.
- The same files are schema-validated, so policy and its validity live together.

### Negative

- Only four parameters are read; tool coverage (`covered_data`) still lives in Python (`tools.py` TODO for v0.3), so OSCAL is not yet the single source of truth.
- The policy version ignores the profile's own version, so a profile-only change does not change the stamped `policy_version` (see A-010).
- `delegation_max_ttl_s` and `log_retention_s` are loaded but not enforced anywhere in v0.2 (A-002).

## Alternatives considered

- Hard-coded constants in Python (rejected by the README's stated thesis).
- A bespoke YAML/JSON config file (not stated; inferred alternative — OSCAL was chosen to align with the sibling OSCAL repos).

## Evidence

- src/oscal_presence_gate/policy_loader.py
- data/presence-propagation-overlay-catalog.json (params)
- data/profiles/restricted-transaction-baseline.json (modify.set-parameters)
- QUICKSTART.md
- tests/test_presence_gate.py::test_params_loaded_from_oscal
- commit 6d4c5cb
