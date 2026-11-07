"""Jinja2-based prompt rendering utilities."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from .schemas import ClientCase, PublicMemory

try:
    from jinja2 import Environment, FileSystemLoader, StrictUndefined
except ImportError:  # pragma: no cover - fallback path for minimal environments
    Environment = None  # type: ignore[assignment]
    FileSystemLoader = None  # type: ignore[assignment]
    StrictUndefined = None  # type: ignore[assignment]


@dataclass
class PromptManager:
    """Loads and renders public and client prompts."""

    prompt_root: Path
    _env: Optional[Any] = None

    def __post_init__(self) -> None:
        if Environment is not None:
            self._env = Environment(
                loader=FileSystemLoader(str(self.prompt_root)),
                autoescape=False,
                undefined=StrictUndefined,
                trim_blocks=True,
                lstrip_blocks=True,
            )

    def render_template(self, template_relpath: str, **kwargs: Any) -> str:
        if self._env is not None:
            template = self._env.get_template(template_relpath)
            return template.render(**kwargs).strip()

        # Fallback: simple replacement for {{ key }} expressions.
        path = self.prompt_root / template_relpath
        text = path.read_text(encoding="utf-8")
        return _simple_render(text, kwargs).strip()

    def render_counselor_system(
        self,
        *,
        modality: str,
        session_index: int,
        output_language: str,
        end_token: str,
        public_memory: PublicMemory,
        therapy_name: Optional[str] = None,
    ) -> str:
        known_static_traits_text = (
            json.dumps(public_memory.known_static_traits, ensure_ascii=False, indent=2)
            if public_memory.known_static_traits
            else _localized_empty(
                output_language,
                "(No confirmed background information)",
                "(Sem informações de contexto confirmadas)",
            )
        )
        session_recaps_text = (
            json.dumps(public_memory.session_recaps, ensure_ascii=False, indent=2)
            if public_memory.session_recaps
            else _localized_empty(
                output_language,
                "(No previous session history)",
                "(Sem histórico de sessões anteriores)",
            )
        )
        last_homework_text = (
            json.dumps(public_memory.last_homework, ensure_ascii=False, indent=2)
            if public_memory.last_homework
            else _localized_empty(output_language, "(None)", "(Nenhuma)")
        )

        return self.render_template(
            "public/counselor_system.jinja2",
            therapy_name=therapy_name or _normalize_therapy_name(modality, output_language),
            modality=modality,
            session_index=session_index,
            output_language=output_language,
            end_token=end_token,
            known_static_traits_text=known_static_traits_text,
            session_recaps_text=session_recaps_text,
            last_homework_text=last_homework_text,
        )

    def render_session_opening(
        self,
        *,
        modality: str,
        session_index: int,
        end_token: str = "</end>",
        output_language: str = "English",
    ) -> str:
        return self.render_template(
            "public/session_opening.jinja2",
            modality=modality,
            session_index=session_index,
            end_token=end_token,
            output_language=output_language,
        )

    def render_public_recap(self, *, public_memory: PublicMemory) -> str:
        recap_items = [
            {
                "session_index": item.get("session_index", idx + 1),
                "summary": item.get("summary", ""),
                "homework": item.get("homework", []),
                "static_traits": item.get("static_traits", {}),
            }
            for idx, item in enumerate(public_memory.session_recaps)
        ]
        return self.render_template(
            "public/public_recap.jinja2",
            known_static_traits_json=json.dumps(public_memory.known_static_traits, ensure_ascii=False, indent=2),
            recaps_json=json.dumps(recap_items, ensure_ascii=False, indent=2),
            last_homework_json=json.dumps(public_memory.last_homework, ensure_ascii=False),
        )

    def render_client_dialogue(
        self,
        *,
        case: ClientCase,
        session_index: int,
        prior_transcript: list[dict[str, Any]],
        output_language: str,
        public_memory: Optional[PublicMemory] = None,
        client_state: Optional[Dict[str, Any]] = None,
    ) -> str:
        normalized_client_state = client_state or {}
        intake_profile = dict(case.intake_profile)
        if "static_traits" not in intake_profile or not isinstance(intake_profile.get("static_traits"), dict):
            intake_profile["static_traits"] = dict(case.basic_info)
        if "growth_experiences" not in intake_profile or not isinstance(intake_profile.get("growth_experiences"), list):
            intake_profile["growth_experiences"] = []

        last_counselor_message = ""
        for msg in reversed(prior_transcript):
            if msg.get("role") == "assistant":
                last_counselor_message = str(msg.get("content", "")).strip()
                break

        session_recaps = (
            list(public_memory.session_recaps)
            if public_memory is not None
            else list(normalized_client_state.get("session_recaps", []))
        )
        last_homework = (
            list(public_memory.last_homework)
            if public_memory is not None
            else list(normalized_client_state.get("homework_history", []))
        )
        modality_profile_text = (
            json.dumps(case.theory_info, ensure_ascii=False, indent=2)
            if case.theory_info
            else _localized_empty(output_language, "Unknown", "Desconhecido")
        )

        if self._env is None:
            return self._render_client_dialogue_localized_fallback(
                intake_profile=intake_profile,
                session_index=session_index,
                session_recaps=session_recaps,
                last_homework=last_homework,
                modality_profile_text=modality_profile_text,
                last_counselor_message=last_counselor_message,
                output_language=output_language,
            )

        return self.render_template(
            "client/dialogue.jinja2",
            modality=case.modality,
            session_index=session_index,
            intake_profile=intake_profile,
            session_recaps=session_recaps,
            last_homework=last_homework,
            modality_profile_text=modality_profile_text,
            last_counselor_message=last_counselor_message,
            client_state=normalized_client_state,
            prior_transcript=prior_transcript,
            output_language=output_language,
        )

    def _render_client_dialogue_localized_fallback(
        self,
        *,
        intake_profile: Dict[str, Any],
        session_index: int,
        session_recaps: list[dict[str, Any]],
        last_homework: list[str],
        modality_profile_text: str,
        last_counselor_message: str,
        output_language: str,
    ) -> str:
        info = intake_profile.get("static_traits", {})
        if not isinstance(info, dict):
            info = {}

        portuguese = "portugu" in output_language.lower() or output_language.lower().startswith("pt")
        if portuguese:
            labels = {
                "name": "Nome", "age": "Idade", "gender": "Gênero", "occupation": "Ocupação",
                "education": "Escolaridade", "marital": "Estado civil", "family": "Situação familiar",
                "social": "Relações sociais", "medical": "Histórico médico", "language": "Características de linguagem",
                "problem": "Queixa principal", "topic": "Tema do aconselhamento", "needs": "Necessidades principais",
            }
            instructions = [
                "Mantenha a resposta coerente com o perfil, o histórico e as preocupações atuais.",
                "Retome assuntos anteriores com naturalidade; não se apresente como se fosse o primeiro encontro.",
                "Quando faltarem informações, diga que não tem certeza. Não invente detalhes sem relação com o caso.",
                "Não fale como um profissional recitando um livro-texto de psicologia.",
            ]
            style = [
                f"Use linguagem natural, cotidiana e conversacional em {output_language}.",
                "Use de 2 a 4 frases por turno e prefira frases curtas.",
                "Evite jargão clínico, resumos sistemáticos sobre si e linguagem de relatório.",
                "Compartilhe informações aos poucos; não revele todas as preocupações profundas de uma vez.",
                "Você pode responder diretamente ou mencionar uma experiência relevante.",
            ]
            interaction = [
                "Você geralmente participa, mas não precisa cooperar perfeitamente.",
                "Em assuntos sensíveis, pode hesitar, minimizar, responder vagamente, evitar o tema ou questionar se a abordagem ajuda.",
                "Suas emoções não melhoram em linha reta; lembranças ou comentários podem mudar seu humor.",
                "Reaja com sinceridade: pode sentir-se compreendido, confuso, discordar, querer continuar ou preferir não falar.",
                "Você pode se desviar um pouco do assunto se houver relação emocional com suas preocupações.",
            ]
            limits = [
                "Fale somente como cliente; não narre ações, expressões faciais ou pensamentos internos.",
                "Não use metacomentários como 'como cliente', 'com base no perfil' ou 'eu deveria'.",
                "Não fale pelo terapeuta e não produza JSON, XML, listas ou explicações.",
            ]
            section_titles = {
                "background": "Contexto", "concerns": "Preocupações e objetivos", "growth": "Experiências de vida",
                "profile": "Perfil adicional relevante", "history": "Sessões anteriores", "homework": "Tarefas anteriores",
                "last_message": "Última fala do terapeuta", "consistency": "Consistência", "speaking": "Estilo de fala",
                "interaction": "Estilo de interação", "limits": "Limites", "session": "Sessão", "summary": "Resumo",
            }
            unknown = "Não informado"
            no_history = "(Sem histórico de sessões anteriores)"
            no_homework = "(Nenhuma)"
            no_last_message = "(Nenhuma)"
            final_instruction = f"Responda naturalmente ao que o terapeuta acabou de dizer, em {output_language}."
        else:
            labels = {
                "name": "Name", "age": "Age", "gender": "Gender", "occupation": "Occupation",
                "education": "Education", "marital": "Marital status", "family": "Family situation",
                "social": "Social relationships", "medical": "Medical history", "language": "Language characteristics",
                "problem": "Main concern", "topic": "Counseling topic", "needs": "Core needs",
            }
            instructions = [
                "Stay consistent with the profile, history, and current concerns.",
                "Refer to previous topics naturally; do not reintroduce yourself as if this were a first meeting.",
                "When information is missing, say you are unsure. Do not invent unrelated details.",
                "Do not sound like a professional reciting a psychology textbook.",
            ]
            style = [
                f"Use natural, everyday, conversational {output_language}.",
                "Use 2–4 sentences per turn and prefer short sentences.",
                "Avoid clinical jargon, systematic self-summaries, and report-like language.",
                "Disclose information gradually; do not reveal every deeper concern at once.",
                "You may answer directly or share a relevant experience.",
            ]
            interaction = [
                "You are generally willing to participate, but do not need to be perfectly cooperative.",
                "On sensitive topics, you may hesitate, minimize, answer vaguely, avoid the topic, or question whether an approach helps.",
                "Your emotions do not improve in a straight line; memories or comments may shift your mood.",
                "React honestly: you may feel understood, confused, disagree, want to continue, or prefer not to discuss something.",
                "You may briefly go off topic if it remains emotionally connected to your concerns.",
            ]
            limits = [
                "Speak only as the client; do not narrate actions, facial expressions, or inner thoughts.",
                "Do not use meta-statements such as 'as the client', 'based on the profile', or 'I should'.",
                "Do not speak for the counselor or output JSON, XML, bullets, or explanations.",
            ]
            section_titles = {
                "background": "Background", "concerns": "Current concerns and goals", "growth": "Life experiences",
                "profile": "Relevant additional profile", "history": "Previous sessions", "homework": "Previous homework",
                "last_message": "Counselor's latest message", "consistency": "Consistency", "speaking": "Speaking style",
                "interaction": "Interaction style", "limits": "Limits", "session": "Session", "summary": "Summary",
            }
            unknown = "Unknown"
            no_history = "(No previous session history)"
            no_homework = "(None)"
            no_last_message = "(None)"
            final_instruction = f"Respond naturally to what the counselor just said, in {output_language}."

        def value(key: str) -> str:
            raw = info.get(key)
            return str(raw).strip() if raw is not None and str(raw).strip() else unknown

        growth = intake_profile.get("growth_experiences") or []
        growth_text = "\n".join(f"- {item}" for item in growth) if growth else f"- {unknown}"
        history = "\n".join(
            f"[{section_titles['session']} {index}]\n- {section_titles['summary']}: {item.get('summary') or unknown}"
            for index, item in enumerate(session_recaps, start=1)
        ) or no_history
        homework = "\n".join(f"- {item}" for item in last_homework) or no_homework
        last_message = last_counselor_message or no_last_message
        basic_fields = (
            (labels["name"], value("name")), (labels["age"], value("age")),
            (labels["gender"], value("gender")), (labels["occupation"], value("occupation")),
            (labels["education"], value("educational_background")), (labels["marital"], value("marital_status")),
            (labels["family"], value("family_status")), (labels["social"], value("social_status")),
            (labels["medical"], value("medical_history")), (labels["language"], value("language_features")),
        )
        basic_text = "\n".join(f"- {label}: {item}" for label, item in basic_fields)
        concern_fields = (
            (labels["problem"], intake_profile.get("main_problem") or unknown),
            (labels["topic"], intake_profile.get("topic") or unknown),
            (labels["needs"], intake_profile.get("core_demands") or unknown),
        )
        concern_text = "\n".join(f"- {label}: {item}" for label, item in concern_fields)
        identity = (
            f"Você é um cliente real de aconselhamento chamado {value('name')}, não uma IA."
            if portuguese
            else f"You are a real counseling client named {value('name')}, not an AI."
        )
        first_person = (
            "Fale sempre em primeira pessoa e produza somente o que diria diretamente ao terapeuta."
            if portuguese
            else "Always speak in the first person and output only what you would say directly to the counselor."
        )
        session_text = (
            f"Esta é a sessão {session_index}." if portuguese else f"This is session {session_index}."
        )
        sections = [
            identity,
            first_person,
            session_text,
            f"[{section_titles['background']}]\n{basic_text}",
            f"[{section_titles['concerns']}]\n{concern_text}",
            f"[{section_titles['growth']}]\n{growth_text}",
            f"[{section_titles['profile']}]\n{modality_profile_text}",
            f"[{section_titles['history']}]\n{history}",
            f"[{section_titles['homework']}]\n{homework}",
            f"[{section_titles['last_message']}]\n{last_message}",
            f"[{section_titles['consistency']}]\n" + "\n".join(f"{index}. {text}" for index, text in enumerate(instructions, 1)),
            f"[{section_titles['speaking']}]\n" + "\n".join(f"{index}. {text}" for index, text in enumerate(style, 1)),
            f"[{section_titles['interaction']}]\n" + "\n".join(f"{index}. {text}" for index, text in enumerate(interaction, 1)),
            f"[{section_titles['limits']}]\n" + "\n".join(f"{index}. {text}" for index, text in enumerate(limits, 1)),
            final_instruction,
        ]
        return "\n\n".join(sections)


def _simple_render(template: str, values: Dict[str, Any]) -> str:
    pattern = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")

    def _repl(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in values:
            raise KeyError(f"missing template variable: {key}")
        return str(values[key])

    return pattern.sub(_repl, template)


def _normalize_therapy_name(modality: str, output_language: str = "English") -> str:
    key = modality.strip().lower()
    is_portuguese = "portugu" in output_language.lower() or output_language.lower().startswith("pt")
    names = {
        "cbt": ("Cognitive Behavioral Therapy (CBT)", "Terapia Cognitivo-Comportamental (TCC)"),
        "act": ("Acceptance and Commitment Therapy (ACT)", "Terapia de Aceitação e Compromisso (ACT)"),
        "dbt": ("Dialectical Behavior Therapy (DBT)", "Terapia Comportamental Dialética (DBT)"),
        "psychodynamic": ("Psychodynamic Therapy", "Terapia Psicodinâmica"),
    }
    if key not in names:
        return modality
    return names[key][1 if is_portuguese else 0]


def _localized_empty(language: str, english: str, portuguese: str) -> str:
    normalized_language = language.lower()
    if "portugu" in normalized_language or normalized_language.startswith("pt"):
        return portuguese
    return english
