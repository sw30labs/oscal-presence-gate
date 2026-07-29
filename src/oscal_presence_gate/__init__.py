"""oscal-presence-gate.

Public surface: run_sequential / build_langgraph (the pipeline),
load_params (runtime policy read from the OSCAL files), PresenceAssertion
and Decision (the data that travels), plus the effect and classification
constants. Everything else is internal plumbing.

Identity tells you who the agent works for; presence tells you where that
person is standing. This package gates on the second.
"""
from .models import (
    ALLOW,
    AUTONOMOUS,
    DENY,
    HUMAN_DELEGATED,
    NEEDS_APPROVAL,
    SOURCE_GPS,
    SOURCE_NETWORK,
    Decision,
    PresenceAssertion,
    PresenceResult,
    ProposedCall,
)
from .graph import build_langgraph, run_sequential
from .policy_loader import PolicyParams, load_params

__version__ = "0.2.0.dev0"

__all__ = [
    "ALLOW",
    "AUTONOMOUS",
    "DENY",
    "HUMAN_DELEGATED",
    "NEEDS_APPROVAL",
    "SOURCE_GPS",
    "SOURCE_NETWORK",
    "Decision",
    "PolicyParams",
    "PresenceAssertion",
    "PresenceResult",
    "ProposedCall",
    "build_langgraph",
    "load_params",
    "run_sequential",
]
