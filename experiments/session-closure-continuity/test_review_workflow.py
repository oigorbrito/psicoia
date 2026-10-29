import csv
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_adjudication_sheet  # noqa: E402
import build_review_forms  # noqa: E402
import prepare_review_assignments  # noqa: E402
import compare_review_forms  # noqa: E402
import validate_pilot  # noqa: E402


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
            "foco_da_sessao": "- test focus",
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
    assert report["decisao_esperada"]["counts_a"] == {"close": 2, "continue": 2}
    assert report["decisao_esperada"]["counts_b"] == {"close": 1, "continue": 3}
    assert report["decisao_esperada"]["disagreements"] == ["SC-02"]


def test_adjudication_sheet_contains_only_category_disagreements(tmp_path):
    path_a, path_b = tmp_path / "a.csv", tmp_path / "b.csv"
    _write_form(path_a, ["close", "close", "continue", "continue"])
    _write_form(path_b, ["close", "continue", "continue", "continue"])
    rows = build_adjudication_sheet.build_adjudication_rows(
        compare_review_forms.read_completed_form(path_a),
        compare_review_forms.read_completed_form(path_b),
    )
    assert [row["id_caso"] for row in rows] == ["SC-02"]
    assert rows[0]["campos_categoricos_divergentes"] == "decisao_esperada"
    assert rows[0]["a_decisao_esperada"] == "close"
    assert rows[0]["b_decisao_esperada"] == "continue"
    assert set(rows[0]) == set(build_adjudication_sheet.OUTPUT_FIELDS)
    assert rows[0]["decisao_adjudicada"] == ""


def test_compare_forms_can_reject_stale_case_text(tmp_path):
    path_a, path_b = tmp_path / "a.csv", tmp_path / "b.csv"
    _write_form(path_a, ["close"])
    _write_form(path_b, ["close"])
    case = {
        "id": "SC-01",
        "session_index": 1,
        "prior_summary": "",
        "prior_agreement": "",
        "session_focus": ["test focus"],
        "dialogue": [{"role": "client", "text": "exemplo"}],
    }
    compare_review_forms.compare_forms(path_a, path_b, [case])
    case["prior_summary"] = "edited after review forms were generated"
    with pytest.raises(ValueError, match="stale or modified pilot case input"):
        compare_review_forms.compare_forms(path_a, path_b, [case])


def test_full_88_case_review_pipeline_in_temp_files(tmp_path):
    cases = build_review_forms.load_cases()
    fields = build_review_forms.FIELDNAMES
    form_paths = [tmp_path / "reviewer-a.csv", tmp_path / "reviewer-b.csv"]
    for reviewer_index, path in enumerate(form_paths):
        rows = []
        for index, case in enumerate(cases):
            row = build_review_forms.form_row(case)
            row["decisao_esperada"] = "close" if index % 2 == 0 else "continue"
            if reviewer_index == 1 and index == 0:
                row["decisao_esperada"] = "continue"
            row["estado_do_foco"] = ["explored", "open", "ambivalent"][index % 3]
            row["sinal_de_encerramento"] = ["none", "natural", "explicit"][index % 3]
            has_prior = bool(case["prior_summary"].strip() or case["prior_agreement"].strip())
            row["estado_do_historico"] = (
                "available" if has_prior else "first_session" if case["session_index"] == 1 else "unavailable"
            )
            row["fatos_de_ancoragem"] = "synthetic test evidence"
            row["continuidade_a_preservar"] = "synthetic test continuity"
            row["afirmacoes_nao_sustentadas"] = "synthetic test caution"
            row["justificativa"] = "synthetic test rationale"
            rows.append(row)
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    form_a = compare_review_forms.read_completed_form(form_paths[0])
    form_b = compare_review_forms.read_completed_form(form_paths[1])
    report = compare_review_forms.compare_forms(*form_paths, expected_cases=cases)
    adjudication = build_adjudication_sheet.build_adjudication_rows(form_a, form_b, cases)
    assert report["decisao_esperada"]["n"] == 88
    assert report["decisao_esperada"]["disagreements"] == ["SC-01"]
    assert [row["id_caso"] for row in adjudication] == ["SC-01"]


def test_compare_forms_rejects_changed_case_input(tmp_path):
    path_a, path_b = tmp_path / "a.csv", tmp_path / "b.csv"
    _write_form(path_a, ["close"], alter_input=False)
    _write_form(path_b, ["close"], alter_input=True)
    with pytest.raises(ValueError, match="case input differs"):
        compare_review_forms.compare_forms(path_a, path_b)


def test_coverage_cross_tab_reports_zero_cells(capsys):
    validate_pilot.print_cross_tab(
        [
            {"focus_state": "open", "ending_signal": "none"},
            {"focus_state": "explored", "ending_signal": "natural"},
        ],
        "focus_state",
        "ending_signal",
    )
    output = capsys.readouterr().out
    assert "explored: {'natural': 1, 'none': 0}" in output
    assert "open: {'natural': 0, 'none': 1}" in output


def test_pilot_validator_checks_history_against_case_context():
    case = {
        "id": "SC-01",
        "session_index": 2,
        "prior_summary": "",
        "prior_agreement": "",
    }
    label = {"history_state": "unavailable", "ending_signal": "none", "expected_action": "continue"}
    validate_pilot.validate_label_case_consistency(case, label)
    label["history_state"] = "available"
    with pytest.raises(ValueError, match="history_state conflicts"):
        validate_pilot.validate_label_case_consistency(case, label)


def test_pilot_validator_requires_closing_action_for_end_signal():
    case = {
        "id": "SC-02",
        "session_index": 1,
        "prior_summary": "",
        "prior_agreement": "",
    }
    label = {"history_state": "first_session", "ending_signal": "explicit", "expected_action": "continue"}
    with pytest.raises(ValueError, match="must map to close"):
        validate_pilot.validate_label_case_consistency(case, label)


def test_prepare_review_assignments_copies_and_refuses_overwrite(tmp_path):
    templates = tmp_path / "templates"
    responses = tmp_path / "responses"
    templates.mkdir()
    for name in prepare_review_assignments.REVIEWER_FILES:
        (templates / name).write_text("blank template", encoding="utf-8")
    copied = prepare_review_assignments.prepare_assignments(templates, responses)
    assert [path.read_text(encoding="utf-8") for path in copied] == ["blank template", "blank template"]
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        prepare_review_assignments.prepare_assignments(templates, responses)


def test_form_builder_detects_existing_annotations(tmp_path, monkeypatch):
    monkeypatch.setattr(build_review_forms, "REVIEW_DIR", tmp_path)
    with (tmp_path / "reviewer-a.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id_caso", *build_review_forms.REVIEW_COLUMNS])
        writer.writeheader()
        writer.writerow({"id_caso": "SC-01", "decisao_esperada": "close"})
    assert build_review_forms.has_completed_reviews()
