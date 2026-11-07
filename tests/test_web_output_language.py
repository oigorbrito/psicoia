from pathlib import Path

import pytest
from pydantic import ValidationError

import src.sample.prompt_manager as prompt_manager_module
from src.sample.prompt_manager import PsychAgentPromptManager
from src.web.backend.schemas import CloseVisitRequest, CreateCourseRequest, CreateVisitRequest, SendVisitMessageRequest


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("language", ["English", "Português (Brasil)"])
def test_counselor_templates_receive_requested_language(language):
    prompt_root = ROOT / "prompts" / "psychagent"
    for modality in ("bt", "cbt", "het", "pdt", "pmt"):
        manager = PsychAgentPromptManager(prompt_root, modality)
        rendered = manager.render(
            "counselor_system",
            client_info={},
            history=[],
            session_stage="Assessment",
            session_focus=[],
            homework_assigned_from_last_session=[],
            suggested_skills=[],
            output_language=language,
        )
        assert f"Respond in {language}" in rendered
        assert "{{ output_language }}" not in rendered


def test_language_directive_survives_missing_jinja(monkeypatch):
    monkeypatch.setattr(prompt_manager_module, "Template", None)
    manager = PsychAgentPromptManager(ROOT / "prompts" / "psychagent", "bt")
    rendered = manager.render("counselor_system", output_language="English")
    assert "Respond in English" in rendered
    assert "Respond in {{ output_language }}" not in rendered


def test_web_requests_accept_optional_supported_output_languages():
    assert CreateCourseRequest(school_id="cbt", output_language="English").output_language == "English"
    assert CreateVisitRequest(output_language="Português (Brasil)").output_language == "Português (Brasil)"
    assert SendVisitMessageRequest(text="Olá", output_language="Português (Brasil)").output_language == "Português (Brasil)"
    assert SendVisitMessageRequest(text="Hello").output_language is None
    assert CloseVisitRequest(output_language="English").output_language == "English"

    with pytest.raises(ValidationError):
        SendVisitMessageRequest(text="Hello", output_language="es")
