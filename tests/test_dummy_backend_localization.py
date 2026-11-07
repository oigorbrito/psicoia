import json

import pytest

from src.sample.backends.dummy_backend import DummyBackend


@pytest.mark.asyncio
async def test_dummy_client_response_uses_brazilian_portuguese():
    backend = DummyBackend()
    result = await backend.chat_text(
        [{"role": "system", "content": "You are a client simulator."}],
        output_language="Português (Brasil)",
    )
    assert "Ainda fico ansioso" in result
    assert "shelter" not in result


@pytest.mark.asyncio
async def test_dummy_summary_is_localized_without_changing_json_contract():
    backend = DummyBackend()
    result = await backend.chat_text(
        [{"role": "system", "content": "You are a shared summarizer."}],
        output_language="pt-BR",
    )
    parsed = json.loads(result)
    assert set(parsed) == {"summary", "homework", "static_traits"}
    assert "A sessão" in parsed["summary"]
    assert isinstance(parsed["homework"], list)


@pytest.mark.asyncio
async def test_dummy_counselor_paths_use_brazilian_portuguese():
    backend = DummyBackend(default_end_after_turn=10)
    opening = await backend.chat_text(
        [{"role": "user", "content": "session opening"}],
        output_language="pt-BR",
    )
    ordinary = await backend.chat_text(
        [{"role": "user", "content": "Tenho me sentido ansioso."}],
        output_language="pt-BR",
    )
    closing = await backend.chat_text(
        [{"role": "user", "content": "Encerramento"}],
        output_language="pt-BR",
        dummy_end_after_turn=1,
        end_token="</end>",
    )

    assert "Que bom receber você" in opening
    assert "Obrigado por compartilhar" in ordinary
    assert "Percebo que você tem se esforçado" in closing
    assert closing.endswith("</end>")
