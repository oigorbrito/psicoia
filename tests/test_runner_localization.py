from src.sample.runner import get_default_session_focus, get_opening_instruction


def test_session_focus_is_localized_for_english_and_brazilian_portuguese():
    english = get_default_session_focus("English")
    portuguese = get_default_session_focus("pt-BR")

    assert len(english) == len(portuguese) == 7
    assert "Establish rapport" in english[0]
    assert "Estabelecer vínculo" in portuguese[0]
    assert all(not any("\u3400" <= char <= "\u9fff" for char in text) for text in english + portuguese)


def test_session_focus_defaults_to_english_and_returns_fresh_lists_for_unknown_locales():
    first = get_default_session_focus("English")
    second = get_default_session_focus("unsupported-locale")

    assert len(first) == len(second) == 7
    assert first == second
    first.clear()
    assert len(get_default_session_focus("English")) == 7


def test_opening_instruction_uses_requested_language():
    assert get_opening_instruction(3, "English") == "This is session 3."
    assert get_opening_instruction(3, "Português (Brasil)") == "Esta é a sessão 3."
    assert get_opening_instruction(3, "unsupported-locale") == "This is session 3."
