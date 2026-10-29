import pytest
from fastapi import HTTPException

from src.web.backend.domain import (
    get_stage_by_visit_no,
    school_to_psychagent_sect,
    stage_key_to_skill_stage,
    summary_stage_to_stage_key,
)


@pytest.mark.parametrize(
    ("visit_no", "expected_stage"),
    [
        (1, "assessment"),
        (2, "assessment"),
        (3, "intervention"),
        (8, "intervention"),
        (9, "consolidation"),
        (10, "consolidation"),
    ],
)
def test_visit_number_maps_to_expected_stage(visit_no, expected_stage):
    assert get_stage_by_visit_no(visit_no).key == expected_stage


def test_stage_to_skill_mapping_preserves_expected_values():
    assert stage_key_to_skill_stage("assessment") == 1
    assert stage_key_to_skill_stage("intervention") == 2
    assert stage_key_to_skill_stage("consolidation") == 3


def test_school_mapping_preserves_psychagent_compatibility_ids():
    assert school_to_psychagent_sect("behavioral") == "bt"
    assert school_to_psychagent_sect("psychodynamic") == "pdt"
    with pytest.raises(HTTPException) as error:
        school_to_psychagent_sect("unknown")
    assert error.value.status_code == 404


def test_summary_stage_accepts_stable_keys_and_rejects_unknown_values():
    assert summary_stage_to_stage_key("intervention") == "intervention"
    assert summary_stage_to_stage_key("not-a-stage") is None
