import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("repository_harness", ROOT / "scripts/harness.py")
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)


def test_checked_in_project_state_is_valid():
    import json

    state = json.loads((ROOT / "policy/project-state.json").read_text(encoding="utf-8"))
    assert harness.valid_state(state)


def test_unknown_facts_are_allowed_but_invalid_level_is_rejected():
    import json

    state = json.loads((ROOT / "policy/project-state.json").read_text(encoding="utf-8"))
    state["maintainers_count"] = None
    state["release"]["made"] = None
    assert harness.valid_state(state)
    state["osps_target_level"] = 4
    assert not harness.valid_state(state)
