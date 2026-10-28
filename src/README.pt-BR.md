# Guia do código-fonte (`src/`)

Este guia descreve os pontos de entrada do código, os limites entre módulos e uma ordem recomendada de leitura. O [README principal](../README.pt-BR.md) apresenta o projeto em alto nível.

## Módulos e fluxo de execução

- `sample/`: gera diálogos de aconselhamento em múltiplas sessões.
- `eval/`: avalia escalas e métricas.
- `rft/`: seleciona as melhores trajetórias (*best-of-n*) usando rollouts e recompensas.
- `shared/`: utilitários compartilhados para caminhos, arquivos e YAML.

O fluxo geral é:

1. `sample` lê casos de `assets/profiles` e grava `course.json` e `session_*.json`.
2. `eval` avalia casos padrão ou adapta resultados de `sample` para avaliação.
3. `rft` reutiliza `sample` para vários rollouts e `eval.reward` para seleção baseada em recompensa.
4. `shared` fornece infraestrutura comum.

## `sample/`

Pontos de entrada: `sample/__main__.py` e `sample/main.py`.

Arquivos úteis:

- `sample/main.py`: argumentos da CLI, carregamento da configuração e inicialização do runner.
- `sample/runner.py`: concorrência entre casos, diálogo das sessões, atualização de resumos/perfis, persistência dos resultados e retomada da execução.
- `sample/io/dataset_loader.py`: descoberta e validação de casos.
- `sample/io/store.py`: organização dos resultados, incluindo `save_root/<baseline>/<modality>/<case_id>/session_*.json` e `course.json`.
- `sample/core/prompt_manager.py`: carrega `prompts/public/` e `prompts/client/`.
- `sample/prompt_manager.py`: carrega `prompts/psychagent/<modality>/...`.
- `sample/client/simulator.py`: simulador de clientes.
- `sample/skill_manager.py`: recuperação de habilidades, usada quando a biblioteca de habilidades está habilitada.
- `sample/models.py`: esquemas de resumo/perfil por modalidade.

Os dois gerenciadores de prompts carregam diretórios diferentes.

## `eval/`

Pontos de entrada: `eval/__main__.py` e `eval/main.py`.

- `eval/main.py`: argumentos da CLI e configuração de execução.
- `eval/manager/evaluation_orchestrator.py`: descoberta de casos, orquestração de sessões, concorrência dos métodos e agregação de resultados.
- `eval/io/input_adapter.py`: adapta dados entre `eval_case` e resultados de `sample`.
- `eval/reward.py`: interface programática de recompensa reutilizada por `rft`.
- `eval/methods/`: registro e implementações de avaliação, organizados em `client/`, `counselor/` e métodos no diretório raiz, como `rro.py`.

Os métodos de avaliação normalmente carregam prompts de pontuação em `prompts/eval/` e reutilizam a lógica de reparo de saída JSON de `core/base.py`.

## `rft/`

Pontos de entrada: `rft/__main__.py` e `rft/main.py`.

- `rft/main.py`: carrega as configurações baseline, runtime de sample, dataset e runtime de RFT.
- `rft/runner.py`: estende `sample.runner.PsychAgentRunner` para adicionar rollouts e seleção por recompensa no nível da sessão.
- `rft/reward.py`: agrega recompensas e calcula pontuações.

Compare `sample/runner.py` e `rft/runner.py` para entender os limites entre os dois módulos.

## `shared/`

- `shared/file_utils.py`: `project_root()`, nomes de arquivo seguros e utilitários para gravação JSON.
- `shared/config_utils.py`: carregamento de YAML com uma alternativa leve quando `PyYAML` não está disponível.

## Relações e observações

- `configs/` fornece configurações aos pontos de entrada dos módulos.
- `prompts/` contém recursos de prompt carregados por `sample`, `rft` e `eval`.
- `data/` e `assets/` fornecem entradas para avaliação e geração.
- Testes, quando disponíveis, servem como referência executável do comportamento esperado.

Execute os módulos com `python -m src.<module>`. `rft` reutiliza explicitamente `sample` e `eval`; não é uma pilha independente. Vários métodos de avaliação usam APIs do Pydantic v2, como `ConfigDict` e `model_validate()`.
