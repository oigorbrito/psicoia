#!/usr/bin/env python3
"""Copy the existing PT-BR skill catalogs byte-for-byte into Android assets."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "skills" / "sect"
DESTINATION = ROOT / "android" / "app" / "src" / "main" / "assets" / "catalog" / "sect"
EXPECTED_FILES = 30
EXPECTED_RECORDS = 5158


def main() -> None:
    sources = sorted(SOURCE.glob("**/*.pt-BR.json"))
    if len(sources) != EXPECTED_FILES:
        raise SystemExit(f"Expected {EXPECTED_FILES} PT-BR catalog files; found {len(sources)}")

    records = 0
    for source in sources:
        payload = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise SystemExit(f"Expected an ID-keyed object: {source.relative_to(ROOT)}")
        for record_id, record in payload.items():
            if not isinstance(record, dict) or record.get("skill_id") != record_id:
                raise SystemExit(f"ID/key mismatch in {source.relative_to(ROOT)}: {record_id}")
            if not isinstance(record.get("parent_ids"), list):
                raise SystemExit(f"Missing parent_ids in {source.relative_to(ROOT)}: {record_id}")
        records += len(payload)

    if records != EXPECTED_RECORDS:
        raise SystemExit(f"Expected {EXPECTED_RECORDS} records; found {records}")

    for source in sources:
        relative = source.relative_to(SOURCE)
        destination = DESTINATION / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        if destination.read_bytes() != source.read_bytes():
            raise SystemExit(f"Byte comparison failed after copying {relative}")

    print(f"Copied {len(sources)} PT-BR files ({records} records) byte-for-byte into Android assets.")


if __name__ == "__main__":
    main()
