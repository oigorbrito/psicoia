#!/usr/bin/env python3
"""Generate a locale-specific skill catalog with a local Ollama chat model."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

TEXT_FIELDS = ("skill_name", "skill_description", "when_to_use", "trigger")
HAN = re.compile(r"[\u3400-\u9fff]")
HAN_ANNOTATION = re.compile(
    r"[\u3400-\u9fff]+\s*[（(]([^()（）]*[A-Za-zÀ-ÖØ-öø-ÿ][^()（）]*)[）)]"
)
SYSTEM_PROMPT = """You are a careful clinical-content translator. Translate every supplied human-readable field from Simplified Chinese into the requested target language. Preserve the source meaning, clinical scope, uncertainty, and level of specificity; do not add advice, diagnoses, risk claims, or explanations. Keep technical acronyms, scale names, numbers, and quoted examples accurate. Translate quoted Chinese examples too; the output must contain no Chinese/Han characters. Return one JSON object only, shaped as {\"translations\": {<same skill IDs>: {<same text-field keys>: <translated strings>}}}. Include every supplied ID and field exactly once. Do not include identifiers or any text outside the JSON object."""


def _parse_translations(content: str, expected: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    result = json.loads(content)
    if not isinstance(result, dict):
        raise ValueError("response must be a JSON object")
    translations = result.get("translations")
    if not isinstance(translations, dict):
        # Some local models return the requested ID-to-fields map directly.
        translations = result if result.keys() == expected.keys() else None
    if not isinstance(translations, dict):
        keys = sorted(result)
        raise ValueError(f"response must contain the expected translation IDs (found top-level keys: {keys})")
    if not isinstance(translations, dict) or translations.keys() != expected.keys():
        raise ValueError("translation IDs do not match the input IDs")
    for skill_id, fields in expected.items():
        translated_fields = translations[skill_id]
        if not isinstance(translated_fields, dict) or translated_fields.keys() != fields.keys():
            raise ValueError(f"{skill_id}: translated fields do not match the input")
        for field, value in translated_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{skill_id}.{field}: translation must be non-empty text")
            if HAN.search(value):
                raise ValueError(f"{skill_id}.{field}: translation still contains Han characters")
    return translations


def _ollama_chat(
    base_url: str,
    model: str,
    target: str,
    batch: dict[str, dict[str, str]],
    correction: str = "",
) -> str:
    language_name = "English" if target == "en" else "Brazilian Portuguese"
    user_content = (
        f"Target language: {language_name}\nTranslate these entries:\n"
        + json.dumps(batch, ensure_ascii=False)
    )
    if correction:
        user_content += (
            "\nCorrection required: The previous response failed validation ("
            + correction
            + "). Return the complete corrected JSON. Translate every quoted example and remove all Han characters."
        )
    body = {
        "model": model,
        "stream": False,
        "think": False,
        "format": "json",
        "options": {"temperature": 0.1, "num_ctx": 8192, "num_predict": 3072},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": user_content,
            },
        ],
    }
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/chat",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=600) as response:
        payload = json.load(response)
    content = payload.get("message", {}).get("content")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("Ollama returned an empty response")
    return content


def _repair_han_field(
    content: str,
    expected: dict[str, dict[str, str]],
    base_url: str,
    model: str,
    locale: str,
    error: ValueError,
) -> dict[str, dict[str, str]]:
    """Re-translate only a field that retained source-script characters."""
    if "still contains Han characters" not in str(error):
        raise error
    payload = json.loads(content)
    translations = payload.get("translations") if isinstance(payload, dict) else None
    if not isinstance(translations, dict) or set(translations) != set(expected):
        raise error
    for skill_id, fields in expected.items():
        if not isinstance(translations[skill_id], dict) or set(translations[skill_id]) != set(fields):
            raise error
        for field, source_text in fields.items():
            if not isinstance(translations[skill_id][field], str):
                raise error
            if not HAN.search(translations[skill_id][field]):
                continue
            # Some model outputs retain a Chinese term beside its translated gloss,
            # e.g. 设想 (planning). Keep the gloss and discard the redundant source script.
            cleaned = HAN_ANNOTATION.sub(r"\1", translations[skill_id][field])
            if not HAN.search(cleaned):
                translations[skill_id][field] = cleaned
                continue
            for attempt in range(3):
                try:
                    field_content = _ollama_chat(
                        base_url,
                        model,
                        locale,
                        {skill_id: {field: source_text}},
                        correction="The previous field contained untranslated Chinese characters. Translate every character into the target language.",
                    )
                    corrected = _parse_translations(
                        field_content, {skill_id: {field: source_text}}
                    )
                    translations[skill_id][field] = corrected[skill_id][field]
                    break
                except (KeyError, TypeError, ValueError) as repair_error:
                    if attempt == 2:
                        raise RuntimeError(
                            f"could not repair {skill_id}.{field}: {repair_error}"
                        ) from repair_error
    return _parse_translations(json.dumps(payload, ensure_ascii=False), expected)


