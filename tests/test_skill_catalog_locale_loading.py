import json
import re
from pathlib import Path
from types import SimpleNamespace

from src.sample.core.schemas import RuntimeConfig
import src.sample.skill_manager as skill_manager_module
from src.sample.skill_manager import SkillManager


def _manager(language: str) -> SkillManager:
    return SkillManager(backend=None, runtime_config=RuntimeConfig(output_language=language))


def test_localized_skill_json_takes_precedence_and_uses_locale_specific_cache(tmp_path, monkeypatch):
    stage_dir = tmp_path / "bt" / "stage1"
    stage_dir.mkdir(parents=True)
    localized_micro = {
        "1": {
            "skill_id": "1",
            "skill_name": "Localized skill",
            "skill_description": "Localized description",
            "parent_ids": ["10"],
        }
    }
    (stage_dir / "micro_skills.en.json").write_text(
        json.dumps(localized_micro), encoding="utf-8"
    )
    (stage_dir / "micro_skills.json").write_text(
        json.dumps({"1": {"skill_id": "1", "skill_name": "Source language"}}),
        encoding="utf-8",
    )
    # A source-language cache must not override an available localized JSON catalog.
    (stage_dir / "micro_skills.pt").write_bytes(b"source cache placeholder")
    monkeypatch.setattr(
        skill_manager_module,
        "torch",
        SimpleNamespace(load=lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("source cache loaded"))),
    )

    manager = _manager("English")
    loaded = manager._load_micro_skills(stage_dir)

    assert loaded["1"]["skill_name"] == "Localized skill"
    assert manager._micro_skills_cache_path(stage_dir) == stage_dir / "micro_skills.en.pt"


def test_localized_embedding_cache_is_loaded_instead_of_source_cache(tmp_path, monkeypatch):
    stage_dir = tmp_path / "bt" / "stage1"
    stage_dir.mkdir(parents=True)
    localized_cache = stage_dir / "micro_skills.en.pt"
    source_cache = stage_dir / "micro_skills.pt"
    localized_cache.write_bytes(b"localized")
    source_cache.write_bytes(b"source")
    localized = {"1": {"skill_id": "1", "skill_name": "Localized cache"}}
    loaded_paths = []

    def fake_load(path, weights_only=False):
        loaded_paths.append(Path(path))
        return localized

    monkeypatch.setattr(skill_manager_module, "torch", SimpleNamespace(load=fake_load))
    loaded = _manager("English")._load_micro_skills(stage_dir)

    assert loaded["1"]["skill_name"] == "Localized cache"
    assert loaded_paths == [localized_cache]


def test_stale_localized_embedding_cache_is_ignored_when_catalog_changes(tmp_path, monkeypatch):
    stage_dir = tmp_path / "bt" / "stage1"
    stage_dir.mkdir(parents=True)
    catalog = stage_dir / "micro_skills.en.json"
    catalog.write_text(
        json.dumps({"1": {"skill_id": "1", "skill_name": "Updated catalog"}}),
        encoding="utf-8",
    )
    (stage_dir / "micro_skills.en.pt").write_bytes(b"stale cache")
    monkeypatch.setattr(
        skill_manager_module,
        "torch",
        SimpleNamespace(load=lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("stale cache loaded"))),
    )

    loaded = _manager("English")._load_micro_skills(stage_dir)

    assert loaded["1"]["skill_name"] == "Updated catalog"


def test_current_localized_embedding_cache_is_selected_when_catalog_digest_matches(
    tmp_path, monkeypatch
):
    stage_dir = tmp_path / "bt" / "stage1"
    stage_dir.mkdir(parents=True)
    catalog = stage_dir / "micro_skills.en.json"
    catalog.write_text(
        json.dumps({"1": {"skill_id": "1", "skill_name": "Translated source"}}),
        encoding="utf-8",
    )
    cache = stage_dir / "micro_skills.en.pt"
    cache.write_bytes(b"current cache")
    manager = _manager("English")
    digest = manager._localized_micro_cache_digest(catalog)
    cache.with_suffix(cache.suffix + ".sha256").write_text(digest, encoding="ascii")
    cached_skills = {"1": {"skill_id": "1", "skill_name": "Cached localized skill"}}
    monkeypatch.setattr(
        skill_manager_module,
        "torch",
        SimpleNamespace(load=lambda *args, **kwargs: cached_skills),
    )

    loaded = manager._load_micro_skills(stage_dir)

    assert loaded["1"]["skill_name"] == "Cached localized skill"


def test_embedding_model_change_invalidates_localized_cache(tmp_path, monkeypatch):
    stage_dir = tmp_path / "bt" / "stage1"
    stage_dir.mkdir(parents=True)
    catalog = stage_dir / "micro_skills.en.json"
    catalog.write_text(
        json.dumps({"1": {"skill_id": "1", "skill_name": "Current catalog"}}),
        encoding="utf-8",
    )
    cache = stage_dir / "micro_skills.en.pt"
    cache.write_bytes(b"cache from old model")
    original_manager = SkillManager(
        backend=None,
        runtime_config=RuntimeConfig(output_language="English", psychagent_embedding_model="old-model"),
    )
    cache.with_suffix(cache.suffix + ".sha256").write_text(
        original_manager._localized_micro_cache_digest(catalog), encoding="ascii"
    )
    monkeypatch.setattr(
        skill_manager_module,
        "torch",
        SimpleNamespace(load=lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("stale model cache loaded"))),
    )

    updated_manager = SkillManager(
        backend=None,
        runtime_config=RuntimeConfig(output_language="English", psychagent_embedding_model="new-model"),
    )
    loaded = updated_manager._load_micro_skills(stage_dir)

    assert loaded["1"]["skill_name"] == "Current catalog"


