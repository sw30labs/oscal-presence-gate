"""Pipeline wiring. Two runtimes, one behavior.

run_sequential() — pure python, zero heavy deps; what tests and CI use.
build_langgraph() — same nodes as a LangGraph StateGraph, behind the
[graph] extra. Same chassis as oscal-agent-guardrails: Planner → Presence
Verifier → Policy Enforcer → (maybe) Tool → Responder, evidence emitter
tapping every decision.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .evidence_emitter import emit
from .models import ALLOW, HUMAN_DELEGATED, Decision, PresenceAssertion
from .planner import plan
from .policy_enforcer import decide
from .policy_loader import PolicyParams, load_params
from .presence_verifier import verify
from .responder import respond
from .tools import ToolRegistry, default_registry


def run_sequential(
    intent: str,
    principal: str,
    assertion: Optional[PresenceAssertion] = None,
    classification: str = HUMAN_DELEGATED,
    now: Optional[datetime] = None,
    params: Optional[PolicyParams] = None,
    registry: Optional[ToolRegistry] = None,
    evidence_path: Optional[Path] = None,
) -> tuple[Decision, Optional[str], str]:
    """One request through the gate -> (decision, tool_output, message)."""
    params = params or load_params()
    registry = registry or default_registry()

    call = plan(intent, principal, assertion=assertion, classification=classification)
    presence = verify(call.assertion, params, now=now)
    decision = decide(call, presence, params, registry)

    tool_output: Optional[str] = None
    if decision.effect == ALLOW:
        # tool runs only on explicit allow — never before the gate speaks
        tool_output = registry.execute(call.tool_name, call.args)

    if evidence_path is not None:
        emit([decision], out_path=evidence_path)

    return decision, tool_output, respond(decision, tool_output)


def build_langgraph(
    params: Optional[PolicyParams] = None,
    registry: Optional[ToolRegistry] = None,
):
    """The same pipeline as a compiled LangGraph StateGraph. Needs [graph]."""
    try:
        from langgraph.graph import END, StateGraph
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "LangGraph is not installed. Use: pip install 'oscal-presence-gate[graph]'"
        ) from exc

    from typing import TypedDict

    params = params or load_params()
    registry = registry or default_registry()

    class GateState(TypedDict, total=False):
        intent: str
        principal: str
        classification: str
        assertion: Optional[PresenceAssertion]
        call: Any
        presence: Any
        decision: Any
        tool_output: Optional[str]
        message: str

    def planner_node(state: GateState) -> GateState:
        state["call"] = plan(
            state["intent"],
            state["principal"],
            assertion=state.get("assertion"),
            classification=state.get("classification", HUMAN_DELEGATED),
        )
        return state

    def presence_node(state: GateState) -> GateState:
        state["presence"] = verify(state["call"].assertion, params)
        return state

    def enforcer_node(state: GateState) -> GateState:
        state["decision"] = decide(state["call"], state["presence"], params, registry)
        return state

    def tool_node(state: GateState) -> GateState:
        d = state["decision"]
        state["tool_output"] = (
            registry.execute(d.tool_name, state["call"].args) if d.effect == ALLOW else None
        )
        return state

    def responder_node(state: GateState) -> GateState:
        state["message"] = respond(state["decision"], state.get("tool_output"))
        return state

    g = StateGraph(GateState)
    g.add_node("planner", planner_node)
    g.add_node("presence_verifier", presence_node)
    g.add_node("policy_enforcer", enforcer_node)
    g.add_node("tool", tool_node)
    g.add_node("responder", responder_node)
    g.set_entry_point("planner")
    g.add_edge("planner", "presence_verifier")
    g.add_edge("presence_verifier", "policy_enforcer")
    g.add_edge("policy_enforcer", "tool")
    g.add_edge("tool", "responder")
    g.add_edge("responder", END)
    return g.compile()
