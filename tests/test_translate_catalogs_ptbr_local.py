import io
import json
import sys
from pathlib import Path

import pytest

from scripts import translate_catalogs_ptbr_local as translator


def _synthetic_catalog(root: Path, count: int = 12) -> Path:
    source_path = root / "assets/skills/sect/synthetic/stage1/meta_skills.json"
    source_path.parent.mkdir(parents=True)
    catalog = {}
    for number in range(1, count + 1):
        skill_id = str(number)
        catalog[skill_id] = {
            "skill_id": skill_id,
            "skill_name": f"整理书桌 {number:02d}",
            "skill_description": f"请为 {{{{ user_name }}}} 整理书桌 {number:02d}。",
            "parent_ids": ["root", skill_id],
            "sect": "synthetic",
            "when_to_use": "保留占位符 {{ user_name }} 与源字段。",
        }
    source_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    return source_path


def _translation_for_batch(batch):
    return {
        str(skill_id): {
            "skill_name": f"Organizar a mesa {skill_id}",
            "skill_description": f"Organize a mesa para {{{{ user_name }}}} (item {skill_id}).",
        }
        for skill_id, _ in batch
    }


def _run_main(monkeypatch, root, output, *options):
    monkeypatch.setattr(
        sys,
        "argv",
        ["translate_catalogs_ptbr_local.py", "--root", str(root), "--output", str(output), *options],
    )
    return translator.main()


def test_call_ollama_preserves_exact_placeholders_and_returns_ptbr(monkeypatch):
    batch = [("1", {
        "skill_name": "整理桌面",
        "skill_description": "请为 {{ user_name }} 整理桌面。",
    })]
    response_body = {
        "message": {
            "content": json.dumps({"entries": [{
                "id": "1",
                "skill_name": "Organizar a mesa",
                "skill_description": "Organize a mesa para {{ user_name }}.",
            }]}, ensure_ascii=False)
        }
    }

    def fake_urlopen(request, timeout):
        payload = json.loads(request.data)
        assert payload["model"] == "qwen3.5:4b"
        assert payload["messages"][0]["content"].find("placeholder") >= 0
        return io.BytesIO(json.dumps(response_body).encode("utf-8"))

    monkeypatch.setattr(translator.urllib.request, "urlopen", fake_urlopen)
    translated = translator.call_ollama("http://127.0.0.1:11434", "qwen3.5:4b", batch, 10, 1)

    assert translated["1"]["skill_name"] == "Organizar a mesa"
    assert "{{ user_name }}" in translated["1"]["skill_description"]
    assert not translator.CJK.search(translated["1"]["skill_description"])


@pytest.mark.parametrize(
    "source_text, translated_text",
    [
        ("为 {{ user_name }} 整理。", "Organize para {{nome_usuario}}."),
        ("为 {{ user_name }} 整理 {{ item_id }}。", "Organize {{ item_id }} para {{ user_name }}."),
    ],
)
def test_call_ollama_rejects_altered_or_reordered_placeholders(monkeypatch, source_text, translated_text):
    batch = [("1", {"skill_name": "桌面", "skill_description": source_text})]
    response_body = {
        "message": {
            "content": json.dumps({"entries": [{
                "id": "1",
                "skill_name": "Organizar a mesa",
                "skill_description": translated_text,
            }]}, ensure_ascii=False)
        }
    }
    monkeypatch.setattr(
        translator.urllib.request,
        "urlopen",
        lambda request, timeout: io.BytesIO(json.dumps(response_body).encode("utf-8")),
    )

    with pytest.raises(RuntimeError, match="Placeholder alterado"):
        translator.call_ollama("http://127.0.0.1:11434", "qwen3.5:4b", batch, 10, 1)


def test_single_record_failure_is_isolated_then_resumable(monkeypatch, tmp_path, capsys):
    root = tmp_path / "synthetic-root"
    source_path = _synthetic_catalog(root)
    original_bytes = source_path.read_bytes()
    output = tmp_path / "drafts"

    def fail_record_seven(url, model, batch, timeout, attempts):
        if any(str(skill_id) == "7" for skill_id, _ in batch):
            raise RuntimeError("synthetic invalid translation for record 7")
        return _translation_for_batch(batch)

    monkeypatch.setattr(translator, "call_ollama", fail_record_seven)
    result = _run_main(monkeypatch, root, output, "--batch-size", "6", "--max-records", "12")

    assert result == 2
    draft_path = output / source_path.relative_to(root).with_name("meta_skills.pt-BR.json")
    partial = json.loads(draft_path.read_text(encoding="utf-8"))
    assert len(partial) == 11
    assert "7" not in partial
    assert "PENDING" in capsys.readouterr().err
    assert not draft_path.with_suffix(draft_path.suffix + ".tmp").exists()
    assert source_path.read_bytes() == original_bytes
    assert not (source_path.parent / "meta_skills.pt-BR.json").exists()

    result = _run_main(monkeypatch, root, output, "--verify-only")
    assert result == 1
    assert "INCOMPLETO" in capsys.readouterr().out

    monkeypatch.setattr(
        translator,
        "call_ollama",
        lambda url, model, batch, timeout, attempts: _translation_for_batch(batch),
    )
    result = _run_main(monkeypatch, root, output, "--batch-size", "4", "--max-records", "12")

    assert result == 0
    complete = json.loads(draft_path.read_text(encoding="utf-8"))
    source = json.loads(source_path.read_text(encoding="utf-8"))
    assert translator.verify(source, complete) == 12
    assert source_path.read_bytes() == original_bytes
    assert all(complete[key]["when_to_use"] == source[key]["when_to_use"] for key in source)
    assert all("{{ user_name }}" in complete[key]["skill_description"] for key in complete)
    assert not list(output.rglob("*.tmp"))

    result = _run_main(monkeypatch, root, output, "--verify-only")
    assert result == 0
    assert "COMPLETO" in capsys.readouterr().out


def test_unavailable_ollama_stops_after_bounded_batch_retry(monkeypatch, tmp_path):
    root = tmp_path / "synthetic-root"
    source_path = _synthetic_catalog(root, count=4)
    output = tmp_path / "drafts"
    calls = 0

    def unavailable(url, model, batch, timeout, attempts):
        nonlocal calls
        calls += 1
        raise translator.OllamaUnavailable("synthetic local endpoint unavailable")

    monkeypatch.setattr(translator, "call_ollama", unavailable)
    result = _run_main(monkeypatch, root, output, "--batch-size", "4", "--max-records", "4")

    assert result == 2
    assert calls == 1
    assert not list(output.rglob("*.json"))
