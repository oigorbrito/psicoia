from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_PAIRS = (
    ("README.md", "README.pt-BR.md"),
    ("assets/README.md", "assets/README.pt-BR.md"),
    ("assets/profiles/README.md", "assets/profiles/README.pt-BR.md"),
    ("assets/skills/README.md", "assets/skills/README.pt-BR.md"),
    ("configs/README.md", "configs/README.pt-BR.md"),
    ("prompts/README.md", "prompts/README.pt-BR.md"),
    ("src/README.md", "src/README.pt-BR.md"),
    ("src/web/README.md", "src/web/README.pt-BR.md"),
)
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)#]+)")
CODE_FENCE = re.compile(r"^```[^\n]*\n(.*?)^```", re.MULTILINE | re.DOTALL)


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_localized_documentation_pairs_exist_and_keep_code_blocks_identical():
    for source_path, localized_path in DOC_PAIRS:
        source = _read(source_path)
        localized = _read(localized_path)
        assert CODE_FENCE.findall(source) == CODE_FENCE.findall(localized), (
            source_path,
            localized_path,
        )


def test_relative_markdown_links_resolve_for_localized_guides():
    for _, localized_path in DOC_PAIRS:
        document = ROOT / localized_path
        for target in MARKDOWN_LINK.findall(document.read_text(encoding="utf-8")):
            if "://" not in target:
                assert (document.parent / target).exists(), (localized_path, target)


def test_legacy_chinese_readme_path_points_to_maintained_locales():
    legacy_readme = ROOT / "README_CN.md"
    content = legacy_readme.read_text(encoding="utf-8")
    assert "README.md" in content
    assert "README.pt-BR.md" in content
