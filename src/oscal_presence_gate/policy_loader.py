"""Load OSCAL content, distill runtime params.

The OSCAL files are the source of truth. Changing the blocked-country list or
the attestation window is an OSCAL edit — never a code change.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import regex as re

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"

OVERLAY_FILE = "presence-propagation-overlay-catalog.json"
CSR_FILE = "dsp-cisa-security-requirements-catalog.json"
PROFILE_FILE = Path("profiles") / "restricted-transaction-baseline.json"

_DURATION_RE = re.compile(
    r"^P(?:(?P<years>\d+)Y)?(?:(?P<months>\d+)M)?(?:(?P<days>\d+)D)?"
    r"(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?)?$"
)


def parse_iso8601_duration_s(value: str) -> int:
    """ISO 8601 duration -> seconds.

    Months ≈ 30 days — only retention math uses months, never the
    attestation window.
    """
    m = _DURATION_RE.match(value.strip())
    if not m or not any(m.groupdict().values()):
        raise ValueError(f"unparseable ISO 8601 duration: {value!r}")
    g = {k: int(v) if v else 0 for k, v in m.groupdict().items()}
    return (
        g["years"] * 365 * 86400
        + g["months"] * 30 * 86400
        + g["days"] * 86400
        + g["hours"] * 3600
        + g["minutes"] * 60
        + g["seconds"]
    )


@dataclass
class PolicyParams:
    blocked_countries: frozenset[str]
    attestation_max_age_s: int
    delegation_max_ttl_s: int
    log_retention_s: int
    policy_version: str
    source_files: list[str] = field(default_factory=list)


def load_json(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _param_values(catalog: dict[str, Any], param_id: str) -> list[str]:
    for p in catalog.get("catalog", {}).get("params", []):
        if p.get("id") == param_id:
            return list(p.get("values", []))
    raise KeyError(f"parameter {param_id!r} not found in overlay catalog")


def load_params(data_dir: Optional[Path] = None, profile_overrides: bool = True) -> PolicyParams:
    """Params from the PRES overlay; the baseline profile's set-parameters win
    on top — that being the whole point of profiles."""
    data_dir = data_dir or DATA_DIR
    overlay = load_json(data_dir / OVERLAY_FILE)

    values: dict[str, list[str]] = {
        pid: _param_values(overlay, pid)
        for pid in (
            "pres_prm_blocked_countries",
            "pres_prm_attestation_max_age",
            "pres_prm_delegation_max_ttl",
            "pres_prm_log_retention",
        )
    }
    sources = [str(data_dir / OVERLAY_FILE)]

    profile_path = data_dir / PROFILE_FILE
    if profile_overrides and profile_path.exists():
        profile = load_json(profile_path)
        for sp in profile.get("profile", {}).get("modify", {}).get("set-parameters", []):
            if sp.get("param-id") in values and sp.get("values"):
                values[sp["param-id"]] = list(sp["values"])
        sources.append(str(profile_path))

    meta = overlay["catalog"]["metadata"]
    # version + catalog uuid prefix — every decision log cites this
    version = f"{meta.get('version', '0')}+{overlay['catalog']['uuid'][:8]}"

    return PolicyParams(
        blocked_countries=frozenset(v.upper() for v in values["pres_prm_blocked_countries"]),
        attestation_max_age_s=parse_iso8601_duration_s(values["pres_prm_attestation_max_age"][0]),
        delegation_max_ttl_s=parse_iso8601_duration_s(values["pres_prm_delegation_max_ttl"][0]),
        log_retention_s=parse_iso8601_duration_s(values["pres_prm_log_retention"][0]),
        policy_version=version,
        source_files=sources,
    )
