import ast
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

import pytest

from src.sample.main import build_arg_parser as sample_arg_parser
from src.eval.main import build_arg_parser as eval_arg_parser
from src.rft.main import build_arg_parser as rft_arg_parser


ROOT = Path(__file__).resolve().parents[1]
SOURCE_CONTEXT = re.compile(
    r"(?i)(research|upstream|paper|article|arxiv|checkpoint|model|qwen|psycheval|"
    r"citation|attribution|provenance|prompt|github|ecnu-icalk|title|pesquisa|artigo|"
    r"modelo|cita[cç][aã]o|proveni[eê]ncia|atribui[cç][aã]o|technical|identifier|compatibility|class|api)"
)


def test_visible_project_identity_and_upstream_attribution():
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_pt = (ROOT / "README.pt-BR.md").read_text(encoding="utf-8")
    html = (ROOT / "src/web/index.html").read_text(encoding="utf-8")
    web_main = (ROOT / "src/web/main.py").read_text(encoding="utf-8")
    state_schema = json.loads((ROOT / "policy/project-state.schema.json").read_text(encoding="utf-8"))

    assert readme_en.startswith("# PsicoIA\n")
    assert readme_pt.startswith("# PsicoIA\n")
    assert "canonical project identity" in readme_en
    assert "identidade canônica" in readme_pt
    assert "https://github.com/ECNU-ICALK/PsychAgent" in readme_en
    assert "Upstream research: ICALK" in readme_en
    assert "<title>PsicoIA</title>" in html
    assert 'title="API Web do PsicoIA"' in web_main
    assert state_schema["title"] == "PsicoIA project evidence state"


def test_cli_help_uses_psicoia_and_preserves_legacy_contracts():
    parsers = (sample_arg_parser(), eval_arg_parser(), rft_arg_parser())
    for parser in parsers:
        help_text = parser.format_help()
        assert "PsicoIA" in parser.description
        # PsychAgent may appear in CLI prose only as explicit source attribution.
        assert help_text.replace("base de pesquisa PsychAgent", "").find("PsychAgent") == -1

    sample_parser = parsers[0]
    assert sample_parser.parse_args([]).mode == "psychagent"
    mode_action = next(action for action in sample_parser._actions if action.dest == "mode")
    assert mode_action.choices == ["psychagent"]
    assert "fluxos de demonstração independentes do PsicoIA" in sample_parser.description
    assert "base de pesquisa PsychAgent" in parsers[1].description
    assert "base de pesquisa PsychAgent" in parsers[2].description


def test_public_docs_use_legacy_name_only_with_source_context():
    docs = (
        "README.md",
        "README.pt-BR.md",
        "README_CN.md",
        "src/README.md",
        "src/README.pt-BR.md",
        "src/web/README.md",
        "src/web/README.pt-BR.md",
        "configs/README.md",
        "configs/README.pt-BR.md",
        "assets/skills/README.md",
        "assets/skills/README.pt-BR.md",
        "LOCALIZATION.md",
        "LOCALIZATION.pt-BR.md",
    )
    for relative in docs:
        for line_number, line in enumerate((ROOT / relative).read_text(encoding="utf-8").splitlines(), start=1):
            if "PsychAgent" in line:
                assert SOURCE_CONTEXT.search(line), f"uncontextualized legacy identity in {relative}:{line_number}: {line}"


def test_runtime_string_literals_do_not_rebrand_psicoia_as_psychagent():
    runtime_files = (
        "src/sample/main.py",
        "src/sample/runner.py",
        "src/eval/main.py",
        "src/rft/main.py",
        "src/rft/runner.py",
        "src/web/backend/psychagent_engine.py",
        "src/web/main.py",
        "src/sample/io/dataset_loader.py",
        "scripts/validate_skill_catalog_locales.py",
    )
    allowed_source_attribution = {
        "src/sample/main.py": {"CLI entrypoint for PsicoIA sample workflows based on PsychAgent research code."},
        "src/eval/main.py": {"Execute os fluxos de avaliação do PsicoIA (base de pesquisa PsychAgent)."},
        "src/rft/main.py": {"Execute os fluxos RFT do PsicoIA (base de pesquisa PsychAgent)."},
        "src/sample/io/dataset_loader.py": {
            "Dataset loader following the original PsychAgent case-file compatibility contract."
        },
        "scripts/validate_skill_catalog_locales.py": {
            "Validate PsicoIA localized catalogs against the PsychAgent research-source JSON."
        },
    }
    for relative in runtime_files:
        tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"), filename=relative)
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and "PsychAgent" in node.value:
                assert node.value in allowed_source_attribution.get(relative, set()), (
                    f"unexpected user-visible legacy brand string in {relative}: {node.value!r}"
                )

    frontend = ROOT / "src/web/src"
    for path in frontend.rglob("*"):
        if path.is_file() and path.suffix in {".js", ".jsx", ".css", ".html"}:
            assert "PsychAgent" not in path.read_text(encoding="utf-8"), path.relative_to(ROOT)


def test_backend_launcher_missing_key_error_uses_canonical_identity_without_renaming_env_key():
    bash = shutil.which("bash")
    if not bash:
        pytest.skip("bash is not installed; launcher output was not exercised")

    with tempfile.TemporaryDirectory(prefix="psicoia-identity-") as temp_dir:
        fake_web = Path(temp_dir) / "web"
        fake_web.mkdir()
        (fake_web / "main.py").write_text("# synthetic entry point\n", encoding="utf-8")
        env = os.environ.copy()
        env.update(
            {
                "WEB_DIR": str(fake_web),
                "ENV_FILE": str(Path(temp_dir) / "absent.env"),
                "PSYCHAGENT_EMBEDDING_API_KEY": "",
            }
        )
        result = subprocess.run(
            [bash, str(ROOT / "run_backend.sh")],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=15,
            check=False,
        )

    output = result.stdout + result.stderr
    assert result.returncode == 1
    assert "PsicoIA" in output
    assert "PSYCHAGENT_EMBEDDING_API_KEY" in output
    assert not re.search(r"(?<![A-Za-z0-9_])PsychAgent(?![A-Za-z0-9_])", output)


def test_private_frontend_package_and_lockfile_names_match():
    package = json.loads((ROOT / "src/web/package.json").read_text(encoding="utf-8"))
    lock = json.loads((ROOT / "src/web/package-lock.json").read_text(encoding="utf-8"))

    assert package["private"] is True
    assert package["name"] == "psicoia-web"
    assert lock["name"] == package["name"]
    assert lock["packages"][""]["name"] == package["name"]
