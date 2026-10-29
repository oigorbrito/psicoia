"""Operational language directives appended to existing prompt contracts."""


def output_language_instruction(output_language: str, audience: str) -> str:
    if "中" in output_language or output_language.lower().startswith("zh"):
        if audience == "client":
            return "请只用中文，以第一人称输出来访者的自然口语回应，不要添加模拟话语以外的内容。"
        return "请只用中文撰写面向来访者的下一段回应，并保留已指定的标记和输出格式。"
    if output_language == "Português (Brasil)":

        if audience == "client":
            return (
                "INSTRUÇÃO FINAL DE IDIOMA: Responda somente em português brasileiro, em primeira pessoa, "
                "e não acrescente conteúdo fora da fala simulada."
            )
        return (
            "INSTRUÇÃO FINAL DE IDIOMA: Escreva a próxima resposta destinada à pessoa usuária somente "
            "em português brasileiro. Preserve os marcadores e o formato de saída já especificados."
        )
    if output_language == "English":
        if audience == "client":
            return (
                "FINAL LANGUAGE INSTRUCTION: Respond only in English, in the first person, and do not add "
                "content outside the simulated utterance."
            )
        return (
            "FINAL LANGUAGE INSTRUCTION: Write the next client-facing response only in English. Preserve "
            "the markers and output format already specified."
        )
    return f"Respond only in {output_language} and preserve the specified output format."
