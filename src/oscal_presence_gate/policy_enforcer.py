"""Policy enforcer — the guardrails whitelist, extended with presence.

Check order IS the article's argument:
  1. unknown tool          -> deny (whitelist)
  2. not covered data      -> allow (entitlement regime, out of LAC scope)
  3. autonomous traffic    -> allow under entitlements, flagged (PRES-4)
  4. presence not verified -> deny, fail closed (PRES-1, CSR-I.B)
  5. blocked country       -> deny (PRES-2, CSR-I.B)
  6. otherwise             -> allow
"""
from __future__ import annotations

from .models import ALLOW, AUTONOMOUS, DENY, Decision, PresenceResult, ProposedCall
from .policy_loader import PolicyParams
from .presence_verifier import VERIFIED
from .tools import ToolRegistry


def decide(
    call: ProposedCall,
    presence: PresenceResult,
    params: PolicyParams,
    registry: ToolRegistry,
) -> Decision:
    common = dict(
        principal=call.principal,
        tool_name=call.tool_name,
        presence_status=presence.status,
        country=presence.country,
        policy_version=params.policy_version,
        correlation_id=call.correlation_id,
    )

    spec = registry.get(call.tool_name)
    if spec is None:
        return Decision(
            effect=DENY,
            reason="unknown tool — whitelist pattern denies by default",
            control_ids=["csr-1.3"],
            **common,
        )

    if not spec.covered_data:
        return Decision(
            effect=ALLOW,
            reason="tool does not reach covered data; governed by ordinary entitlements",
            control_ids=[],
            **common,
        )

    if call.classification == AUTONOMOUS:
        # allow, but the contract is one-sided: output must never render to a
        # human — that end is the delivery-surface-gate's problem
        return Decision(
            effect=ALLOW,
            reason=(
                "autonomous pipeline under data-subscription entitlements (PRES-4); "
                "output MUST NOT render to a human — delivery-surface-gate enforces that end"
            ),
            control_ids=["pres-4"],
            **common,
        )

    if presence.status != VERIFIED:
        return Decision(
            effect=DENY,
            reason="principal presence unknown (" + "; ".join(presence.reasons) + ") — fail closed for covered data",
            control_ids=["pres-1", "csr-1.5"],
            **common,
        )

    if presence.country in params.blocked_countries:
        return Decision(
            effect=DENY,
            reason=f"principal attested in blocked country {presence.country}",
            control_ids=["pres-2", "csr-1.5"],
            **common,
        )

    return Decision(
        effect=ALLOW,
        reason=f"fresh presence attestation in allowed country {presence.country}",
        control_ids=["pres-1", "pres-2"],
        **common,
    )
