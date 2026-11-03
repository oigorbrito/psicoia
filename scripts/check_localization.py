#!/usr/bin/env python3
"""Run local localization, identity, API-contract, and UI regression tests.

This entry point deliberately does not run release/distribution checks such as
scripts/harness.py. It does not grant rights or validate clinical content.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "src" / "web"
PYTHON_TESTS = (
    "tests/test_localized_documentation.py",
    "tests/test_project_identity.py",
    "tests/test_output_language_localization.py",
    "tests/test_web_output_language.py",
    "tests/test_skill_catalog_locale_loading.py",
    "tests/test_skill_catalog_localization_validation.py",
    "tests/test_skill_manager_locale_retrieval.py",
    "src/web/tests/test_domain.py",
)


def run(label: str, command: list[str], cwd: Path) -> bool:
    print(f"\n== {label} ==", flush=True)
    result = subprocess.run(command, cwd=cwd, check=False)
    if result.returncode:
        print(f"FAIL: {label} exited with {result.returncode}", flush=True)
        return False
    return True


def run_npm_tests() -> bool:
    npm = shutil.which("npm")
    if not npm:
        print("FAIL: npm is unavailable; web localization tests were not run", flush=True)
        return False
    if os.name == "nt":
        return _run_windows_npm(npm)
    return run("Web localization helpers", [npm, "test"], WEB)


def _run_windows_npm(npm: str) -> bool:
    result = subprocess.run(f'"{npm}" test', cwd=WEB, shell=True, check=False)
    if result.returncode:
        print(f"FAIL: Web localization helpers exited with {result.returncode}", flush=True)
        return False
    return True


def main() -> int:
    if not run("Python localization, identity, and contract tests", [
        sys.executable, "-m", "pytest", "-q", *PYTHON_TESTS,
    ], ROOT):
        return 1
    if not run_npm_tests():
        return 1
    print("\nPASS: local localization checks completed; release/distribution gates were not run.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
