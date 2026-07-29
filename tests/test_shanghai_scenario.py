"""End to end: the article's opening scene as an executable fixture.

Delegate in New York, fly to Shanghai, watch the gate hold at every stage —
and leave schema-valid evidence behind.
"""
from datetime import timedelta

from oscal_presence_gate.evidence_emitter import emit
from oscal_presence_gate.graph import run_sequential
from oscal_presence_gate.models import ALLOW, DENY, SOURCE_GPS, PresenceAssertion, utcnow
from oscal_presence_gate.validation import validate_file

INTENT = "Summarize the payment disputes for our top US retail clients this quarter."
PRINCIPAL = "analyst@bank"


def test_shanghai_scenario_end_to_end(tmp_path):
    now = utcnow()
    evidence = tmp_path / "assessment-results.json"

    # t0 — fresh GPS attestation in New York: covered data flows
    ny = PresenceAssertion(PRINCIPAL, "US", SOURCE_GPS, issued_at=now - timedelta(minutes=5))
    d1, out1, msg1 = run_sequential(INTENT, PRINCIPAL, assertion=ny, now=now)
    assert d1.effect == ALLOW and out1 and "[COVERED DATA]" in out1

    # t+26h — the agent still holds the delegation; the attestation is long
    # stale. the agent's datacenter IP buys nothing: no fresh presence, no data
    stale = PresenceAssertion(PRINCIPAL, "US", SOURCE_GPS, issued_at=now - timedelta(hours=26))
    d2, out2, msg2 = run_sequential(INTENT, PRINCIPAL, assertion=stale, now=now)
    assert d2.effect == DENY and out2 is None
    assert "stale" in d2.reason

    # re-attestation from the Shanghai hotel — fresh signal, blocked country
    cn = PresenceAssertion(PRINCIPAL, "CN", SOURCE_GPS, issued_at=now - timedelta(minutes=2))
    d3, out3, msg3 = run_sequential(INTENT, PRINCIPAL, assertion=cn, now=now)
    assert d3.effect == DENY and "CN" in d3.reason

    # custody chain must tell the three requests apart
    assert len({d1.correlation_id, d2.correlation_id, d3.correlation_id}) == 3

    # denials explain themselves — a silent 403 just breeds exemption tickets
    assert "Location-aware access control" in msg2 and "correlation" in msg3

    # evidence out, and it validates against the official NIST schema
    emit([d1, d2, d3], out_path=evidence)
    assert validate_file(evidence) == []
