"""Data models. Identity tells you who — presence tells you where.

These carry both through the pipeline so no hop has to guess.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

# PRES-4: classify by principal reachability, not grant type
HUMAN_DELEGATED = "human-delegated"
AUTONOMOUS = "autonomous"

# presence sources — gps outranks network evidence, see the catalog
SOURCE_GPS = "gps-attestation"
SOURCE_NETWORK = "network-verified"

ALLOW = "allow"
DENY = "deny"
NEEDS_APPROVAL = "needs_approval"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class PresenceAssertion:
    """Short-lived, attested claim about where the human principal is (PRES-1).

    Production version is a signed claim (JWS) from the attestation service —
    signature here is a stub until v0.3.
    """

    principal: str
    country: str  # ISO 3166-1 alpha-2, as the attestation source reports it
    source: str  # SOURCE_GPS or SOURCE_NETWORK
    issued_at: datetime
    max_age_s: int = 3600
    integrity_ok: bool = True  # device-integrity result at issuance
    signature: str = "stub"  # TODO(nic): real JWS in v0.3 — unsigned already fails closed

    def age_s(self, now: Optional[datetime] = None) -> float:
        now = now or utcnow()
        return (now - self.issued_at).total_seconds()

    def is_fresh(self, now: Optional[datetime] = None, policy_max_age_s: Optional[int] = None) -> bool:
        # stricter of the assertion's own window and the policy window
        limit = min(self.max_age_s, policy_max_age_s) if policy_max_age_s else self.max_age_s
        return self.age_s(now) <= limit


@dataclass
class PresenceResult:
    """Verifier outcome — 'verified' or 'unknown', nothing in between.

    Stale, absent, tampered all collapse to unknown; unknown fails closed
    for covered data.
    """

    status: str
    country: Optional[str] = None
    reasons: list[str] = field(default_factory=list)


@dataclass
class ProposedCall:
    """What the planner wants to do — before the gate has said anything."""

    tool_name: str
    args: dict[str, Any]
    principal: str
    classification: str = HUMAN_DELEGATED
    assertion: Optional[PresenceAssertion] = None
    correlation_id: str = field(default_factory=lambda: uuid.uuid4().hex)


@dataclass
class Decision:
    """The gate's answer, with enough to reconstruct it later (PRES-5).

    Assessors ask for this. So does opposing counsel.
    """

    effect: str  # ALLOW / DENY / NEEDS_APPROVAL
    reason: str
    control_ids: list[str]
    principal: str
    tool_name: str
    presence_status: str
    country: Optional[str]
    policy_version: str
    correlation_id: str
    timestamp: datetime = field(default_factory=utcnow)

    def to_record(self) -> dict[str, Any]:
        return {
            "decision": self.effect,
            "reason": self.reason,
            "control_ids": list(self.control_ids),
            "principal": self.principal,
            "tool": self.tool_name,
            "presence_status": self.presence_status,
            "country": self.country,
            "policy_version": self.policy_version,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(timespec="seconds"),
        }
