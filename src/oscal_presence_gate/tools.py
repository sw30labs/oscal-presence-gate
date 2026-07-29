"""Demo tools. Two on purpose — the smallest world where the classifier
question ("does covered data reach a human?") is real.

TODO(nic): derive covered_data from the component-definition in v0.3 so the
OSCAL file is the single source of truth, not this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass
class ToolSpec:
    name: str
    covered_data: bool
    fn: Callable[[dict[str, Any]], str]
    description: str = ""


def _read_covered_customer_data(args: dict[str, Any]) -> str:
    scope = args.get("scope", "top US retail clients")
    return (
        f"[COVERED DATA] Payment-dispute summary for {scope}: 4,312 disputes QTD, "
        "top driver card-not-present chargebacks. (Demo payload — masked, synthetic.)"
    )


def _read_public_report(args: dict[str, Any]) -> str:
    return "[PUBLIC] Quarterly industry report: dispute volumes trending +6% sector-wide. (Demo payload.)"


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec

    def get(self, name: str) -> Optional[ToolSpec]:
        return self._tools.get(name)

    def execute(self, name: str, args: dict[str, Any]) -> str:
        spec = self._tools[name]
        return spec.fn(args)


def default_registry() -> ToolRegistry:
    r = ToolRegistry()
    r.register(
        ToolSpec(
            name="read_covered_customer_data",
            covered_data=True,
            fn=_read_covered_customer_data,
            description="Bulk US customer financial data (>10k US persons) — covered under 28 CFR 202.",
        )
    )
    r.register(
        ToolSpec(
            name="read_public_report",
            covered_data=False,
            fn=_read_public_report,
            description="Public market data — not covered.",
        )
    )
    return r
