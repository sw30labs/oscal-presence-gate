# ADR-0007: Vendor the official NIST OSCAL 1.1.3 schemas and validate offline with a regex-module pattern override

## Status

Accepted (retrospective, inferred 2026-11-13)

## Context

All OSCAL content in the repo and the generated evidence must be schema-valid. README states the schemas are vendored "so validation runs offline". NIST's schemas use XSD-style `\p{...}` escapes that Python's `re` cannot compile (validation.py docstring). README also declares OSCAL 1.1.3 the house standard across sw30labs repos.

## Decision

Four official schemas (catalog, profile, component, assessment-results) are committed under `data/schemas/`. `validation.py` extends jsonschema's `Draft7Validator`, replacing the `pattern` and `patternProperties` keywords with implementations using the third-party `regex` module. `validate_all()` checks every JSON under `data/` except the schemas; `opg validate` also checks generated evidence. A test asserts the repo's own content is valid.

## Consequences

### Positive

- Validation needs no network and is deterministic.
- Content and evidence are held to the official schema, not a hand-written subset.

### Negative

- An unparseable pattern is treated as a match (`except re2.error: ok = True`), which can let invalid values through silently (A-005).
- Vendored schemas must be updated by hand on an OSCAL upgrade.
- ~310 KB of schema JSON lives in the repo.

## Alternatives considered

- Fetching schemas at runtime (rejected implicitly by the offline requirement).
- Python `re` with patterns stripped (not chosen; the docstring explains the `\p{}` problem).

## Evidence

- src/oscal_presence_gate/validation.py
- data/schemas/oscal_*_schema.json
- src/oscal_presence_gate/cli.py (validate)
- tests/test_presence_gate.py::test_repo_oscal_content_is_schema_valid
- README.md ("House standard")
- commit 6d4c5cb
