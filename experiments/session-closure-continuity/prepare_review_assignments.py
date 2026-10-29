#!/usr/bin/env python3
"""Copy blank, tracked templates to the ignored directory used for reviewer responses."""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATE_DIR = ROOT / "review" / "templates"
RESPONSE_DIR = ROOT / "review" / "responses"
REVIEWER_FILES = ("reviewer-a.csv", "reviewer-b.csv")


def prepare_assignments(template_dir: Path, response_dir: Path) -> list[Path]:
    sources = [template_dir / name for name in REVIEWER_FILES]
    missing = [path.name for path in sources if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing blank templates: {', '.join(missing)}")
    destinations = [response_dir / name for name in REVIEWER_FILES]
    existing = [path.name for path in destinations if path.exists()]
    if existing:
        raise FileExistsError(
            f"refusing to overwrite response files: {', '.join(existing)}; back them up or move them first"
        )
    response_dir.mkdir(parents=True, exist_ok=True)
    for source, destination in zip(sources, destinations):
        shutil.copyfile(source, destination)
    return destinations


def main() -> None:
    paths = prepare_assignments(TEMPLATE_DIR, RESPONSE_DIR)
    print("Prepared separate response copies (ignored by Git):")
    for path in paths:
        print(f"  {path.relative_to(ROOT)}")
    print("Give each reviewer only their assigned CSV and the review guide.")


if __name__ == "__main__":
    main()
