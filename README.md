[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![tests](https://img.shields.io/badge/tests-18%20passing-2ce6c8?style=flat-square)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-optional%20extra-green.svg)](https://langchain-ai.github.io/langgraph/)
[![NIST OSCAL](https://img.shields.io/badge/policy-NIST%20OSCAL%201.1.3-8b5cf6.svg)](https://pages.nist.gov/OSCAL/)
[![OSCAL JSON Reference](https://img.shields.io/badge/Reference-OSCAL%20JSON-9c27b0.svg)](https://pages.nist.gov/OSCAL-Reference/models/v1.1.3/)

# oscal-presence-gate

> **Author:** [Nic Cravino](https://github.com/sw30labs)
> **License:** Apache 2.0
> **Created:** July 2026
> **Series:** From Article to Artefacts, Vol 3 — companion code for *"OAuth Can Prove Who Your Agent Works For. It Can't Prove Where That Person Is Standing."*

**OSCAL as the policy brain for WHERE, not just WHAT.**

[`oscal-skills-guardrails`](https://github.com/sw30labs/oscal-skills-guardrails) gates **what** an agent may load. This repo gates **where** the human it serves is standing. Same loop both times: policy in (OSCAL), evidence out (OSCAL `assessment-results`), nothing un-vetted in between.

## The problem, in one scene

An analyst delegates a task to her firm's AI assistant from New York. Days later she opens the same conversation from a Shanghai hotel. The agent — running in a US datacenter, holding her still-valid delegated token — calls the customer-data API. The API sees a Virginia IP and a legitimate user token. **Allow.** Payment histories for thousands of US customers render on hotel Wi-Fi in a country of concern.

Under the DOJ Data Security Program ([28 CFR Part 202](https://www.ecfr.gov/current/title-28/chapter-I/part-202)), "access" includes the ability to *view* — and the [CISA Security Requirements](https://www.federalregister.gov/documents/2025/01/08/2024-31479/notice-of-availability-of-security-requirements-for-restricted-transactions-under-executive-order) demand that firms *"implement logical and physical access controls to prevent covered persons or countries of concern from gaining access to covered data."* OAuth delegation propagates **identity** through every hop (`act`, RFC 8693). Nothing propagates **presence**. This repo is a working answer to that gap.

## What it does (v0.2)

- Loads its runtime policy — blocked countries, attestation window, delegation TTL — **from OSCAL files**, not code. Changing the country list is an OSCAL edit.
- Runs a **presence verifier** ahead of the policy enforcer: stale, absent, unsigned, or integrity-failed assertions all collapse to *unknown*, and unknown **fails closed** for covered data.
- Enforces the decision table below and **emits every decision as an OSCAL `assessment-results` observation** with the full custody record embedded — anti-phantom-control by construction.
- Validates *all* of its own OSCAL content (and its generated evidence) against the **official NIST v1.1.3 schemas**, vendored in-repo, in CI and via `opg validate`.

## Architecture

```
User Intent → Planner → Presence Verifier → Policy Enforcer → (maybe) Tool → Responder
                             │                     │
                   presence assertion        OSCAL profile
                   (age, source, country)    (PRES + CSR controls)
                             └─────────┬───────────┘
                               Evidence Emitter
                        (decision → assessment-results)
```

Same chassis as [`oscal-agent-guardrails`](https://github.com/ai-agents-cybersecurity/oscal-agent-guardrails), plus one node. The tool is never invoked unless explicitly allowed.

## The decision table

| # | Condition | Effect | Controls |
|---|---|---|---|
| 1 | Unknown tool | deny | whitelist default (csr-1.3) |
| 2 | Tool doesn't reach covered data | allow | ordinary entitlements |
| 3 | Autonomous pipeline (no human rendering) | allow, flagged | pres-4 |
| 4 | Presence unknown (stale / absent / unsigned / integrity-failed) | **deny, fail closed** | pres-1, csr-1.5 |
| 5 | Principal attested in blocked country (CN **incl. HK/MO**, RU, IR, KP, CU, VE) | deny | pres-2, csr-1.5 |
| 6 | Fresh attestation, allowed country | allow | pres-1, pres-2 |

## Quickstart

```bash
pip install -e ".[test]"
pytest                    # 18 tests, incl. the Shanghai scenario end-to-end
opg demo                  # run the fly-with-a-token timeline, emit evidence
opg validate              # every OSCAL file + generated evidence vs NIST schemas
pip install -e ".[graph]" # optional: the same pipeline as a LangGraph StateGraph
```

## The OSCAL content (the novel part)

| File | What it is |
|---|---|
| `data/dsp-cisa-security-requirements-catalog.json` | **Unofficial** OSCAL encoding of the CISA Security Requirements for Restricted Transactions — to my knowledge the first public one. Complete Sections I and II (20 controls, incl. the I.A organizational items, I.C risk assessment, and II.D); every statement is verbatim against the source document, verified against the **rendered page images** of the OCR'd PDF (the embedded text layer contains recognition errors — the printed page wins; conventions documented in the catalog remarks). Draft SP 800-53 rev 5 mappings as props. |
| `data/presence-propagation-overlay-catalog.json` | Five **PRES** controls: presence as an attested claim in the delegation chain, enforcement at initiation *and* delivery, bounded delegation lifetimes, principal-based traffic classification, delegation-chain custody logging. Parameterized (blocked countries, PT1H attestation window, PT8H delegation TTL, P12M retention). |
| `data/profiles/restricted-transaction-baseline.json` | Profile importing both catalogs and pinning the runtime parameters the enforcer consumes. |
| `data/presence-gate-component-definition.json` | Reference components: presence-attestation-service, location-gate-middleware (FastAPI-targeted), delivery-surface-gate. |
| `data/schemas/` | Vendored official NIST OSCAL v1.1.3 JSON schemas so validation runs offline. |

## Sibling repos

| Repo | Gates | Shared pattern |
|---|---|---|
| [oscal-skills-guardrails](https://github.com/sw30labs/oscal-skills-guardrails) | **what** skills an agent may load | policy in, evidence out |
| [oscal-agent-guardrails](https://github.com/ai-agents-cybersecurity/oscal-agent-guardrails) | **which tools** an agent may call | planner → enforcer → responder |
| **oscal-presence-gate** (this repo) | **where** the principal is standing | both of the above |
| [oscal-agent-lab](https://github.com/ai-agents-cybersecurity/oscal-agent-lab) / [oscal-cac-playgd](https://github.com/ai-agents-cybersecurity/oscal-cac-playgd) / [oscal-digital-twin-playground](https://github.com/ai-agents-cybersecurity/oscal-digital-twin-playground) | exploration substrate | catalogs, CaC CLI, what-if twins |

## Roadmap

**v0.3** — JWS-signed presence assertions (replace the signature stub); minimal assessment plan (retire the `import-ap` placeholder); derive tool `covered_data` flags from the component-definition so OSCAL is the single source of truth; per-decision `finding` entries linking observations to control ids. **v0.4** — digital-twin what-if (chains `oscal-digital-twin-playground`): replay logged traffic against a candidate country-list or window change *before* enforcing it; delivery-surface gate demo (the render-time check).

**House standard:** OSCAL **1.1.3** across all sw30labs repos. An upgrade kit for `oscal-skills-guardrails` (version bump + a schema-strict profile variant that takes its official-schema errors from 87 to 0) ships alongside this repo.

## Honest limitations

The CISA catalog is **unofficial** and says so in its metadata; statement prose was verified verbatim against the [source document](https://www.cisa.gov/resources-tools/resources/EO-14117-security-requirements)'s rendered pages, with the encoding conventions (framework citations and footnote markers dropped from statements, whitespace normalized, printed-page precedence over the OCR text layer) documented in the catalog remarks. The SP 800-53 mappings are informed drafts, not authoritative. The presence assertion is integrity-stubbed pending v0.3 signing. And none of this is legal advice — it is a working argument that location compliance for agent traffic can be *policy in, evidence out* instead of prose in, hope out.
