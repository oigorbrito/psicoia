# Prompts

Este diretório contém os recursos de prompt usados pelo projeto, incluindo templates Jinja2 e prompts de avaliação em texto puro. Prompts fazem parte do comportamento de execução. São carregados por:

- `src/sample/core/prompt_manager.py`
- `src/sample/prompt_manager.py`
- `src/sample/skill_manager.py`
- `src/eval/utils.py`

## Grupos de prompts

- Geração: simulação de clientes, diálogo do terapeuta, resumos e atualização de perfis.
- Habilidades: seleção e reescrita de habilidades quando a biblioteca está habilitada.
- Avaliação: instruções padronizadas de pontuação para escalas e métricas.

### `public/`

Prompts compartilhados usados por `src/sample/core/prompt_manager.py`: `counselor_system.jinja2`, `session_opening.jinja2` e `public_recap.jinja2`. Eles definem contexto comum, como informações de histórico, conversas anteriores, revisão de tarefas e abertura de sessão.

### `client/`

`dialogue.jinja2` é o template principal do simulador de clientes, chamado por `ClientSimulator.generate_client_utterance()`. Ele recebe `intake_profile`, o histórico da conversa, tarefas anteriores e a fala mais recente do terapeuta.

### `psychagent/`

Prompts usados diretamente por `sample` e `rft`, organizados em `bt/`, `cbt/`, `het/`, `pdt/`, `pmt/` e `skill/`. Os diretórios de prompts por modalidade seguem esta estrutura:

```text
<modality>/
  counsel/system.jinja2
  summary/system.jinja2
  summary/user.jinja2
  profile/system.jinja2
  profile/user.jinja2
```

Os caminhos e nomes de arquivo são lidos diretamente por `src/sample/prompt_manager.py`. Prompts de aconselhamento costumam exigir as seções `<think>` e `<response>`; `src/sample/runner.py` extrai `<response>` para o transcript. Os prompts em `skill/select_skill/` e `skill/rewrite/` são carregados por `src/sample/skill_manager.py`.

### `eval/`

Prompts de pontuação usados por `src.eval`, normalmente armazenados em:

```text
prompts/eval/<method_name>/<prompt_name>.txt
```

Por exemplo: `ctrs/collaboration.txt`, `miti/empathy.txt`, `psc/transference.txt` e `tes/warmth.txt`. Alguns prompts, como `human_vs_llm_eval.txt`, ficam diretamente em `prompts/eval/`; `src/eval/utils.py::load_prompt()` aceita os dois formatos.

## Compatibilidade e edição segura

A estrutura dos diretórios e os nomes dos arquivos são referenciados pelo código e não devem ser alterados sem necessidade. Preserve placeholders Jinja, tags de saída e formatos esperados. Traduzir um prompt pode alterar o comportamento do modelo; trate isso como uma mudança de escopo separado e valide-a explicitamente. A existência de arquivos de prompt para habilidades não significa que o runtime de exemplo habilite a biblioteca por padrão.

## Leitura recomendada

1. Leia `public/counselor_system.jinja2` e `client/dialogue.jinja2`.
2. Examine os prompts de aconselhamento, resumo e perfil de uma modalidade.
3. Compare os prompts de avaliação com as implementações em `src/eval/methods/`.
