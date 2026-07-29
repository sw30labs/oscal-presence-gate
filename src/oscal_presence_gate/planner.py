"""Planner — user intent in, proposed tool call out.

Deterministic keyword routing so demo and tests run with zero API keys. Swap
in an LLM planner via the [graph] extra — the gate downstream neither knows
nor cares which planner produced the call. That's the point: the control
can't depend on the planner's honesty.
"""
from __future__ import annotations

from typing import Optional

from .models import HUMAN_DELEGATED, PresenceAssertion, ProposedCall

_COVERED_HINTS = ("dispute", "customer", "payment", "account", "client", "chargeback")


def plan(
    intent: str,
    principal: str,
    assertion: Optional[PresenceAssertion] = None,
    classification: str = HUMAN_DELEGATED,
) -> ProposedCall:
    text = intent.lower()
    if any(h in text for h in _COVERED_HINTS):
        return ProposedCall(
            tool_name="read_covered_customer_data",
            args={"scope": "top US retail clients", "intent": intent},
            principal=principal,
            classification=classification,
            assertion=assertion,
        )
    return ProposedCall(
        tool_name="read_public_report",
        args={"intent": intent},
        principal=principal,
        classification=classification,
        assertion=assertion,
    )
