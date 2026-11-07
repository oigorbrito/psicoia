import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_canonical_display_brand_and_upstream_attribution_are_distinct():
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_pt = (ROOT / "README.pt-BR.md").read_text(encoding="utf-8")
    legacy_readme = (ROOT / "README_CN.md").read_text(encoding="utf-8")

    assert readme_en.startswith("# PsicoIA\n")
    assert readme_pt.startswith("# PsicoIA\n")
    assert "## How PsicoIA Works" in readme_en
    assert "## Como o PsicoIA funciona" in readme_pt
    assert "# PsicoIA — documentation" in legacy_readme
    assert "**PsychAgent:" in readme_en and "**PsychAgent:" in readme_pt
    assert "https://github.com/ECNU-ICALK/PsychAgent" in readme_en


def test_web_display_metadata_uses_psicoia_without_changing_compatibility_keys():
    html = (ROOT / "src/web/index.html").read_text(encoding="utf-8")
    web_readme_en = (ROOT / "src/web/README.md").read_text(encoding="utf-8")
    web_readme_pt = (ROOT / "src/web/README.pt-BR.md").read_text(encoding="utf-8")
    main = (ROOT / "src/web/main.py").read_text(encoding="utf-8")
    i18n = (ROOT / "src/web/src/i18n.js").read_text(encoding="utf-8")

    assert "<title>PsicoIA</title>" in html
    assert web_readme_en.startswith("# PsicoIA Web\n")
    assert web_readme_pt.startswith("# PsicoIA Web\n")
    assert 'FastAPI(title="PsicoIA Web API"' in main
    assert '"This counseling approach is not supported by PsicoIA.": "Esta abordagem não é compatível com o PsicoIA."' in i18n
    assert 'detail="This username is already registered."' in main
    assert 'detail="Incorrect username or password."' in main
    assert "用户已存在" not in main and "用户名或密码错误" not in main
    assert 'export const LOCALE_STORAGE_KEY = "mindcare.locale"' in i18n


def test_private_frontend_package_and_lockfile_names_match_canonical_project():
    package = json.loads((ROOT / "src/web/package.json").read_text(encoding="utf-8"))
    lock = json.loads((ROOT / "src/web/package-lock.json").read_text(encoding="utf-8"))

    assert package["private"] is True
    assert package["name"] == "psicoia-web"
    assert lock["name"] == package["name"]
    assert lock["packages"][""]["name"] == package["name"]
