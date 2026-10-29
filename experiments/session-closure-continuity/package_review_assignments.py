#!/usr/bin/env python3
"""Create one minimal, label-blind PT-BR handoff archive per reviewer."""

import csv
import zipfile
from pathlib import Path

from build_review_forms import CASE_COUNT, FIELDNAMES, REVIEW_COLUMNS

ROOT = Path(__file__).resolve().parent
TEMPLATE_DIR = ROOT / "review" / "templates"
PACKAGE_DIR = ROOT / "review" / "packages"
GUIDE_PATH = ROOT / "review" / "REVIEW-GUIDE.pt-BR.md"
REVIEWER_FILES = ("reviewer-a.csv", "reviewer-b.csv")
ARCHIVE_FORM_NAME = "review-form.csv"
ARCHIVE_GUIDE_NAME = "REVIEW-GUIDE.pt-BR.md"


def validate_blank_form(path: Path) -> None:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        rows = list(reader)
    if fields != FIELDNAMES or len(rows) != CASE_COUNT:
        raise ValueError(f"{path.name}: unexpected fields or case count")
    ids = [row["id_caso"] for row in rows]
    if len(set(ids)) != CASE_COUNT:
        raise ValueError(f"{path.name}: case IDs must be unique")
    for row in rows:
        if any(row[field].strip() for field in REVIEW_COLUMNS):
            raise ValueError(f"{path.name}: refusing to package a form with filled ratings")


def create_package(form_path: Path, guide_path: Path, output_path: Path) -> Path:
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite existing package: {output_path}")
    validate_blank_form(form_path)
    if not guide_path.is_file():
        raise FileNotFoundError(f"review guide not found: {guide_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(form_path, arcname=ARCHIVE_FORM_NAME)
        archive.write(guide_path, arcname=ARCHIVE_GUIDE_NAME)
    with zipfile.ZipFile(output_path) as archive:
        names = set(archive.namelist())
    if names != {ARCHIVE_FORM_NAME, ARCHIVE_GUIDE_NAME}:
        output_path.unlink(missing_ok=True)
        raise ValueError(f"unexpected package contents: {sorted(names)}")
    return output_path


def main() -> None:
    package_paths = [PACKAGE_DIR / f"{Path(filename).stem}-pt-BR.zip" for filename in REVIEWER_FILES]
    existing = [path for path in package_paths if path.exists()]
    if existing:
        raise SystemExit(f"Refusing to overwrite existing package(s): {', '.join(map(str, existing))}")
    packages = []
    for filename, package in zip(REVIEWER_FILES, package_paths):
        packages.append(create_package(TEMPLATE_DIR / filename, GUIDE_PATH, package))
    print("Created label-blind reviewer handoff archives (one CSV plus PT-BR guide each):")
    for package in packages:
        print(f"  {package.relative_to(ROOT)}")
    print("Do not give reviewers access to the repository or provisional labels.")


if __name__ == "__main__":
    main()
