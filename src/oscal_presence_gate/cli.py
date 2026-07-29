"""CLI. `opg demo` — the fly-with-a-token scenario end to end.
`opg validate` — every OSCAL file vs the vendored NIST schemas."""
from __future__ import annotations

import argparse
import sys
from datetime import timedelta
from pathlib import Path

from .evidence_emitter import emit
from .graph import run_sequential
from .models import SOURCE_GPS, PresenceAssertion, utcnow
from .policy_loader import load_params
from .validation import validate_all


def _demo(args: argparse.Namespace) -> int:
    params = load_params()
    now = utcnow()
    intent = "Summarize the payment disputes for our top US retail clients this quarter."
    decisions = []

    print("== oscal-presence-gate demo: the Shanghai scenario ==")
    print(f"policy {params.policy_version} | blocked: {', '.join(sorted(params.blocked_countries))} "
          f"| attestation window: {params.attestation_max_age_s}s\n")

    scenarios = [
        (
            "t0 — analyst in New York, fresh GPS attestation",
            PresenceAssertion("analyst@bank", "US", SOURCE_GPS, issued_at=now - timedelta(minutes=5)),
        ),
        (
            "t+26h — same delegation, assertion long stale (she flew; the agent didn't)",
            PresenceAssertion("analyst@bank", "US", SOURCE_GPS, issued_at=now - timedelta(hours=26)),
        ),
        (
            "re-attestation from Shanghai hotel — fresh, but the country is blocked",
            PresenceAssertion("analyst@bank", "CN", SOURCE_GPS, issued_at=now - timedelta(minutes=2)),
        ),
    ]

    for label, assertion in scenarios:
        decision, _, message = run_sequential(intent, "analyst@bank", assertion=assertion, now=now)
        decisions.append(decision)
        print(f"--- {label}")
        print(f"    -> {decision.effect.upper()}: {decision.reason}")
        print(f"    controls: {', '.join(decision.control_ids)}\n")

    out = Path(args.out)
    emit(decisions, out_path=out)
    print(f"evidence written: {out} ({len(decisions)} observations, OSCAL assessment-results)")
    print("run `opg validate` to check it against the official schema.")
    return 0


def _validate(args: argparse.Namespace) -> int:
    results = validate_all()
    # fold in freshly generated evidence when it exists
    out = Path(args.out)
    if out.exists():
        from .validation import validate_file

        results[str(out)] = validate_file(out)
    bad = {k: v for k, v in results.items() if v}
    for name in sorted(results):
        status = "PASS" if not results[name] else f"FAIL ({len(results[name])})"
        print(f"{status:10s} {name}")
        for e in results[name][:5]:
            print(f"           {e[:160]}")
    return 1 if bad else 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="opg", description="oscal-presence-gate")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("demo", help="run the fly-with-a-token demo and emit evidence")
    d.add_argument("--out", default="output/assessment-results.json")
    d.set_defaults(fn=_demo)

    v = sub.add_parser("validate", help="validate all OSCAL content against vendored NIST schemas")
    v.add_argument("--out", default="output/assessment-results.json")
    v.set_defaults(fn=_validate)

    ns = p.parse_args(argv)
    return ns.fn(ns)


if __name__ == "__main__":
    sys.exit(main())
