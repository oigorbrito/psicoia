import json
from pathlib import Path

from scripts.validate_skill_catalog_locales import validate_catalog_pair


def _write(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def test_catalog_validator_accepts_localized_text_with_preserved_identifiers(tmp_path):
    source = {
        "7": {
            "skill_id": "7",
            "skill_name": "技能",
            "skill_description": "描述",
            "parent_ids": ["3", "7"],
            "sect": "bt",
        }
    }
    localized = {
        "7": {
            "skill_id": "7",
            "skill_name": "Skill",
            "skill_description": "Description",
            "parent_ids": ["3", "7"],
            "sect": "bt",
        }
    }
    source_path = _write(tmp_path / "source.json", source)
    localized_path = _write(tmp_path / "localized.json", localized)

    assert validate_catalog_pair(source_path, localized_path) == []


def test_all_committed_localized_catalogs_match_source_contract():
    root = Path(__file__).resolve().parents[1] / "assets/skills/sect"
    checked = 0
    for source_path in root.rglob("*.json"):
        if ".en." not in source_path.name and ".pt-BR." not in source_path.name:
            continue
        locale = "en" if ".en." in source_path.name else "pt-BR"
        base_name = source_path.name.replace(f".{locale}", "")
        source_catalog = source_path.with_name(base_name)
        assert source_catalog.is_file()
        assert validate_catalog_pair(source_catalog, source_path) == []
        checked += 1

    # Count complete locale .json files; the two .json.partial drafts are intentionally excluded.
    assert checked == 40


def test_catalog_validator_rejects_changed_contract_fields_and_untranslated_text(tmp_path):
    source = {
        "7": {
            "skill_id": "7",
            "skill_name": "技能",
            "skill_description": "描述",
            "parent_ids": ["3", "7"],
            "sect": "bt",
        }
    }
    localized = {
        "7": {
            "skill_id": "70",
            "skill_name": "技能",
            "skill_description": "Description",
            "parent_ids": ["7"],
            "sect": "cbt",
        }
    }
    source_path = _write(tmp_path / "source.json", source)
    localized_path = _write(tmp_path / "localized.json", localized)

    errors = validate_catalog_pair(source_path, localized_path)

    assert any("fixed field changed: skill_id" in error for error in errors)
    assert any("fixed field changed: parent_ids" in error for error in errors)
    assert any("fixed field changed: sect" in error for error in errors)
    assert any("skill_name still contains Han" in error for error in errors)
