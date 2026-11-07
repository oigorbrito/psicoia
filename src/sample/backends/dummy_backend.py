"""Dummy backend for dry-run and tests."""

from __future__ import annotations

import asyncio
from typing import List

from .base import Message


class DummyBackend:
    """Deterministic text backend that can emit an end token."""

    def __init__(self, *, default_end_after_turn: int = 2) -> None:
        self._default_end_after_turn = default_end_after_turn

    async def chat_text(self, messages: List[Message], **kwargs: object) -> str:
        await asyncio.sleep(0)
        end_after_turn = int(kwargs.get("dummy_end_after_turn", self._default_end_after_turn))
        end_token = str(kwargs.get("end_token", "</end>"))
        output_language = str(kwargs.get("output_language", "English"))
        normalized_language = output_language.strip().lower().replace("_", "-")
        is_brazilian_portuguese = normalized_language.startswith("pt") or "portugu" in normalized_language
        if messages:
            system_text = str(messages[0].get("content", ""))
            if "client simulator" in system_text.lower():
                if is_brazilian_portuguese:
                    return "Ainda fico ansioso e me culpo pelo que aconteceu no abrigo. Sua pergunta me ajuda a continuar falando."
                return (
                    "I still get anxious and self-critical about what happened at the shelter. "
                    "Your question helps me keep talking."
                )
            if "shared summarizer" in system_text.lower():
                if is_brazilian_portuguese:
                    return (
                        '{'
                        '"summary":"A sessão abordou as dificuldades atuais da pessoa atendida e um próximo passo prático.",'
                        '"homework":["Registre uma situação que despertou emoções nesta semana e anote os pensamentos e sentimentos associados."],'
                        '"static_traits":{}'
                        '}'
                    )
                return (
                    '{'
                    '"summary":"The session focused on current distress and a practical next step.",'
                    '"homework":["Track one trigger this week and note thoughts and feelings."],'
                    '"static_traits":{}'
                    '}'
                )

        counselor_turn = sum(1 for m in messages if m.get("role") == "assistant") + 1
        last_user = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user = msg.get("content", "")
                break

        # Opening generation path: avoid echoing meta task instructions.
        if counselor_turn == 1 and "session opening" in last_user.lower():
            if is_brazilian_portuguese:
                return "Que bom receber você. Antes de começarmos, gostaria de ouvir o que tem sido mais difícil ultimamente. Também podemos definir juntos um pequeno foco para hoje."
            return (
                "Welcome. Before we start, I'd like to hear what has felt most difficult lately, "
                "and we can set one small focus for today."
            )

        if counselor_turn >= end_after_turn:
            if is_brazilian_portuguese:
                return f"Percebo que você tem se esforçado. Vamos encerrar por hoje. {end_token}"
            return f"I hear your progress. Let's pause here for today. {end_token}"

        clipped = last_user.replace("\n", " ")[:140]
        if is_brazilian_portuguese:
            return f"Obrigado por compartilhar. Ouvi você mencionar: “{clipped}”. Podemos pensar juntos em um passo concreto para esta semana."
        return f"Thanks for sharing. I heard: '{clipped}'. Let's explore one concrete coping step for this week."
