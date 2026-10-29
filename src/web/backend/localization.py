"""Brazilian Portuguese operational messages for the web API.

Technical field names, status codes, identifiers, and persisted values are kept
outside this presentation catalogue.
"""

from __future__ import annotations

from typing import Any

DEFAULT_OUTPUT_LANGUAGE = "Português (Brasil)"

PT_BR_SCHOOL_NAMES = {
    "behavioral": "Terapia comportamental (BT)",
    "cbt": "Terapia cognitivo-comportamental (CBT)",
    "humanistic": "Terapia humanista-existencial (HET)",
    "psychodynamic": "Terapia psicodinâmica (PDT)",
    "postmodern": "Terapia pós-moderna (PMT)",
}

PT_BR_MESSAGES = {
    "auth_missing_token": "Token de acesso não informado.",
    "auth_invalid_token": "Token de acesso inválido.",
    "auth_user_not_found": "Usuário não encontrado.",
    "auth_user_exists": "Este nome de usuário já está em uso.",
    "auth_invalid_credentials": "Nome de usuário ou senha incorretos.",
    "course_not_found": "Percurso não encontrado.",
    "visit_not_found": "Sessão não encontrada.",
    "access_forbidden": "Acesso não autorizado.",
    "school_not_found": "Abordagem não encontrada.",
    "unsupported_school": "A abordagem selecionada não está disponível.",
    "course_create_failed": "Não foi possível criar o percurso. Tente novamente.",
    "course_close_visit_first": "Encerre a sessão atual antes de concluir o percurso.",
    "course_archive_incomplete": "Somente percursos concluídos podem ser arquivados.",
    "visit_course_inactive": "Só é possível iniciar uma sessão em um percurso em andamento.",
    "visit_already_open": "Este percurso já tem uma sessão em andamento.",
    "visit_already_closed": "Esta sessão já foi encerrada.",
    "visit_closed_cannot_send": "Esta sessão foi encerrada e não aceita novas mensagens.",
    "visit_opening_failed": "Não foi possível preparar a abertura da sessão. Tente novamente.",
    "model_call_failed": "Não foi possível gerar uma resposta. Tente novamente.",
    "model_empty_response": "O serviço de geração retornou uma resposta vazia. Tente novamente.",
    "validation_required": "Este campo é obrigatório.",
    "validation_invalid": "Os dados informados são inválidos.",
    "validation_type": "O tipo de dado informado não é válido.",
    "validation_too_short": "O valor informado é menor que o mínimo permitido.",
    "validation_too_long": "O valor informado excede o limite permitido.",
    "validation_out_of_range": "O valor informado está fora do intervalo permitido.",
    "validation_choice": "O valor informado não corresponde a uma opção válida.",
    "validation_json": "O corpo da solicitação contém JSON inválido.",
}


def message(key: str, **values: Any) -> str:
    """Return a localized operational message, formatting only known placeholders."""
    template = PT_BR_MESSAGES.get(key, PT_BR_MESSAGES["validation_invalid"])
    return template.format(**values)


def school_display_name(school_id: str) -> str:
    return PT_BR_SCHOOL_NAMES.get(school_id, school_id)


def structured_output_contract(output_language: str) -> str:
    if output_language == "Português (Brasil)":
        return (
            "Escreva em português brasileiro todos os valores textuais destinados à pessoa usuária. "
            "Preserve sem alterações as chaves JSON e os valores enumerados explicitamente."
        )
    if output_language == "English":
        return "Write all free-text string values in English. Preserve JSON keys and explicitly enumerated values exactly."
    return f"Write all free-text string values in {output_language}. Preserve JSON keys and explicitly enumerated values exactly."


def output_language_or_default(output_language: str | None) -> str:
    return output_language or DEFAULT_OUTPUT_LANGUAGE


def validation_message(error_type: str) -> str:
    if error_type == "missing":
        return message("validation_required")
    if error_type in {"string_too_short", "too_short"}:
        return message("validation_too_short")
    if error_type in {"string_too_long", "too_long"}:
        return message("validation_too_long")
    if error_type in {"greater_than_equal", "greater_than", "less_than_equal", "less_than"}:
        return message("validation_out_of_range")
    if error_type in {"literal_error", "enum"}:
        return message("validation_choice")
    if error_type in {"json_invalid", "value_error.jsondecode"}:
        return message("validation_json")
    if error_type.endswith("_type") or error_type in {"string_type", "int_type", "bool_type"}:
        return message("validation_type")
    return message("validation_invalid")
