import json

import pytest

from scripts.generate_skill_catalog_locales import _parse_translations


def test_translation_parser_ignores_unrelated_top_level_model_metadata():
    expected = {"42": {"skill_name": "Source name"}}
    response = {
        "translations": {"42": {"skill_name": "Nome localizado"}},
        "metadata": "ignored by the catalog writer",
    }

    assert _parse_translations(json.dumps(response), expected) == response["translations"]
    direct_map = {"42": {"skill_name": "Nome localizado"}}
    assert _parse_translations(json.dumps(direct_map), expected) == direct_map


def test_translation_parser_still_rejects_missing_ids_or_han_text():
    expected = {"42": {"skill_name": "Source name"}}
    missing_id = {"translations": {"99": {"skill_name": "Nome"}}}
    untranslated = {"translations": {"42": {"skill_name": "技能"}}}

    with pytest.raises(ValueError, match="IDs do not match"):
        _parse_translations(json.dumps(missing_id), expected)
    with pytest.raises(ValueError, match="Han characters"):
        _parse_translations(json.dumps(untranslated, ensure_ascii=False), expected)