def translate_catalog(
    source_path: Path,
    locale: str,
    model: str,
    base_url: str,
    batch_size: int = 4,
    overwrite: bool = False,
) -> Path:
    source = json.loads(source_path.read_text(encoding="utf-8"))
    if not isinstance(source, dict):
        raise ValueError("source catalog must be a JSON object")
    target_path = source_path.with_name(f"{source_path.stem}.{locale}{source_path.suffix}")
    if target_path.exists() and not overwrite:
        raise FileExistsError(f"refusing to overwrite existing catalog: {target_path}")

    entries = list(source.items())
    partial_path = target_path.with_suffix(target_path.suffix + ".partial")
    translated: dict[str, dict[str, str]] = {}
    if partial_path.exists():
        saved = json.loads(partial_path.read_text(encoding="utf-8"))
        if not isinstance(saved, dict):
            raise ValueError(f"invalid partial translation file: {partial_path}")
        source_ids = {skill_id for skill_id, _ in entries}
        if not set(saved).issubset(source_ids):
            raise ValueError("partial translation contains IDs absent from the source catalog")
        for skill_id, fields in saved.items():
            expected_fields = {
                field: source[skill_id][field]
                for field in TEXT_FIELDS
                if isinstance(source[skill_id].get(field), str)
            }
            translated[skill_id] = _parse_translations(
                json.dumps({"translations": {skill_id: fields}}, ensure_ascii=False),
                {skill_id: expected_fields},
            )[skill_id]
        print(f"Resuming {locale}: {len(translated)}/{len(entries)} records already translated", flush=True)

    for start in range(0, len(entries), batch_size):
        subset = entries[start : start + batch_size]
        expected: dict[str, dict[str, str]] = {}
        for skill_id, item in subset:
            if skill_id in translated:
                continue
            if not isinstance(item, dict):
                raise ValueError(f"{skill_id}: source entry must be an object")
            expected[skill_id] = {
                field: item[field]
                for field in TEXT_FIELDS
                if isinstance(item.get(field), str)
            }
            if not expected[skill_id].get("skill_name") or not expected[skill_id].get("skill_description"):
                raise ValueError(f"{skill_id}: required skill text is missing")

        if not expected:
            continue

        last_error: Exception | None = None
        for attempt in range(3):
            try:
                content = _ollama_chat(
                    base_url,
                    model,
                    locale,
                    expected,
                    correction=str(last_error) if last_error is not None else "",
                )
                try:
                    batch_translations = _parse_translations(content, expected)
                except ValueError as validation_error:
                    batch_translations = _repair_han_field(
                        content, expected, base_url, model, locale, validation_error
                    )
                translated.update(batch_translations)
                last_error = None
                break
            except (OSError, ValueError, json.JSONDecodeError) as error:
                last_error = error
                if attempt == 2:
                    raise RuntimeError(
                        f"translation failed for records {start + 1}-{start + len(subset)}: {error}"
                    ) from error
        if last_error is not None:
            raise last_error
        completed = min(start + batch_size, len(entries))
        partial_path.with_suffix(partial_path.suffix + ".tmp").write_text(
            json.dumps(translated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        partial_path.with_suffix(partial_path.suffix + ".tmp").replace(partial_path)
        print(f"{locale}: translated {completed}/{len(entries)}", flush=True)

    output: dict[str, dict[str, Any]] = {}
    for skill_id, source_item in entries:
        item = dict(source_item)
        item.update(translated[skill_id])
        output[skill_id] = item
    target_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    partial_path.unlink(missing_ok=True)
    return target_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="source meta_skills.json or micro_skills.json")
    parser.add_argument("--locale", choices=("en", "pt-BR"), required=True)
    parser.add_argument("--model", default="qwen3.5:9b-q4_K_M")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.batch_size < 1 or args.batch_size > 8:
        parser.error("--batch-size must be between 1 and 8")
    try:
        output = translate_catalog(
            args.source, args.locale, args.model, args.base_url, args.batch_size, args.overwrite
        )
    except (OSError, ValueError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
