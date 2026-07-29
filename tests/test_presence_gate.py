"""Units: params come from OSCAL, verifier edge cases, the enforcer decision
table, and schema-valid evidence out."""
from datetime import timedelta

import pytest

from oscal_presence_gate.evidence_emitter import build_assessment_results
from oscal_presence_gate.models import (
    ALLOW,
    AUTONOMOUS,
    DENY,
    SOURCE_GPS,
    PresenceAssertion,
    ProposedCall,
    utcnow,
)
from oscal_presence_gate.planner import plan
from oscal_presence_gate.policy_enforcer import decide
from oscal_presence_gate.policy_loader import load_params, parse_iso8601_duration_s
from oscal_presence_gate.presence_verifier import UNKNOWN, VERIFIED, verify
from oscal_presence_gate.tools import default_registry
from oscal_presence_gate.validation import validate_document


@pytest.fixture(scope="module")
def params():
    return load_params()


@pytest.fixture()
def registry():
    return default_registry()


def fresh(country="US", minutes=5, **kw):
    return PresenceAssertion(
        "analyst@bank", country, SOURCE_GPS, issued_at=utcnow() - timedelta(minutes=minutes), **kw
    )


# ---- params live in the OSCAL files, not in code ------------------------------

def test_params_loaded_from_oscal(params):
    # HK/MO must be here — 202.208 folds both into "China", geoip does not
    assert {"CN", "HK", "MO", "RU", "IR", "KP", "CU", "VE"} <= params.blocked_countries
    assert params.attestation_max_age_s == 3600  # PT1H via profile
    assert params.delegation_max_ttl_s == 8 * 3600  # PT8H
    assert params.policy_version


def test_duration_parser():
    assert parse_iso8601_duration_s("PT1H") == 3600
    assert parse_iso8601_duration_s("PT90M") == 5400
    assert parse_iso8601_duration_s("P12M") == 12 * 30 * 86400
    with pytest.raises(ValueError):
        parse_iso8601_duration_s("banana")


# ---- verifier: everything degrades to unknown ---------------------------------

def test_verifier_fresh(params):
    r = verify(fresh(), params)
    assert r.status == VERIFIED and r.country == "US"


def test_verifier_absent(params):
    assert verify(None, params).status == UNKNOWN


def test_verifier_stale(params):
    r = verify(fresh(minutes=90), params)  # policy window is 60 min
    assert r.status == UNKNOWN and "stale" in r.reasons[0]


def test_verifier_integrity_failure(params):
    assert verify(fresh(integrity_ok=False), params).status == UNKNOWN


def test_verifier_unsigned(params):
    assert verify(fresh(signature=""), params).status == UNKNOWN


# ---- enforcer: the decision table from the article ----------------------------

def _decide_for(params, registry, assertion, classification="human-delegated",
                tool="read_covered_customer_data"):
    call = ProposedCall(tool, {}, "analyst@bank", classification=classification, assertion=assertion)
    return decide(call, verify(assertion, params), params, registry)


def test_allow_fresh_allowed_country(params, registry):
    d = _decide_for(params, registry, fresh("US"))
    assert d.effect == ALLOW and "pres-1" in d.control_ids


def test_deny_blocked_country(params, registry):
    d = _decide_for(params, registry, fresh("CN"))
    assert d.effect == DENY and "pres-2" in d.control_ids and "csr-1.5" in d.control_ids


def test_deny_hong_kong_is_china(params, registry):
    assert _decide_for(params, registry, fresh("HK")).effect == DENY


def test_deny_unknown_presence_fails_closed(params, registry):
    d = _decide_for(params, registry, None)
    assert d.effect == DENY and "pres-1" in d.control_ids


def test_uncovered_tool_skips_gate(params, registry):
    d = _decide_for(params, registry, None, tool="read_public_report")
    assert d.effect == ALLOW and d.control_ids == []


def test_unknown_tool_denied(params, registry):
    d = _decide_for(params, registry, fresh(), tool="drop_all_tables")
    assert d.effect == DENY


def test_autonomous_allowed_under_entitlements(params, registry):
    d = _decide_for(params, registry, None, classification=AUTONOMOUS)
    assert d.effect == ALLOW and "pres-4" in d.control_ids


def test_planner_routes_covered_intents():
    call = plan("summarize payment disputes", "analyst@bank")
    assert call.tool_name == "read_covered_customer_data"
    assert plan("weather tomorrow", "analyst@bank").tool_name == "read_public_report"


# ---- evidence: assessment-results that actually validate ----------------------

def test_evidence_validates_against_official_schema(params, registry):
    decisions = [
        _decide_for(params, registry, fresh("US")),
        _decide_for(params, registry, fresh("CN")),
        _decide_for(params, registry, None),
    ]
    doc = build_assessment_results(decisions)
    errors = validate_document(doc)
    assert errors == [], f"assessment-results failed official schema: {errors[:3]}"
    obs = doc["assessment-results"]["results"][0]["observations"]
    assert len(obs) == 3
    assert all("correlation_id" in o["relevant-evidence"][0]["description"] for o in obs)


def test_repo_oscal_content_is_schema_valid():
    from oscal_presence_gate.validation import validate_all

    results = validate_all()
    bad = {k: v for k, v in results.items() if v}
    assert not bad, f"invalid OSCAL content: {bad}"
    assert len(results) >= 4  # 2 catalogs + component-definition + profile
