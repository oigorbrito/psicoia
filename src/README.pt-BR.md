# Guia do código-fonte (`src/`)

O código está organizado em quatro módulos principais:

- `sample/`: geração de diálogos de aconselhamento em múltiplas sessões.
- `eval/`: avaliação de escalas e métricas.
- `rft/`: seleção de trajetórias best-of-n baseada em rollouts e recompensas.
- `shared/`: utilitários de caminhos, arquivos e YAML compartilhados.

## Fluxo geral

1. `sample` lê casos em `assets/profiles` e gera `course.json` e `session_*.json`.
2. `eval` avalia casos ou adapta resultados de `sample` para avaliação.
3. `rft` reutiliza `sample` para gerar rollouts e `eval.reward` para calcular recompensas e selecionar resultados.
4. `shared` fornece utilitários comuns.

## Arquivos de entrada e leitura

### `sample`

Entradas: `sample/__main__.py` e `sample/main.py`. A execução principal está em `sample/runner.py`; descoberta de dados em `sample/io/dataset_loader.py`; persistência em `sample/io/store.py`; simulação do cliente em `sample/client/simulator.py`; recuperação de habilidades em `sample/skill_manager.py`. Os gerenciadores de prompts em `sample/core/prompt_manager.py` e `sample/prompt_manager.py` carregam diretórios de prompts diferentes.

### `eval`

Entradas: `eval/__main__.py` e `eval/main.py`. A orquestração está em `eval/manager/evaluation_orchestrator.py`, a adaptação de entradas em `eval/io/input_adapter.py`, e a interface de recompensa reutilizada por `rft` em `eval/reward.py`. Os métodos ficam em `eval/methods/client/`, `eval/methods/counselor/` e no nível raiz de `eval/methods/`.

### `rft`

Entradas: `rft/__main__.py` e `rft/main.py`. `rft/runner.py` estende `sample.runner.PsychAgentRunner` para incorporar rollouts e seleção por recompensa; `rft/reward.py` agrega e calcula pontuações.

### `shared`

`shared/file_utils.py` oferece utilitários de raiz do projeto, nomes de arquivo e gravação JSON. `shared/config_utils.py` carrega YAML e mantém uma alternativa leve quando `PyYAML` não está disponível.

## Relação com outros diretórios

- `configs/`: parâmetros lidos pelas entradas dos módulos.
- `prompts/`: templates carregados por `sample`, `rft` e `eval`.
- `data/` e `assets/`: entradas para avaliação e geração.
- `tests/`: referência executável para o comportamento esperado, quando disponível.

Os três módulos podem ser executados com `python -m src.<module>`. `rft` reutiliza explicitamente partes de `sample` e `eval`; não é uma stack independente.
