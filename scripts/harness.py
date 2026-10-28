#!/usr/bin/env python3
"""Checks a narrow set of local evidence; not a compliance assessment."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "policy/project-state.json"


def valid_state(state: object) -> bool:
    if not isinstance(state, dict):
        return False
    release = state.get("release")
    return (
        state.get("schema_version") == 1
        and state.get("osps_baseline_version") == "2026.08.28"
        and state.get("project_kind") == "code"
        and isinstance(state.get("osps_target_level"), int)
        and not isinstance(state.get("osps_target_level"), bool)
        and state["osps_target_level"] in (1, 2, 3)
        and (state.get("maintainers_count") is None or (isinstance(state["maintainers_count"], int) and not isinstance(state["maintainers_count"], bool) and state["maintainers_count"] >= 0))
        and state.get("consistent_users") in {"unknown", "none", "small", "large"}
        and isinstance(release, dict)
        and {"made", "version", "evidence"}.issubset(release)
        and (release["made"] is None or isinstance(release["made"], bool))
        and (release["version"] is None or isinstance(release["version"], str))
        and (release["evidence"] is None or isinstance(release["evidence"], str))
        and (state.get("production_deployed") is None or isinstance(state.get("production_deployed"), bool))
        and isinstance(state.get("product_stage"), str)
        and isinstance(state.get("notes"), str)
        and isinstance(state.get("enforce_local_gaps"), bool)
    )


def main() -> int:
    try:
        state = json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"GAP STATE: cannot load project state: {exc}")
        return 2
    if not valid_state(state):
        print("GAP STATE: project-state.json does not satisfy the locally checked schema")
        return 2

    print(f"OSPS reference: {state['osps_baseline_version']} (not a compliance claim)")
    print(f"Recorded target: Level {state['osps_target_level']} (not an achieved level)")
    checks = [
        ("CONTRIBUTING.md exists", (ROOT / "CONTRIBUTING.md").is_file()),
        ("Recognized license file exists", any((ROOT / name).exists() for name in ("LICENSE", "COPYING", "LICENSES"))),
        ("Project Python tests exist", any((ROOT / "tests").glob("test_*.py"))),
        ("Web UI tests exist", any((ROOT / "src/web/tests").glob("*.test.js"))),
    ]
    for label, ok in checks:
        print(f"{'PASS' if ok else 'GAP':20} {label}")
    print(f"{'UNKNOWN_EXTERNAL':20} GitHub rules, MFA, active users, releases, private security reporting, and deployment status")
    print("NOTE: This harness validates limited local evidence and file presence; it does not run tests or verify platform settings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
