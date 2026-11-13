# Architecture Decision Records — sw30labs/oscal-presence-gate

Retrospective ADRs for **oscal-presence-gate**: presence-aware OSCAL guardrails for delegated AI-agent traffic (EO 14117 / DOJ Data Security Program), companion code for *From Article to Artefacts, Vol 3*. Reviewed at `6d4c5cb` (the only commit on `main`).

Format: Title; Status; Context; Decision; Consequences (positive/negative); Alternatives considered; Evidence (file paths, commit SHAs). All records here were written retrospectively on 2026-11-13 from a full read of the repository at the reviewed commit. Where the *why* is inferred rather than stated in the code, docs, or commit messages, the ADR says so and the inference is logged in [`../assumptions.md`](../assumptions.md).

| ADR | Title | Status |
|---|---|---|
| [0001](0001-oscal-files-as-runtime-policy-source.md) | OSCAL files are the runtime policy source, with profile set-parameters overriding the overlay | Accepted (retrospective) |
| [0002](0002-presence-verifier-node-on-guardrails-chassis.md) | Add a presence-verifier node to the oscal-agent-guardrails chassis; the tool runs only on explicit allow | Accepted (retrospective) |
| [0003](0003-fail-closed-unknown-presence.md) | Collapse every non-verified presence state to 'unknown' and fail closed for covered data | Accepted (retrospective) |
| [0004](0004-ordered-decision-table.md) | Encode the gate as an ordered six-rule decision table | Accepted (retrospective) |
| [0005](0005-blocked-countries-include-hk-mo.md) | Treat Hong Kong and Macau as China in the blocked-country parameter | Accepted (retrospective) |
| [0006](0006-evidence-as-oscal-assessment-results.md) | Emit every decision as an OSCAL assessment-results observation with the raw decision record embedded | Accepted (retrospective) |
| [0007](0007-vendored-nist-schemas-offline-validation.md) | Vendor the official NIST OSCAL 1.1.3 schemas and validate offline with a regex-module pattern override | Accepted (retrospective) |
| [0008](0008-pure-python-default-langgraph-optional.md) | Pure-Python sequential runtime by default; LangGraph as an optional extra; deterministic keyword planner | Accepted (retrospective) |
| [0009](0009-unofficial-cisa-catalog-and-pres-overlay.md) | Ship an unofficial verbatim OSCAL encoding of the CISA Security Requirements plus an original PRES overlay and reference components | Accepted (retrospective) |
| [0010](0010-explanatory-denials.md) | Every denial explains itself with reason, controls, correlation ID and a recovery path | Accepted (retrospective) |
| [0011](0011-packaging-license-cli.md) | Apache-2.0 hatchling package for Python 3.10+, `opg` CLI, data read from the repo tree | Accepted (retrospective) |
