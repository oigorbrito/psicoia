#!/usr/bin/env python3
"""Summarize independent reviewer agreement without consulting provisional labels."""

import argparse
import csv
from collections import Counter
from pathlib import Path

from build_review_forms import form_row, load_cases

ROOT = Path(__file__).resolve().parent
DEFAULT_REVIEW_DIR = ROOT / "review" / "responses"
EXPECTED_CASE_COUNT = 88
INPUT_COLUMNS = {
    "id_caso",
    "indice_da_sessao",
    "resumo_previo_disponivel",
    "acordo_previo_disponivel",
    "foco_da_sessao",
    "dialogo",
}
CATEGORICAL_VALUES = {
    "decisao_esperada": {"close", "continue"},
    "estado_do_foco": {"explored", "open", "ambivalent"},
    "sinal_de_encerramento": {"none", "natural", "explicit"},
    "estado_do_historico": {"available", "first_session", "unavailable"},
}
TEXT_REVIEW_COLUMNS = {
    "fatos_de_ancoragem",
    "continuidade_a_preservar",
    "afirmacoes_nao_sustentadas",
    "justificativa",
    "observacoes",
}


def cohen_kappa(first: list[str], second: list[str]) -> float | None:
    """Return unweighted Cohen's kappa, or None when chance agreement is undefined."""
    if len(first) != len(second) or not first:
        raise ValueError("rating lists must have the same nonzero length")
    n = len(first)
    observed = sum(a == b for a, b in zip(first, second)) / n
    labels = set(first) | set(second)
    counts_a = Counter(first)
    counts_b = Counter(second)
    expected = sum((counts_a[label] / n) * (counts_b[label] / n) for label in labels)
    if expected == 1:
        return None
    return (observed - expected) / (1 - expected)


def read_completed_form(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        columns = set(reader.fieldnames or [])
    expected_columns = INPUT_COLUMNS | set(CATEGORICAL_VALUES) | TEXT_REVIEW_COLUMNS
    if columns != expected_columns:
        raise ValueError(f"{path.name}: unexpected or missing columns")
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        case_id = row["id_caso"].strip()
        if not case_id or case_id in result:
            raise ValueError(f"{path.name}: blank or duplicate case ID {case_id!r}")
        for field, allowed in CATEGORICAL_VALUES.items():
            value = row[field].strip()
            if value not in allowed:
                raise ValueError(f"{path.name}: {case_id} has invalid/missing {field}: {value!r}")
        for field in TEXT_REVIEW_COLUMNS - {"observacoes"}:
            if not row[field].strip():
                raise ValueError(f"{path.name}: {case_id} is missing {field}")
        result[case_id] = row
    if not result:
        raise ValueError(f"{path.name}: no completed ratings found")
    return result


def compare_forms(
    path_a: Path,
    path_b: Path,
    expected_cases: list[dict] | None = None,
) -> dict[str, dict[str, object]]:
    form_a = read_completed_form(path_a)
    form_b = read_completed_form(path_b)
    if form_a.keys() != form_b.keys():
        raise ValueError("reviewers must rate the same case IDs")
    ids = sorted(form_a, key=lambda value: int(value.rsplit("-", 1)[-1]))
    expected_by_id = None
    if expected_cases is not None:
        expected_by_id = {case["id"]: form_row(case) for case in expected_cases}
        if set(ids) != set(expected_by_id):
            raise ValueError("review forms do not match the current pilot case IDs")
    for case_id in ids:
        for field in INPUT_COLUMNS - {"id_caso"}:
            if form_a[case_id][field] != form_b[case_id][field]:
                raise ValueError(f"case input differs between reviewers: {case_id}/{field}")
            if expected_by_id is not None and form_a[case_id][field] != str(expected_by_id[case_id][field]):
                raise ValueError(f"stale or modified pilot case input: {case_id}/{field}")

    report = {}
    for field in CATEGORICAL_VALUES:
        ratings_a = [form_a[case_id][field].strip() for case_id in ids]
        ratings_b = [form_b[case_id][field].strip() for case_id in ids]
        disagreements = [case_id for case_id, a, b in zip(ids, ratings_a, ratings_b) if a != b]
        report[field] = {
            "n": len(ids),
            "agreement": 1 - len(disagreements) / len(ids),
            "kappa": cohen_kappa(ratings_a, ratings_b),
            "counts_a": dict(sorted(Counter(ratings_a).items())),
            "counts_b": dict(sorted(Counter(ratings_b).items())),
            "disagreements": disagreements,
        }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewer-a", type=Path, default=DEFAULT_REVIEW_DIR / "reviewer-a.csv")
    parser.add_argument("--reviewer-b", type=Path, default=DEFAULT_REVIEW_DIR / "reviewer-b.csv")
    args = parser.parse_args()

    report = compare_forms(args.reviewer_a, args.reviewer_b, load_cases())
    if any(values["n"] != EXPECTED_CASE_COUNT for values in report.values()):
        raise SystemExit(f"Both reviewers must complete all {EXPECTED_CASE_COUNT} cases before comparison.")
    print("Inter-rater agreement (descriptive; not an adjudication or benchmark result):")
    for field, values in report.items():
        kappa = "undefined" if values["kappa"] is None else f"{values['kappa']:.3f}"
        print(f"{field}: n={values['n']}, raw_agreement={values['agreement']:.3f}, Cohen_kappa={kappa}")
        print(f"  reviewer A counts: {values['counts_a']}")
        print(f"  reviewer B counts: {values['counts_b']}")
        if values["disagreements"]:
            print("  disagreements:", ", ".join(values["disagreements"]))
    print("Review free-text rationales and adjudicate disagreements separately; do not infer correctness from agreement alone.")


if __name__ == "__main__":
    main()
