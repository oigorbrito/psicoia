import json
from pathlib import Path

from src.sample.main import build_arg_parser


ROOT = Path(__file__).resolve().parents[1]


def test_visible_project_identity_and_upstream_attribution():
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_pt = (ROOT / "README.pt-BR.md").read_text(encoding="utf-8")
    html = (ROOT / "src/web/index.html").read_text(encoding="utf-8")
    web_main = (ROOT / "src/web/main.py").read_text(encoding="utf-8")

    assert readme_en.startswith("# PsicoIA\n")
    assert readme_pt.startswith("# PsicoIA\n")
    assert "https://github.com/ECNU-ICALK/PsychAgent" in readme_en
    assert "<title>PsicoIA</title>" in html
    assert 'FastAPI(title="PsicoIA Web API"' in web_main


def test_cli_uses_psicoia_display_name_without_changing_compatibility_mode():
    parser = build_arg_parser()
    assert parser.parse_args([]).mode == "psychagent"
    mode_action = next(action for action in parser._actions if action.dest == "mode")
    assert mode_action.choices == ["psychagent"]
    assert "PsicoIA standalone sample workflows" in parser.description


def test_private_frontend_package_and_lockfile_names_match():
    package = json.loads((ROOT / "src/web/package.json").read_text(encoding="utf-8"))
    lock = json.loads((ROOT / "src/web/package-lock.json").read_text(encoding="utf-8"))

    assert package["private"] is True
    assert package["name"] == "psicoia-web"
    assert lock["name"] == package["name"]
    assert lock["packages"][""]["name"] == package["name"]
