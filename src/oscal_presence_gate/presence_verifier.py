"""Presence verifier — the one new node on the guardrails chassis.

Answers the question the rest of the identity stack can't: where is the human
this request is FOR, right now? Everything degrades to 'unknown' — and unknown
fails closed downstream. PRES-1.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from .models import PresenceAssertion, PresenceResult, utcnow
from .policy_loader import PolicyParams

VERIFIED = "verified"
UNKNOWN = "unknown"


def verify(
    assertion: Optional[PresenceAssertion],
    params: PolicyParams,
    now: Optional[datetime] = None,
) -> PresenceResult:
    now = now or utcnow()

    if assertion is None:
        return PresenceResult(UNKNOWN, reasons=["no presence assertion in delegation chain"])

    if not assertion.integrity_ok:
        # jailbreak / mock-location caught at issuance — the assertion is noise
        return PresenceResult(
            UNKNOWN, reasons=["device-integrity check failed at issuance (jailbreak/mock-location)"]
        )

    if assertion.signature is None or assertion.signature == "":
        return PresenceResult(UNKNOWN, reasons=["unsigned presence assertion"])

    if not assertion.is_fresh(now=now, policy_max_age_s=params.attestation_max_age_s):
        return PresenceResult(
            UNKNOWN,
            reasons=[
                f"assertion stale: age {int(assertion.age_s(now))}s exceeds "
                f"policy window {params.attestation_max_age_s}s"
            ],
        )

    country = (assertion.country or "").strip().upper()
    if not country:
        return PresenceResult(UNKNOWN, reasons=["assertion carries no country"])

    return PresenceResult(VERIFIED, country=country, reasons=[f"fresh {assertion.source} assertion"])
