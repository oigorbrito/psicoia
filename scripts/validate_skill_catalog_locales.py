#!/usr/bin/env python3
"""Validate PsicoIA localized catalogs against the PsychAgent research-source JSON."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

HAN = re.compile(r"[\u3400-\u9fff]")
FIXED_FIELDS = ("skill_id", "parent_ids", "sect")
TEXT_FIELDS = ("skill_name", "skill_description", "when_to_use", "trigger")
CATALOG_NAMES = ("meta_skills", "micro_skills")


def _read_catalog(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"catalog root must be an object: {path}")
    return value


def validate_catalog_pair(source_path: Path, localized_path: Path) -> list[str]:
    """Return contract or untranslated-text errors for one source/locale pair."""
    source = _read_catalog(source_path)
    localized = _read_catalog(localized_path)
    errors: list[str] = []
    if source.keys() != localized.keys():
        missing = sorted(source.keys() - localized.keys())
        extra = sorted(localized.keys() - source.keys())
        errors.append(f"catalog IDs differ (missing={missing}, extra={extra})")

    for skill_id in source.keys() & localized.keys():
        src_item, loc_item = source[skill_id], localized[skill_id]
        if not isinstance(src_item, dict) or not isinstance(loc_item, dict):
            errors.append(f"{skill_id}: catalog entry must be an object")
            continue
        if src_item.keys() != loc_item.keys():
            errors.append(f"{skill_id}: entry fields differ")
            continue
        for field in FIXED_FIELDS:
            if field in src_item and src_item[field] != loc_item[field]:
                errors.append(f"{skill_id}: fixed field changed: {field}")
        for field in TEXT_FIELDS:
            if field not in src_item:
                continue
            value = loc_item[field]
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{skill_id}: {field} must be a non-empty string")
            elif HAN.search(value):
                errors.append(f"{skill_id}: {field} still contains Han characters")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("assets/skills/sect"))
    parser.add_argument("--locale", choices=("en", "pt-BR"), required=True)
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="report coverage and validate present catalogs without failing on missing locale files",
    )
    args = parser.parse_args()

    source_files = sorted(
        stage_dir / f"{name}.json"
        for stage_dir in args.root.glob("*/stage*/")
        for name in CATALOG_NAMES
        if (stage_dir / f"{name}.json").is_file()
    )
    errors: list[str] = []
    missing_count = 0
    localized_count = 0
    source_records = 0
    localized_records = 0
    for source_path in source_files:
        source = _read_catalog(source_path)
        source_records += len(source)
        localized_path = source_path.with_name(
            f"{source_path.stem}.{args.locale}{source_path.suffix}"
        )
        if not localized_path.is_file():
            missing_count += 1
            if not args.allow_missing:
                errors.append(f"missing locale catalog: {localized_path}")
            continue
        localized_count += 1
        localized_records += len(_read_catalog(localized_path))
        errors.extend(
            f"{localized_path}: {error}"
            for error in validate_catalog_pair(source_path, localized_path)
        )

    total = len(source_files)
    print(
        f"{args.locale}: {localized_count}/{total} catalogs; "
        f"{localized_records}/{source_records} records localized"
    )
    for error in errors:
        print(f"ERROR: {error}")
    return 1 if errors or (missing_count and not args.allow_missing) else 0


if __name__ == "__main__":
    raise SystemExit(main())
