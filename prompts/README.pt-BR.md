# Prompts

Este diretório contém templates Jinja2 e prompts de avaliação em texto puro. Os prompts são parte do comportamento de execução, não apenas documentação. São carregados por `src/sample/core/prompt_manager.py`, `src/sample/prompt_manager.py`, `src/sample/skill_manager.py` e `src/eval/utils.py`.

## Categorias

- `public/`: contexto compartilhado, abertura de sessão e recapitulação.
- `client/dialogue.jinja2`: entrada principal do simulador de clientes. Recebe perfil inicial, resumo histórico, tarefa anterior e fala recente do terapeuta.
- `psychagent/`: prompts de geração e resumo para `bt/`, `cbt/`, `het/`, `pdt/`, `pmt/` e `skill/`.
- `eval/`: prompts de pontuação por método, normalmente organizados como `prompts/eval/<method_name>/<prompt_name>.txt`.

Os templates por modalidade usam uma estrutura como:

```text
<modality>/
  counsel/system.jinja2
  summary/system.jinja2
  summary/user.jinja2
  profile/system.jinja2
  profile/user.jinja2
```

## Contratos e cuidados

Os caminhos e nomes de arquivo são usados diretamente pelo código; renomeá-los pode interromper a execução. Alguns prompts de aconselhamento requerem `<think>` e `<response>`, e o runner extrai `<response>` para o transcript. O loader de avaliação também aceita arquivos diretamente em `prompts/eval/`.

Não altere nomes de arquivos, placeholders Jinja, tags de saída ou formato esperado como parte de uma tradução. A tradução de prompts pode alterar o comportamento do modelo; trate-a como uma mudança separada e valide-a explicitamente. A existência de prompts de habilidades não significa que o carregamento da biblioteca de habilidades esteja ativado por padrão.

## Leitura recomendada

1. Leia `public/counselor_system.jinja2` e `client/dialogue.jinja2`.
2. Compare os prompts `counsel`, `summary` e `profile` de uma modalidade.
3. Consulte `src/eval/methods/` junto com os prompts de avaliação correspondentes.
