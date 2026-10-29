#!/usr/bin/env python3
"""Create a separate, label-blind adjudication sheet from two completed reviews."""

import argparse
import csv
from pathlib import Path

from build_review_forms import form_row, load_cases
from compare_review_forms import (
    CATEGORICAL_VALUES,
    EXPECTED_CASE_COUNT,
    read_completed_form,
)

ROOT = Path(__file__).resolve().parent
REVIEW_DIR = ROOT / "review" / "responses"
INPUT_FIELDS = [
    "indice_da_sessao",
    "resumo_previo_disponivel",
    "acordo_previo_disponivel",
    "foco_da_sessao",
    "dialogo",
]
TEXT_FIELDS = [
    "fatos_de_ancoragem",
    "continuidade_a_preservar",
    "afirmacoes_nao_sustentadas",
    "justificativa",
    "observacoes",
]
ADJUDICATION_FIELDS = [
    "decisao_adjudicada",
    "estado_do_foco_adjudicado",
    "sinal_de_encerramento_adjudicado",
    "estado_do_historico_adjudicado",
    "fatos_adjudicados",
    "continuidade_adjudicada",
    "afirmacoes_nao_sustentadas_adjudicadas",
    "justificativa_da_adjudicacao",
]
OUTPUT_FIELDS = [
    "id_caso",
    "campos_categoricos_divergentes",
    *INPUT_FIELDS,
    *(f"a_{field}" for field in CATEGORICAL_VALUES),
    *(f"b_{field}" for field in CATEGORICAL_VALUES),
    *(f"a_{field}" for field in TEXT_FIELDS),
    *(f"b_{field}" for field in TEXT_FIELDS),
    *ADJUDICATION_FIELDS,
]


def build_adjudication_rows(
    form_a: dict[str, dict[str, str]],
    form_b: dict[str, dict[str, str]],
    expected_cases: list[dict] | None = None,
) -> list[dict[str, str]]:
    if form_a.keys() != form_b.keys():
        raise ValueError("reviewers must rate the same case IDs")
    ids = sorted(form_a, key=lambda value: int(value.rsplit("-", 1)[-1]))
    expected_by_id = None
    if expected_cases is not None:
        expected_by_id = {case["id"]: form_row(case) for case in expected_cases}
        if set(ids) != set(expected_by_id):
            raise ValueError("review forms do not match the current pilot case IDs")
    result = []
    for case_id in ids:
        a, b = form_a[case_id], form_b[case_id]
        for field in INPUT_FIELDS:
            if a[field] != b[field]:
                raise ValueError(f"case input differs between reviewers: {case_id}/{field}")
            if expected_by_id is not None and a[field] != str(expected_by_id[case_id][field]):
                raise ValueError(f"stale or modified pilot case input: {case_id}/{field}")
        disagreements = [field for field in CATEGORICAL_VALUES if a[field] != b[field]]
        if not disagreements:
            continue
        row = {
            "id_caso": case_id,
            "campos_categoricos_divergentes": "; ".join(disagreements),
            **{field: a[field] for field in INPUT_FIELDS},
            **{f"a_{field}": a[field] for field in CATEGORICAL_VALUES},
            **{f"b_{field}": b[field] for field in CATEGORICAL_VALUES},
            **{f"a_{field}": a[field] for field in TEXT_FIELDS},
            **{f"b_{field}": b[field] for field in TEXT_FIELDS},
            **{field: "" for field in ADJUDICATION_FIELDS},
        }
        result.append(row)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewer-a", type=Path, default=REVIEW_DIR / "reviewer-a.csv")
    parser.add_argument("--reviewer-b", type=Path, default=REVIEW_DIR / "reviewer-b.csv")
    parser.add_argument("--output", type=Path, default=REVIEW_DIR / "adjudication.csv")
    parser.add_argument("--force", action="store_true", help="overwrite an existing adjudication sheet")
    args = parser.parse_args()

    form_a = read_completed_form(args.reviewer_a)
    form_b = read_completed_form(args.reviewer_b)
    if len(form_a) != EXPECTED_CASE_COUNT or len(form_b) != EXPECTED_CASE_COUNT:
        raise SystemExit(f"Both reviewers must complete all {EXPECTED_CASE_COUNT} cases first.")
    rows = build_adjudication_rows(form_a, form_b, load_cases())
    if args.output.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite {args.output}; back it up and pass --force if intended.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Created adjudication sheet with {len(rows)} categorical-disagreement cases.")
    print("No provisional labels were read or changed; review free-text differences separately.")


if __name__ == "__main__":
    main()
