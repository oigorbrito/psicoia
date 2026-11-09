import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "skills" / "sect"
ANDROID_ASSETS = ROOT / "android" / "app" / "src" / "main" / "assets" / "catalog" / "sect"


def test_android_bundles_the_complete_pt_br_catalog_byte_for_byte():
    source_files = sorted(SOURCE.glob("**/*.pt-BR.json"))
    bundled_files = sorted(ANDROID_ASSETS.glob("**/*.pt-BR.json"))

    assert len(source_files) == len(bundled_files) == 30
    source_by_relative_path = {path.relative_to(SOURCE): path for path in source_files}
    bundle_by_relative_path = {path.relative_to(ANDROID_ASSETS): path for path in bundled_files}
    assert source_by_relative_path.keys() == bundle_by_relative_path.keys()

    count = 0
    for relative, source_path in source_by_relative_path.items():
        bundle_path = bundle_by_relative_path[relative]
        assert source_path.read_bytes() == bundle_path.read_bytes()
        records = json.loads(source_path.read_text(encoding="utf-8"))
        for record_id, record in records.items():
            assert record["skill_id"] == record_id
            assert isinstance(record["parent_ids"], list)
            count += 1

    assert count == 5_158


def test_android_manifest_has_no_network_permission_or_provider_configuration():
    manifest = (ROOT / "android/app/src/main/AndroidManifest.xml").read_text(encoding="utf-8")
    app_gradle = (ROOT / "android/app/build.gradle.kts").read_text(encoding="utf-8")
    kotlin = (ROOT / "android/app/src/main/kotlin/org/psicoia/android/MainActivity.kt").read_text(encoding="utf-8")

    assert "android.permission.INTERNET" not in manifest
    assert "project(\":llama\")" in app_gradle
    assert "AiChat.getInferenceEngine" in kotlin
    assert "OpenDocument()" in kotlin
    assert "https://" not in kotlin
    assert "api.openai.com" not in kotlin
    assert "gemini" not in kotlin.lower()
    assert "ConversationStore" in kotlin
    assert "CatalogIndex" in kotlin
    llama_license = ROOT / "android/third_party/llama.cpp/LICENSE"
    packaged_license = ROOT / "android/app/src/main/assets/open_source_licenses/llama.cpp.MIT.txt"
    assert llama_license.read_bytes() == packaged_license.read_bytes()
