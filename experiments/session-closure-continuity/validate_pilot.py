#!/usr/bin/env python3
"""Validate the synthetic session-closure pilot fixtures; makes no model calls."""

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED_COUNT = 44
CASE_FIELDS = {
    "id",
    "category",
    "locale",
    "session_index",
    "prior_summary",
    "prior_agreement",
    "session_focus",
    "dialogue",
    "synthetic",
}
LABEL_FIELDS = {
    "id",
    "expected_action",
    "grounding_facts",
    "carry_forward",
    "must_not_claim",
    "rationale",
    "focus_state",
    "ending_signal",
    "history_state",
}
LABEL_DIMENSIONS = {
    "focus_state": {"explored", "open", "ambivalent"},
    "ending_signal": {"none", "natural", "explicit"},
    "history_state": {"available", "first_session", "unavailable"},
}


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            raise ValueError(f"{path.name}:{line_number}: blank lines are not allowed")
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path.name}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path.name}:{line_number}: each record must be an object")
        rows.append(row)
    return rows


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    cases = load_jsonl(ROOT / "pilot-cases.jsonl")
    labels = load_jsonl(ROOT / "pilot-labels.jsonl")
    require(len(cases) == EXPECTED_COUNT, f"expected {EXPECTED_COUNT} cases, found {len(cases)}")
    require(len(labels) == EXPECTED_COUNT, f"expected {EXPECTED_COUNT} labels, found {len(labels)}")

    case_ids = [row.get("id") for row in cases]
    label_ids = [row.get("id") for row in labels]
    require(len(set(case_ids)) == EXPECTED_COUNT, "case IDs must be unique and non-empty")
    require(len(set(label_ids)) == EXPECTED_COUNT, "label IDs must be unique and non-empty")
    require(set(case_ids) == set(label_ids), "case and label IDs do not match")

    for row in cases:
        case_id = row["id"]
        require(CASE_FIELDS <= row.keys(), f"{case_id}: missing case fields {sorted(CASE_FIELDS - row.keys())}")
        require(row["synthetic"] is True, f"{case_id}: pilot records must be marked synthetic")
        require(row["locale"] == "pt-BR", f"{case_id}: expected pt-BR locale")
        require(isinstance(row["session_index"], int) and row["session_index"] >= 1, f"{case_id}: invalid session_index")
        require(isinstance(row["session_focus"], list) and row["session_focus"], f"{case_id}: session_focus must be non-empty")
        require(isinstance(row["dialogue"], list) and row["dialogue"], f"{case_id}: dialogue must be non-empty")
        for turn in row["dialogue"]:
            require(isinstance(turn, dict) and turn.get("role") in {"client", "counselor"}, f"{case_id}: invalid dialogue role")
            require(isinstance(turn.get("text"), str) and turn["text"].strip(), f"{case_id}: dialogue text must be non-empty")

    for row in labels:
        case_id = row["id"]
        require(LABEL_FIELDS <= row.keys(), f"{case_id}: missing label fields {sorted(LABEL_FIELDS - row.keys())}")
        require(row["expected_action"] in {"close", "continue"}, f"{case_id}: invalid expected_action")
        for field, allowed in LABEL_DIMENSIONS.items():
            require(row[field] in allowed, f"{case_id}: invalid {field}={row[field]!r}")
        require(isinstance(row["grounding_facts"], list) and row["grounding_facts"], f"{case_id}: grounding_facts must be non-empty")
        require(isinstance(row["must_not_claim"], list), f"{case_id}: must_not_claim must be a list")
        require(isinstance(row["carry_forward"], str) and row["carry_forward"].strip(), f"{case_id}: carry_forward must be non-empty")
        require(isinstance(row["rationale"], str) and row["rationale"].strip(), f"{case_id}: rationale must be non-empty")

    print(f"Pilot fixtures valid: {EXPECTED_COUNT} synthetic cases and labels; no model calls performed.")
    for field in LABEL_DIMENSIONS:
        counts = Counter(row[field] for row in labels)
        print(f"{field}: {dict(sorted(counts.items()))}")
    action_by_signal = Counter((row["ending_signal"], row["expected_action"]) for row in labels)
    print(f"ending_signal × expected_action: {dict(sorted(action_by_signal.items()))}")


if __name__ == "__main__":
    main()
