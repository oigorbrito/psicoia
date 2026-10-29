from pathlib import Path

from sample.backends.dummy_backend import DummyBackend
from sample.client.simulator import ClientSimulator
from sample.core.language import output_language_instruction
from sample.core.prompt_manager import PromptManager
from sample.core.schemas import ClientCase, PublicMemory, RuntimeConfig
from web.backend.localization import (
    DEFAULT_OUTPUT_LANGUAGE,
    output_language_or_default,
    structured_output_contract,
    validation_message,
)


def test_runtime_defaults_to_brazilian_portuguese_without_changing_override(monkeypatch):
    monkeypatch.setenv("PSYCHAGENT_EMBEDDING_API_KEY", "synthetic-test-key")
    assert RuntimeConfig().output_language == DEFAULT_OUTPUT_LANGUAGE
    assert RuntimeConfig.from_dict({}).output_language == DEFAULT_OUTPUT_LANGUAGE
    assert RuntimeConfig.from_dict({"output_language": "English"}).output_language == "English"


def test_web_language_contract_preserves_machine_fields_and_localizes_text():
    contract = structured_output_contract("Português (Brasil)")
    assert "português brasileiro" in contract
    assert "chaves JSON" in contract
    assert output_language_or_default(None) == "Português (Brasil)"
    assert validation_message("missing") == "Este campo é obrigatório."


def test_sample_prompts_end_with_explicit_requested_output_language():
    prompt_manager = PromptManager(Path("prompts"))
    counselor_prompt = prompt_manager.render_counselor_system(
        modality="cbt",
        session_index=1,
        output_language="Português (Brasil)",
        end_token="</end>",
        public_memory=PublicMemory(),
    )
    assert counselor_prompt.endswith(output_language_instruction("Português (Brasil)", "counselor"))
    assert "<\u002fend>" in counselor_prompt
    assert "中文回应" not in counselor_prompt

    client_prompt = prompt_manager.render_client_dialogue(
        case=ClientCase("synthetic", "cbt", {}, {}),
        session_index=1,
        prior_transcript=[],
        output_language="English",
    )
    assert client_prompt.endswith(output_language_instruction("English", "client"))


def test_simulated_outputs_follow_pt_br_default():
    simulator = ClientSimulator(prompt_manager=PromptManager(Path("prompts")))
    utterance = simulator._fallback_client_utterance(
        ClientCase("synthetic", "cbt", {}, {}), 1, [], None
    )
    assert "Esta é a sessão 1" in utterance

    import asyncio

    output = asyncio.run(
        DummyBackend().chat_text(
            [{"role": "system", "content": "Você simula a pessoa atendida"}],
            output_language="Português (Brasil)",
        )
    )
    assert "abrigo" in output


def test_web_request_schema_preserves_field_names_enum_and_localized_descriptions():
    from web.backend.schemas import CreateCourseRequest

    schema = CreateCourseRequest.model_json_schema()
    properties = schema["properties"]
    assert set(properties) == {
        "school_id",
        "title",
        "planned_visit_count",
        "goal_summary",
        "intake_note",
        "goals",
        "auto_start_first_visit",
        "opening_note",
        "output_language",
    }
    language_value = properties["output_language"]["anyOf"][0]
    assert language_value["enum"] == ["English", "Português (Brasil)"]
    assert "Idioma solicitado" in properties["output_language"]["description"]
    main_source = Path("src/web/main.py").read_text(encoding="utf-8")
    assert 'title="API Web do PsicoIA"' in main_source
    assert '@app.post("/auth/login"' in main_source
    courses_source = Path("src/web/backend/routes/courses.py").read_text(encoding="utf-8")
    assert '"/courses"' in courses_source
