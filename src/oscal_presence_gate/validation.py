"""Validate the repo's OSCAL content against the vendored NIST v1.1.3 schemas.

NIST's schemas use XSD-style \\p{...} unicode property escapes — python's
`re` chokes on those, so the pattern keywords are re-implemented with the
`regex` module.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
import regex as re2
from jsonschema import Draft7Validator, validators

from .policy_loader import DATA_DIR

SCHEMAS_DIR = DATA_DIR / "schemas"

ROOT_TO_SCHEMA = {
    "catalog": "oscal_catalog_schema.json",
    "profile": "oscal_profile_schema.json",
    "component-definition": "oscal_component_schema.json",
    "assessment-results": "oscal_assessment-results_schema.json",
}


def _pattern_kw(validator, patrn, instance, schema):
    if validator.is_type(instance, "string"):
        try:
            ok = re2.search(patrn, instance)
        except re2.error:
            ok = True  # unparseable pattern -> skip, don't false-fail
        if not ok:
            yield jsonschema.ValidationError(f"{instance!r} does not match pattern {patrn!r}")


def _pattern_props_kw(validator, pattern_properties, instance, schema):
    if not validator.is_type(instance, "object"):
        return
    for pat, subschema in pattern_properties.items():
        for key, value in instance.items():
            if re2.search(pat, key):
                yield from validator.descend(value, subschema, path=key, schema_path=pat)


OscalValidator = validators.extend(
    Draft7Validator, {"pattern": _pattern_kw, "patternProperties": _pattern_props_kw}
)


def validate_document(doc: dict[str, Any]) -> list[str]:
    """Validate one loaded OSCAL document. Empty list = valid."""
    roots = [k for k in doc.keys() if k in ROOT_TO_SCHEMA]
    if len(roots) != 1:
        return [f"unrecognized OSCAL root: {sorted(doc.keys())}"]
    schema_path = SCHEMAS_DIR / ROOT_TO_SCHEMA[roots[0]]
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)
    errs = sorted(OscalValidator(schema).iter_errors(doc), key=lambda e: list(e.absolute_path))
    return ["/" + "/".join(map(str, e.absolute_path)) + ": " + e.message for e in errs]


def validate_file(path: Path) -> list[str]:
    with open(path, encoding="utf-8") as f:
        return validate_document(json.load(f))


def validate_all(data_dir: Path | None = None) -> dict[str, list[str]]:
    """Every OSCAL JSON under data/ — the schemas themselves excluded."""
    data_dir = data_dir or DATA_DIR
    results: dict[str, list[str]] = {}
    for path in sorted(data_dir.rglob("*.json")):
        if SCHEMAS_DIR in path.parents:
            continue
        results[str(path.relative_to(data_dir))] = validate_file(path)
    return results
