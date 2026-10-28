import csv
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_review_forms  # noqa: E402
import compare_review_forms  # noqa: E402


def test_cohen_kappa_known_example():
    assert compare_review_forms.cohen_kappa(
        ["close", "close", "continue", "continue"],
        ["close", "continue", "continue", "continue"],
    ) == pytest.approx(0.5)


def test_cohen_kappa_is_undefined_for_single_shared_category():
    assert compare_review_forms.cohen_kappa(["close"] * 3, ["close"] * 3) is None


def _write_form(path: Path, decision_values: list[str], *, alter_input: bool = False):
    fields = [
        "id_caso", "indice_da_sessao", "resumo_previo_disponivel",
        "acordo_previo_disponivel", "foco_da_sessao", "dialogo",
        *compare_review_forms.CATEGORICAL_VALUES,
        *compare_review_forms.TEXT_REVIEW_COLUMNS,
    ]
    rows = []
    for index, decision in enumerate(decision_values, start=1):
        row = {
            "id_caso": f"SC-{index:02d}",
            "indice_da_sessao": "1",
            "resumo_previo_disponivel": "" if not alter_input else "changed",
            "acordo_previo_disponivel": "",
            "foco_da_sessao": "test focus",
            "dialogo": "Pessoa: exemplo",
            "decisao_esperada": decision,
            "estado_do_foco": "explored",
            "sinal_de_encerramento": "natural",
            "estado_do_historico": "first_session",
            "fatos_de_ancoragem": "fact",
            "continuidade_a_preservar": "carry-forward",
            "afirmacoes_nao_sustentadas": "unsupported claim",
            "justificativa": "reason",
            "observacoes": "",
        }
        rows.append(row)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def test_compare_forms_aligns_ids_and_reports_agreement(tmp_path):
    path_a, path_b = tmp_path / "a.csv", tmp_path / "b.csv"
    _write_form(path_a, ["close", "close", "continue", "continue"])
    _write_form(path_b, ["close", "continue", "continue", "continue"])
    report = compare_review_forms.compare_forms(path_a, path_b)
    assert report["decisao_esperada"]["agreement"] == pytest.approx(0.75)
    assert report["decisao_esperada"]["kappa"] == pytest.approx(0.5)
    assert report["decisao_esperada"]["disagreements"] == ["SC-02"]


def test_compare_forms_rejects_changed_case_input(tmp_path):
    path_a, path_b = tmp_path / "a.csv", tmp_path / "b.csv"
    _write_form(path_a, ["close"], alter_input=False)
    _write_form(path_b, ["close"], alter_input=True)
    with pytest.raises(ValueError, match="case input differs"):
        compare_review_forms.compare_forms(path_a, path_b)


def test_form_builder_detects_existing_annotations(tmp_path, monkeypatch):
    monkeypatch.setattr(build_review_forms, "REVIEW_DIR", tmp_path)
    with (tmp_path / "reviewer-a.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id_caso", *build_review_forms.REVIEW_COLUMNS])
        writer.writeheader()
        writer.writerow({"id_caso": "SC-01", "decisao_esperada": "close"})
    assert build_review_forms.has_completed_reviews()
