# ADR-0009: Ship an unofficial verbatim OSCAL encoding of the CISA Security Requirements plus an original PRES overlay and reference components

## Status

Accepted (retrospective, inferred 2026-11-13)

## Context

docs/BRIEF.md records (checked 2026-07-28) that no public OSCAL encoding of the CISA Security Requirements for Restricted Transactions existed. The project needed both the regulatory baseline and the article's proposed engineering controls in assessable form.

## Decision

`data/dsp-cisa-security-requirements-catalog.json` (catalog version 0.2.1) encodes Sections I and II as 20 controls (csr-1.1 … csr-1.6 with sub-controls csr-1.4.1–1.4.6 and csr-1.5.1–1.5.3, csr-2.1 … csr-2.5), each tagged `provenance: verbatim`, with encoding conventions in metadata remarks (printed page wins over the OCR text layer; citations and footnote markers dropped; whitespace normalized) and draft SP 800-53 mappings as props. It is labelled UNOFFICIAL and not endorsed by CISA/DOJ/NIST. `data/presence-propagation-overlay-catalog.json` holds five original PRES controls (pres-1 … pres-5) and the runtime parameters. `data/presence-gate-component-definition.json` defines three reference components (presence-attestation-service, location-gate-middleware, delivery-surface-gate).

## Consequences

### Positive

- A first-mover, machine-readable baseline that the gate's decisions cite by control ID.
- Clear separation between regulatory text (CSR) and proposed controls (PRES).

### Negative

- SP 800-53 mappings are informed drafts, not authoritative (README).
- Only location-gate-middleware behaviour is implemented; the attestation service and delivery-surface gate exist only as definitions (A-004).

## Alternatives considered

- Summarising rather than quoting the source (the brief's v0 had `summary` provenance on some controls; the shipped catalog upgraded all to verbatim).

## Evidence

- data/dsp-cisa-security-requirements-catalog.json (metadata remarks, groups)
- data/presence-propagation-overlay-catalog.json
- data/presence-gate-component-definition.json
- docs/BRIEF.md ("Why this doesn't exist yet", "Honest TODOs")
- README.md ("The OSCAL content", "Honest limitations")
- commit 6d4c5cb
