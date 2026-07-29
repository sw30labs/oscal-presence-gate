"""Responder.

Puts the reason, the correlation id, and the recovery path (re-attest, or
break-glass — which pages security) into every denial. Users who understand
why they were denied file fewer exemption tickets.
"""
from __future__ import annotations

from typing import Optional

from .models import ALLOW, Decision


def respond(decision: Decision, tool_output: Optional[str]) -> str:
    if decision.effect == ALLOW and tool_output is not None:
        return (
            f"{tool_output}\n"
            f"(presence-gate: allowed — {decision.reason}; "
            f"correlation {decision.correlation_id[:8]}, policy {decision.policy_version})"
        )
    return (
        "I can't retrieve that right now. Location-aware access control applies to this data, "
        f"and the gate returned '{decision.effect}': {decision.reason}. "
        f"This decision is logged (correlation {decision.correlation_id[:8]}) under controls "
        f"{', '.join(decision.control_ids) or 'n/a'}. If you believe this is an error, re-attest "
        "your location in the authenticator and try again — or use the break-glass process, which "
        "pages security."
    )
