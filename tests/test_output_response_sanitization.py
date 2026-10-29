from src.sample.backends.openai_api import OpenAIStyleBackend
from src.sample.utils import extract_public_response


def test_extracts_only_complete_response_and_hides_reasoning():
    raw = "<think>private analysis</think><response>Public answer</response>"
    assert extract_public_response(raw, "</end>") == ("Public answer", False)


def test_accepts_response_without_closing_tag_and_stops_at_internal_markup():
    assert extract_public_response("<response>Public answer", "</end>") == ("Public answer", False)
    assert extract_public_response("<response>Public answer<client_state>private", "</end>") == (
        "Public answer",
        False,
    )


def test_fails_closed_on_unclosed_reasoning_and_removes_trailing_reasoning():
    assert extract_public_response("<think") == ("", False)
    assert extract_public_response("<response>Public<skill") == ("", False)
    assert extract_public_response("<think>private reasoning") == ("", False)
    assert extract_public_response("<think>private</think>") == ("", False)
    assert extract_public_response("<think>private</think>Public answer") == ("Public answer", False)


def test_handles_end_markers_and_plain_text_provider_output():
    assert extract_public_response("<response>Finished</response></end>", "</end>") == (
        "Finished",
        True,
    )
    assert extract_public_response("<response>Finished<end>", "</end>") == (
        "Finished",
        False,
    )
    assert extract_public_response("A plain final answer") == ("A plain final answer", False)


def test_openai_compatible_reasoning_fields_and_content_blocks_are_not_returned():
    payload = {
        "choices": [
            {
                "message": {
                    "reasoning_content": "private field",
                    "content": [
                        {"type": "reasoning", "text": "private block"},
                        {"type": "text", "text": "final answer"},
                    ],
                }
            }
        ]
    }
    assert OpenAIStyleBackend._extract_text(payload) == "final answer"


def test_uses_direct_public_output_when_message_content_is_empty():
    payload = {
        "choices": [{"message": {"content": "", "reasoning_content": "private"}}],
        "output_text": "public final",
    }
    assert OpenAIStyleBackend._extract_text(payload) == "public final"


def test_untyped_text_blocks_remain_compatible():
    payload = {"choices": [{"message": {"content": [{"text": "final answer"}]}}]}
    assert OpenAIStyleBackend._extract_text(payload) == "final answer"
