# ADR-0011: Apache-2.0 hatchling package for Python 3.10+, `opg` CLI, data read from the repo tree

## Status

Accepted (retrospective, inferred 2026-11-13)

## Context

The repo is companion code for the article series "From Article to Artefacts, Vol 3" and is meant to be cloned and run (`pip install -e`).

## Decision

`pyproject.toml` builds with hatchling, packages only `src/oscal_presence_gate`, requires Python ≥3.10, declares Apache-2.0 (matching LICENSE and README), and exposes `opg` with `demo` and `validate` subcommands. Data is located at runtime via `Path(__file__).resolve().parents[2] / "data"`, i.e. the repository root.

## Consequences

### Positive

- License is consistent across LICENSE, README and pyproject.
- Single-command demo and validation.

### Negative

- The wheel does not include `data/`, so a non-editable install cannot find its policy or schemas (A-007).
- Package version is `0.2.0.dev0` while the commit message says v0.2.1 (A-011).

## Alternatives considered

- Shipping data as package data (not done).

## Evidence

- pyproject.toml
- LICENSE
- src/oscal_presence_gate/policy_loader.py (REPO_ROOT, DATA_DIR)
- src/oscal_presence_gate/cli.py
- src/oscal_presence_gate/__init__.py (__version__)
- commit 6d4c5cb
