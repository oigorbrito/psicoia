import ast
from pathlib import Path

import pytest

from src.eval.core.base import EvaluationMethod


ROOT = Path(__file__).resolve().parents[1]


def _string_value(node: ast.AST) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "".join(
            part.value if isinstance(part, ast.Constant) and isinstance(part.value, str) else "{value}"
            for part in node.values
        )
    return ""


def _content_messages():
    for path in (ROOT / "src" / "eval").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Dict):
                continue
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and key.value == "content":
                    message = _string_value(value)
                    if message:
                        yield path, message


def test_evaluation_repair_messages_use_english_and_preserve_json_contracts():
    messages = list(_content_messages())
    repair_messages = [
        message
        for _, message in messages
        if message.startswith("The previous output failed format validation.")
    ]
    assert len(repair_messages) == 24
    assert all("Return only" in message and "JSON" in message for message in repair_messages)
    assert all(not any("\u3400" <= char <= "\u9fff" for char in message) for message in repair_messages)


@pytest.mark.asyncio
async def test_base_json_repair_prompt_returns_valid_object():
    class ConcreteEvaluation(EvaluationMethod):
        async def evaluate(self, gpt_api, dialogue, profile=None):
            return {}

    class FakeAPI:
        model = "test"

        def __init__(self):
            self.calls = []

        async def chat_text(self, *, messages, **kwargs):
            self.calls.append(messages)
            return "not json" if len(self.calls) == 1 else '{"items": []}'

    api = FakeAPI()
    result = await ConcreteEvaluation().chat_api(api, [])

    assert result == '{"items": []}'
    assert api.calls[1][0]["content"] == "You are a strict JSON repair assistant. Return only valid JSON object text."
