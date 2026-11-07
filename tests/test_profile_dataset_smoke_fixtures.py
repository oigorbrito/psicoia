import json
from pathlib import Path

from src.sample.io.config_loader import load_dataset_config
from src.sample.io.dataset_loader import DatasetLoader

ROOT = Path(__file__).resolve().parents[1]
MODALITIES = {"bt", "cbt", "het", "pdt", "pmt"}


def test_default_sample_and_rft_datasets_load_only_synthetic_smoke_fixtures():
    for split in ("sample", "rft"):
        config_path = ROOT / "configs" / "datasets" / f"profiles_{split}.yaml"
        cases = DatasetLoader(load_dataset_config(config_path)).load_cases(seed=1)

        assert len(cases) == len(MODALITIES)
        assert {case.modality for case in cases} == MODALITIES
        assert {case.case_id for case in cases} == {"synthetic_smoke_001"}

        for modality in MODALITIES:
            fixture_path = ROOT / "assets" / "profiles" / modality / split / "synthetic_smoke_001.json"
            fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
            metadata = fixture["fixture_metadata"]
            assert metadata["kind"] == "synthetic_smoke_test"
            assert metadata["clinical_equivalence"] is False
            assert metadata["modality"] == modality
            assert metadata["split"] == split