def test_missing_localized_catalog_is_reported_without_changing_source_fallback(tmp_path, caplog):
    stage_dir = tmp_path / "bt" / "stage1"
    stage_dir.mkdir(parents=True)
    (stage_dir / "meta_skills.json").write_text("{}", encoding="utf-8")
    (stage_dir / "micro_skills.json").write_text("{}", encoding="utf-8")

    manager = _manager("English")
    manager._log_locale_catalog_gaps(tmp_path, ["bt"])

    assert "Localized en skill catalog unavailable for bt/stage1" in caplog.text
    assert "source-language catalogs are selected where present" in caplog.text


def test_localized_meta_json_is_selected_when_available(tmp_path):
    stage_dir = tmp_path / "bt" / "stage1"
    stage_dir.mkdir(parents=True)
    source_meta = {"1": {"skill_id": "1", "skill_name": "Source name"}}
    localized_meta = {"1": {"skill_id": "1", "skill_name": "Localized name"}}
    (stage_dir / "meta_skills.json").write_text(json.dumps(source_meta), encoding="utf-8")
    (stage_dir / "meta_skills.pt-BR.json").write_text(
        json.dumps(localized_meta), encoding="utf-8"
    )

    manager = _manager("Português (Brasil)")
    localized_path = manager._localized_skill_path(stage_dir, "meta_skills", ".json")

    assert localized_path is not None
    assert manager._load_json_dict(localized_path)["1"]["skill_name"] == "Localized name"


def test_complete_pmt_ptbr_catalogs_are_selected_at_runtime():
    assets_root = Path(__file__).resolve().parents[1] / "assets/skills/sect/pmt"
    manager = _manager("Português (Brasil)")
    han = re.compile(r"[\u3400-\u9fff]")

    for stage in ("stage1", "stage2", "stage3"):
        stage_dir = assets_root / stage
        localized_meta_path = manager._localized_skill_path(stage_dir, "meta_skills", ".json")
        localized_micro = manager._load_micro_skills(stage_dir)
        expected_micro = json.loads(
            (stage_dir / "micro_skills.pt-BR.json").read_text(encoding="utf-8")
        )

        assert localized_meta_path == stage_dir / "meta_skills.pt-BR.json"
        assert set(localized_micro) == set(expected_micro)
        assert manager._micro_skills_cache_path(stage_dir).name == "micro_skills.pt-BR.pt"
        assert all(
            not han.search(str(item.get(field, "")))
            for item in expected_micro.values()
            for field in ("skill_name", "skill_description", "when_to_use", "trigger")
        )


def test_unavailable_locale_falls_back_to_source_catalog_without_changing_cache_path(tmp_path):
    stage_dir = tmp_path / "bt" / "stage1"
    stage_dir.mkdir(parents=True)
    source = {"1": {"skill_id": "1", "skill_name": "Source name"}}
    (stage_dir / "micro_skills.json").write_text(json.dumps(source), encoding="utf-8")

    manager = _manager("unsupported")

    assert manager._localized_skill_path(stage_dir, "meta_skills", ".json") is None
    assert manager._load_micro_skills(stage_dir)["1"]["skill_name"] == "Source name"
    assert manager._micro_skills_cache_path(stage_dir) == stage_dir / "micro_skills.pt"


def test_stage3_localizations_preserve_catalog_contract_and_translate_text():
    assets_root = Path(__file__).resolve().parents[1] / "assets/skills/sect"
    fixed_fields = ("skill_id", "parent_ids", "sect")
    text_fields = ("skill_name", "skill_description", "when_to_use", "trigger")
    han = re.compile(r"[\u3400-\u9fff]")

    for approach in ("bt", "het", "pmt"):
        stage_dir = assets_root / approach / "stage3"
        for stem in ("meta_skills", "micro_skills"):
            source = json.loads((stage_dir / f"{stem}.json").read_text(encoding="utf-8"))
            for suffix in ("en", "pt-BR"):
                localized = json.loads(
                    (stage_dir / f"{stem}.{suffix}.json").read_text(encoding="utf-8")
                )
                assert localized.keys() == source.keys()
                for skill_id, source_item in source.items():
                    localized_item = localized[skill_id]
                    assert localized_item.keys() == source_item.keys()
                    for field in fixed_fields:
                        if field in source_item:
                            assert localized_item[field] == source_item[field]
                    for field in text_fields:
                        if field in source_item:
                            assert localized_item[field].strip()
                            assert not han.search(localized_item[field]), (approach, suffix, skill_id, field)

            for suffix, language in (("en", "English"), ("pt-BR", "Português (Brasil)")):
                manager = _manager(language)
                localized_micro = manager._load_micro_skills(stage_dir)
                assert set(localized_micro) == set(
                    json.loads(
                        (stage_dir / f"micro_skills.{suffix}.json").read_text(encoding="utf-8")
                    )
                )
                assert manager._micro_skills_cache_path(stage_dir).name == f"micro_skills.{suffix}.pt"
