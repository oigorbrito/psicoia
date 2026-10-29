#!/usr/bin/env python3
"""Check the two independent review sheets contain cases but no gold labels."""

import csv
from pathlib import Path

from build_review_forms import form_row, load_cases

ROOT = Path(__file__).resolve().parent / "review"
EXPECTED_COUNT = 88
REVIEW_COLUMNS = {
    "decisao_esperada",
    "estado_do_foco",
    "sinal_de_encerramento",
    "estado_do_historico",
    "fatos_de_ancoragem",
    "continuidade_a_preservar",
    "afirmacoes_nao_sustentadas",
    "justificativa",
    "observacoes",
}
INPUT_COLUMNS = {
    "id_caso",
    "indice_da_sessao",
    "resumo_previo_disponivel",
    "acordo_previo_disponivel",
    "foco_da_sessao",
    "dialogo",
}


def load_form(name: str, cases_by_id: dict[str, dict]) -> tuple[list[str], list[dict[str, str]]]:
    with (ROOT / name).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = reader.fieldnames or []
    if set(fields) != INPUT_COLUMNS | REVIEW_COLUMNS:
        raise ValueError(f"{name}: unexpected or missing columns")
    if len(rows) != EXPECTED_COUNT:
        raise ValueError(f"{name}: expected {EXPECTED_COUNT} rows, got {len(rows)}")
    ids = [row["id_caso"] for row in rows]
    if len(set(ids)) != EXPECTED_COUNT:
        raise ValueError(f"{name}: case IDs must be unique")
    if set(ids) != set(cases_by_id):
        raise ValueError(f"{name}: case IDs do not match the current pilot cases")
    input_columns = INPUT_COLUMNS
    for row in rows:
        expected = form_row(cases_by_id[row["id_caso"]])
        for column in input_columns:
            if row[column] != str(expected[column]):
                raise ValueError(f"{name}: stale or changed case input {row['id_caso']}/{column}")
        if any(row[column].strip() for column in REVIEW_COLUMNS):
            raise ValueError(f"{name}: reviewer fields must be blank before independent review")
    return ids, rows


def main() -> None:
    cases_by_id = {case["id"]: case for case in load_cases()}
    ids_a, _ = load_form("reviewer-a.csv", cases_by_id)
    ids_b, _ = load_form("reviewer-b.csv", cases_by_id)
    if set(ids_a) != set(ids_b):
        raise ValueError("review forms do not contain the same case IDs")
    if ids_a == ids_b:
        raise ValueError("reviewer order must be independently randomized")
    print(f"Two blind review forms valid: {EXPECTED_COUNT} cases each; no reference labels included.")


if __name__ == "__main__":
    main()
