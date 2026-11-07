import asyncio
import unittest
from pathlib import Path

from src.sample.client.simulator import ClientSimulator
from src.sample.core.prompt_manager import PromptManager
from src.sample.core.schemas import ClientCase, PublicMemory


class RecordingPromptManager:
    def __init__(self):
        self.output_language = None

    def render_client_dialogue(self, **kwargs):
        self.output_language = kwargs["output_language"]
        return f"Client prompt in {self.output_language}"


class RecordingBackend:
    def __init__(self):
        self.messages = None
        self.kwargs = None

    async def chat_text(self, messages, **kwargs):
        self.messages = messages
        self.kwargs = kwargs
        return "Resposta natural."


class ClientSimulatorLocalizationTests(unittest.TestCase):
    def setUp(self):
        self.case = ClientCase(
            case_id="localization-test",
            modality="cbt",
            basic_info={"main_problem": "ansiedade"},
            theory_info={},
        )
        self.memory = PublicMemory()
        self.previous_dialogue = [{"role": "assistant", "content": "Vamos explorar isso."}]

    def response(self, language, dialogue=None, memory=None):
        simulator = ClientSimulator(prompt_manager=None, output_language=language)
        return simulator._fallback_client_utterance(
            self.case,
            1,
            dialogue or [],
            memory or self.memory,
        )

    def test_requested_language_reaches_prompt_and_model_backend(self):
        prompt_manager = RecordingPromptManager()
        backend = RecordingBackend()
        simulator = ClientSimulator(
            prompt_manager=prompt_manager,
            output_language="Português (Brasil)",
            backend=backend,
        )
        response = asyncio.run(
            simulator.generate_client_utterance(
                case=self.case,
                session_index=1,
                prior_transcript=[],
                public_memory=self.memory,
            )
        )
        self.assertEqual(response, "Resposta natural.")
        self.assertEqual(prompt_manager.output_language, "Português (Brasil)")
        self.assertEqual(backend.kwargs["output_language"], "Português (Brasil)")
        self.assertIn("Respond in Português (Brasil)", backend.messages[0]["content"])
        self.assertEqual(backend.messages[1]["content"], "Client prompt in Português (Brasil)")

    def test_portuguese_brazil_first_session_fallback(self):
        response = self.response("Português (Brasil)")
        self.assertIn("sessão 1", response)
        self.assertIn("ansiedade", response)
        self.assertIn("nesta semana", response)

    def test_portuguese_brazil_follow_up_fallback(self):
        response = self.response("pt-BR", self.previous_dialogue)
        self.assertIn("sentimentos confusos", response)
        self.assertIn("Vamos explorar isso.", response)

    def test_portuguese_missing_concern_uses_localized_fallback(self):
        case_without_concern = ClientCase("empty", "cbt", {}, {})
        simulator = ClientSimulator(prompt_manager=None, output_language="pt-BR")
        response = simulator._fallback_client_utterance(
            case_without_concern,
            1,
            [],
            self.memory,
        )
        self.assertIn("estresse e sobrecarga emocional", response)

    def test_portuguese_sentiment_markers(self):
        positive = PublicMemory(session_recaps=[{"summary": "Senti alívio e progresso"}])
        negative = PublicMemory(session_recaps=[{"summary": "Tenho me sentido ansioso"}])
        self.assertIn("um pouco melhor", self.response("pt-BR", self.previous_dialogue, positive))
        self.assertIn("muita pressão", self.response("pt-BR", self.previous_dialogue, negative))

    def test_client_prompt_renders_in_requested_languages(self):
        prompt_manager = PromptManager(Path(__file__).resolve().parents[1] / "prompts")
        for language in ("English", "Português (Brasil)"):
            with self.subTest(language=language):
                prompt = prompt_manager.render_client_dialogue(
                    case=self.case,
                    session_index=2,
                    prior_transcript=self.previous_dialogue,
                    output_language=language,
                    public_memory=self.memory,
                )
                self.assertIn(f"conversational {language}", prompt)
                self.assertIn("Vamos explorar isso.", prompt)
                self.assertIn("ansiedade", prompt)

    def test_session_opening_prompt_preserves_locale_and_end_token(self):
        prompt_manager = PromptManager(Path(__file__).resolve().parents[1] / "prompts")
        prompt = prompt_manager.render_session_opening(
            modality="CBT",
            session_index=3,
            end_token="</end>",
            output_language="Português (Brasil)",
        )
        self.assertIn("Respond in Português (Brasil)", prompt)
        self.assertIn("session 3", prompt)
        self.assertIn("</end>", prompt)

    def test_public_recap_renders_only_supplied_context(self):
        prompt_manager = PromptManager(Path(__file__).resolve().parents[1] / "prompts")
        memory = PublicMemory(
            known_static_traits={"name": "Ana"},
            session_recaps=[{"summary": "A client-provided summary"}],
            last_homework=["A client-provided task"],
        )
        prompt = prompt_manager.render_public_recap(public_memory=memory)
        self.assertIn('"name": "Ana"', prompt)
        self.assertIn("A client-provided summary", prompt)
        self.assertIn("A client-provided task", prompt)
        self.assertIn("Use only this information", prompt)

    def test_public_counselor_prompt_localizes_empty_context_and_modality(self):
        prompt_manager = PromptManager(Path(__file__).resolve().parents[1] / "prompts")
        portuguese_prompt = prompt_manager.render_counselor_system(
            modality="cbt",
            session_index=1,
            output_language="pt-BR",
            end_token="</end>",
            public_memory=self.memory,
        )
        self.assertIn("Terapia Cognitivo-Comportamental (TCC)", portuguese_prompt)
        self.assertIn("Sem informações de contexto confirmadas", portuguese_prompt)
        self.assertIn("Sem histórico de sessões anteriores", portuguese_prompt)

        english_prompt = prompt_manager.render_counselor_system(
            modality="cbt",
            session_index=1,
            output_language="English",
            end_token="</end>",
            public_memory=self.memory,
        )
        self.assertIn("Cognitive Behavioral Therapy (CBT)", english_prompt)
        self.assertIn("No confirmed background information", english_prompt)

    def test_jinja_unavailable_fallback_respects_output_language(self):
        prompt_manager = PromptManager(Path(__file__).resolve().parents[1] / "prompts")
        prompt_manager._env = None
        prompt = prompt_manager.render_client_dialogue(
            case=self.case,
            session_index=1,
            prior_transcript=[],
            output_language="Português (Brasil)",
            public_memory=self.memory,
        )
        self.assertIn("português", prompt.lower())
        self.assertIn("Queixa principal", prompt)
        self.assertFalse(any("\u4e00" <= character <= "\u9fff" for character in prompt))

        prompt_manager = PromptManager(Path(__file__).resolve().parents[1] / "prompts")
        prompt_manager._env = None
        english_prompt = prompt_manager.render_client_dialogue(
            case=self.case,
            session_index=1,
            prior_transcript=[],
            output_language="English",
            public_memory=self.memory,
        )
        self.assertIn("Main concern", english_prompt)
        self.assertFalse(any("\u4e00" <= character <= "\u9fff" for character in english_prompt))

    def test_english_is_the_fallback_for_unrecognized_output_languages(self):
        self.assertIn("This is session 1", self.response("English"))
        self.assertIn("This is session 1", self.response("unsupported-locale"))


if __name__ == "__main__":
    unittest.main()
