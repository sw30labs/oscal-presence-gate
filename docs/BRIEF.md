[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Enabled-green.svg)](https://langchain-ai.github.io/langgraph/)
[![NIST OSCAL](https://img.shields.io/badge/Docs-NIST%20OSCAL-0a67a3.svg)](https://pages.nist.gov/OSCAL/)
[![OSCAL Content](https://img.shields.io/badge/Repo-oscal--content-ff9800.svg)](https://github.com/usnistgov/oscal-content)
[![OSCAL JSON Reference](https://img.shields.io/badge/Reference-OSCAL%20JSON-9c27b0.svg)](https://pages.nist.gov/OSCAL-Reference/models/v1.1.3/)

# oscal-presence-gate — Project Brief (v0)
> **Author:** [Nic Cravino](https://github.com/sw30labs)
> **License:** Apache 2.0 (proposed)
> **Status:** ideation brief + validated seed artifacts — not yet a repo

Use **OSCAL as the policy brain for WHERE, not just WHAT.**

`oscal-agent-guardrails` proved the pattern: an OSCAL profile encodes what an agent may *do*, and a LangGraph enforcer consults it before any tool runs. This project extends the same pattern to the question the DOJ Data Security Program just made existential for regulated firms: *where is the human this agent is working for, and where will the data land?* It is PoC #5 in the OSCAL series, and the direct companion artifact to the article "OAuth Can Prove Who Your Agent Works For. It Can't Prove Where That Person Is Standing."

## Why this doesn't exist yet (checked 2026-07-28)

Nobody has published the [CISA Security Requirements for Restricted Transactions](https://www.federalregister.gov/documents/2025/01/08/2024-31479/notice-of-availability-of-security-requirements-for-restricted-transactions-under-executive-order) (EO 14117 / [28 CFR 202.248](https://www.ecfr.gov/current/title-28/chapter-I/part-202/subpart-B/section-202.248)) as an OSCAL catalog — searches surface only legal alerts and the regulatory text itself. The compliance regime driving the biggest access-control retrofit in banking has **no machine-readable encoding**. First-mover artifact, and the DSP's first annual audits land ~October 2026, so the timing writes itself.

## What ships (three layers)

**Layer 1 — Content (the novel part).** Two catalogs plus components, already drafted and **validated against the official NIST OSCAL v1.1.3 JSON schemas**:

| File | What it is |
|---|---|
| `data/dsp-cisa-security-requirements-catalog.json` | Unofficial OSCAL encoding of the CISA Security Requirements: Section I org/system-level (inventory, logging ≥12mo, deny-by-default, governance, and the keystone — *"implement logical and physical access controls to prevent covered persons or countries of concern from gaining access to covered data"* — with MFA/AAL2-3, credential revocation, identity-attribute subcontrols) + Section II data-level (minimization, encryption, key custody outside countries of concern, PETs). Every control carries a `provenance` prop (`verbatim` / `near-verbatim` / `summary`) and draft SP 800-53 rev 5 mappings. |
| `data/presence-propagation-overlay-catalog.json` | The original contribution: five **PRES** controls turning the article's argument into assessable requirements — presence as an attested claim in the delegation chain (PRES-1), enforcement at task initiation and result delivery (PRES-2), bounded delegation/connection lifetimes (PRES-3), principal-based traffic classification instead of grant-type (PRES-4), delegation-chain custody logging (PRES-5). Parameterized OSCAL-style: blocked countries (CN/HK/MO/RU/IR/KP/CU/VE), attestation max-age (PT1H), delegation TTL (PT8H), log retention (P12M). |
| `data/presence-gate-component-definition.json` | Three reference components mapped to both catalogs: `presence-attestation-service` (issues signed short-TTL presence assertions), `location-gate-middleware` (FastAPI-targeted enforcement dependency, fail-closed, principal-based), `delivery-surface-gate` (recipient-location check at render time — where DSP "access" legally happens). |

**Layer 2 — Runtime (the guardrails pattern, extended).** LangGraph flow reusing the `oscal-agent-guardrails` chassis with one new node:

```
User Intent → Planner → Presence Verifier → Policy Enforcer → (maybe) Tool → Responder
                              │                    │
                    presence assertion      OSCAL profile
                    (age, source, country)  (PRES + CSR controls)
                              └────────┬───────────┘
                                Evidence Emitter
                          (decision log → assessment evidence)
```

The enforcer today answers "may this tool run?" The presence verifier makes it also answer "for a principal standing *where*?" — deny/needs-approval when the assertion is stale, absent, or resolves to a blocked country. Same whitelist philosophy: unknown = deny.

**Layer 3 — Evidence (the audit close-the-loop).** An emitter that batches runtime decision logs into OSCAL **assessment-results** fragments, each observation linking a real log record as evidence. This is the anti-phantom-control move from *From Article to Artefacts Vol 2* inverted: instead of agents writing compliance prose that may describe nothing, the control emits machine-readable evidence of itself operating. Continuous audit for the October 2026 cycle.

## Repo layout (following house conventions)

```
oscal-presence-gate/
├── README.md  QUICKSTART.md  LICENSE  pyproject.toml
├── data/
│   ├── dsp-cisa-security-requirements-catalog.json     ← seed drafted ✅ schema-valid
│   ├── presence-propagation-overlay-catalog.json       ← seed drafted ✅ schema-valid
│   ├── presence-gate-component-definition.json         ← seed drafted ✅ schema-valid
│   └── profiles/restricted-transaction-baseline.json   ← v0.2: imports both catalogs
├── src/oscal_presence_gate/
│   ├── graph.py  planner.py  presence_verifier.py  policy_enforcer.py
│   ├── evidence_emitter.py  policy_loader.py  models.py  cli.py
├── tests/          (incl. the fly-with-a-token scenario as a fixture)
└── map_oscal_presence_gate.html   (interactive concept map, per house style)
```

## Roadmap

`v0.1` catalogs + component-definition + profile, schema-validated in CI (done for the three seeds — CI wiring pending) → `v0.2` LangGraph runtime: presence verifier + enforcer consuming the profile; simulated attestation source → `v0.3` evidence emitter producing valid assessment-results; the Shanghai scenario as an end-to-end demo (delegate in "NY", relocate mid-task, watch the deny + evidence record) → `v0.4` digital-twin what-if (chains `oscal-digital-twin-playground`): simulate country-list changes or attestation-window tightening against replayed traffic before enforcing.

## How it chains with the existing repos

`oscal-agent-guardrails` contributes the enforcement chassis and `og:`-style namespaced props (here `pg:`/provenance props). `oscal-agent-lab` contributes catalog/profile loading against real NIST content. `oscal-cac-playgd` gets two new file types its explain/diff CLI can chew on. `oscal-digital-twin-playground` gets the v0.4 what-if scenario. The article supplies the narrative; the repo supplies the proof.

## Honest TODOs before anything ships

Verify every `provenance: summary` control against the CISA source PDF and split `csr-1.4` into discrete controls with exact wording; complete Section I coverage (vulnerability remediation timelines, network topology, and remaining items); sanity-check the SP 800-53 mappings (currently informed drafts, not authoritative); decide the disclaimer posture (the catalog is UNOFFICIAL and says so in metadata — keep it loud); pick the final name (`oscal-presence-gate` recommended; alternates: `oscal-geo-guardrails`, `oscal-lac-lab`).

## Naming note

"Presence gate" states the thesis in two words: identity tells you who; presence tells you where; the gate is what regulators now expect between the two. And the acronym-free name survives the day LAAC means something else.
