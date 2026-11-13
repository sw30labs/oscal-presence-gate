# ADR-0006: Emit every decision as an OSCAL assessment-results observation with the raw decision record embedded

## Status

Accepted (retrospective, inferred 2026-11-13)

## Context

docs/BRIEF.md (Layer 3) describes the "anti-phantom-control" move: instead of compliance prose that may describe nothing, the control emits machine-readable evidence of itself operating. PRES-5 asks for delegation-chain custody logging.

## Decision

`evidence_emitter.build_assessment_results()` builds one OSCAL 1.1.3 `assessment-results` document per batch: one result, one observation per decision (method `TEST`), each embedding `Decision.to_record()` (decision, reason, control IDs, principal, tool, presence status, country, policy version, correlation ID, timestamp) as JSON in `relevant-evidence`. `reviewed-controls` lists only the controls the batch actually exercised (or include-all when none). `import-ap` points at a placeholder assessment plan until v0.3.

## Consequences

### Positive

- Evidence validates against the official schema (tested).
- Each request is distinguishable by correlation ID (tested in the Shanghai scenario).
- Output can sit in one audit package with the oscal-skills-guardrails evidence stream (module docstring).

### Negative

- The decision record is embedded as a JSON string inside a description field, not as structured OSCAL props.
- `import-ap` references a file that does not exist (`./assessment-plan-placeholder.json`).
- No `findings` linking observations to control IDs yet (roadmap v0.3).
- Retention (P12M) is only described in remarks; nothing enforces it.

## Alternatives considered

- Plain JSONL decision logs (not chosen; the brief wants OSCAL-native evidence).
- Per-decision `finding` entries (deferred to v0.3 per README roadmap).

## Evidence

- src/oscal_presence_gate/evidence_emitter.py
- src/oscal_presence_gate/models.py (Decision.to_record)
- docs/BRIEF.md (Layer 3)
- tests/test_presence_gate.py::test_evidence_validates_against_official_schema
- tests/test_shanghai_scenario.py
- commit 6d4c5cb
