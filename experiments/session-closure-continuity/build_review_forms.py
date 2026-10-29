#!/usr/bin/env python3
"""Build two independent, label-blind human-review CSVs from pilot cases only."""

import argparse
import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REVIEW_DIR = ROOT / "review" / "templates"
CASE_COUNT = 88
REVIEW_COLUMNS = [
    "decisao_esperada",  # close | continue
    "estado_do_foco",  # explored | open | ambivalent
    "sinal_de_encerramento",  # none | natural | explicit
    "estado_do_historico",  # available | first_session | unavailable
    "fatos_de_ancoragem",
    "continuidade_a_preservar",
    "afirmacoes_nao_sustentadas",
    "justificativa",
    "observacoes",
]
FIELDNAMES = [
    "id_caso",
    "indice_da_sessao",
    "resumo_previo_disponivel",
    "acordo_previo_disponivel",
    "foco_da_sessao",
    "dialogo",
    *REVIEW_COLUMNS,
]


def load_cases() -> list[dict]:
    path = ROOT / "pilot-cases.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    if len(rows) != CASE_COUNT or len({row["id"] for row in rows}) != CASE_COUNT:
        raise ValueError(f"expected {CASE_COUNT} unique pilot cases")
    return rows


def form_row(case: dict) -> dict[str, str | int]:
    dialogue = []
    role_names = {"client": "Pessoa", "counselor": "Terapeuta"}
    for turn in case["dialogue"]:
        dialogue.append(f"{role_names[turn['role']]}: {turn['text']}")
    return {
        "id_caso": case["id"],
        "indice_da_sessao": case["session_index"],
        "resumo_previo_disponivel": case["prior_summary"],
        "acordo_previo_disponivel": case["prior_agreement"],
        "foco_da_sessao": "\n".join(f"- {focus}" for focus in case["session_focus"]),
        "dialogo": "\n".join(dialogue),
        **{column: "" for column in REVIEW_COLUMNS},
    }


def has_completed_reviews() -> bool:
    for reviewer in ("reviewer-a.csv", "reviewer-b.csv"):
        path = REVIEW_DIR / reviewer
        if not path.exists():
            continue
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                if any(row.get(column, "").strip() for column in REVIEW_COLUMNS):
                    return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing review entries (destructive; use only after backing them up)",
    )
    args = parser.parse_args()
    if has_completed_reviews() and not args.force:
        raise SystemExit("Refusing to overwrite filled review forms; back them up and pass --force only if intended.")

    cases = load_cases()
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    base_rows = [form_row(case) for case in cases]
    for reviewer, seed in (("reviewer-a.csv", 20260601), ("reviewer-b.csv", 20260602)):
        rows = [dict(row) for row in base_rows]
        random.Random(seed).shuffle(rows)
        with (REVIEW_DIR / reviewer).open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)
    print("Created two label-blind review forms from pilot-cases.jsonl only.")


if __name__ == "__main__":
    main()
