# `configs/`

Este guia explica quais arquivos de configuração são usados por `sample`, `eval` e `rft`, e onde ajustar as opções.

## Configuração por fluxo

```text
sample: baseline + runtime + dataset
eval: runtime
rft: baseline + runtime + dataset + rft runtime
```

O [README principal](../README.pt-BR.md) contém comandos para começar. Consulte este guia ao alterar parâmetros, endpoints, tamanho dos datasets ou limites entre configurações.

## `sample`

Uma execução típica lê:

- [`baselines/psychagent_sglang_local.yaml`](baselines/psychagent_sglang_local.yaml)
- [`runtime/psychagent_sglang_local.yaml`](runtime/psychagent_sglang_local.yaml)
- [`datasets/profiles_sample.yaml`](datasets/profiles_sample.yaml) ou outro arquivo YAML de dataset

`baseline` controla o endpoint do modelo terapeuta e os parâmetros de geração, incluindo `backend`, `model`, `base_url`, `api_key_env`, `temperature`, `max_tokens`, `max_sessions`, `max_counselor_turns` e `end_token`.

`runtime` controla a execução, incluindo `concurrency`, `resume`, `overwrite`, `save_dir`, `output_language`, configurações do simulador de clientes (`client_*`), configurações de sessão e recuperação de habilidades (`psychagent_*`) e configurações de embeddings (`psychagent_embedding_*`).

Neste candidato de integração, os prompts e padrões upstream de `sample` permanecem em chinês. A implementação local de resposta nos idiomas PT-BR/inglês está pendente de revisão separada e não foi incluída. A presença de `output_language` na configuração não significa que a localização PT-BR esteja habilitada.

`dataset` seleciona os casos por meio de opções como `root_data_path`, `supported_modalities`, `split`, `max_cases`, `max_cases_per_modality`, `case_selection_strategy` e `filename_sort_policy`.

Alterações comuns: edite `baselines/*.yaml` para trocar serviços de modelo, o YAML de runtime para ajustar a execução upstream e `datasets/*.yaml` para trocar ou limitar os dados. Mudanças no comportamento do idioma de saída permanecem fora deste candidato de cópia literal.

## `eval`

A avaliação usa [`runtime/eval_default.yaml`](runtime/eval_default.yaml). Esse arquivo controla caminhos de entrada/saída, formato de entrada, endpoint de avaliação, concorrência, retomada e sobrescrita, limites de casos, modalidades aceitas e mapeamento de métodos. Opções da CLI como `--input-format`, `--data-root`, `--output-root` e `--modalities` podem substituir valores do YAML durante uma execução.

## `rft`

`rft` reutiliza os três tipos de configuração de `sample` e acrescenta [`runtime/rft_default.yaml`](runtime/rft_default.yaml). Esse runtime controla quantidade e concorrência de rollouts, concorrência e endpoint de recompensa (`reward_api_*`), retenção de transcrições e mapeamento dos métodos de recompensa. Configure `reward_api_*` para usar um endpoint separado para o avaliador de recompensa.

## Arquivos de exemplo

- `baselines/psychagent_sglang_local.yaml`: conexão com o modelo terapeuta.
- `datasets/profiles_sample.yaml` e `datasets/profiles_rft.yaml`: datasets baseados nos perfis incluídos.
- `datasets/psycheval.yaml` e `datasets/psycheval_bt_cbt_het_pdt_pmt.yaml`: configurações do dataset `PsychEval`.
- `runtime/psychagent_sglang_local.yaml`: runtime principal compartilhado por `sample` e `rft`.
- `runtime/eval_default.yaml`: runtime de avaliação.
- `runtime/rft_default.yaml`: configurações de rollout e recompensa.

## Caminhos e análise

Caminhos relativos em `datasets/*.yaml` são resolvidos em relação ao diretório do arquivo de configuração, não ao diretório atual do shell. Os arquivos YAML de dataset de `sample` e `rft` são analisados por [`../src/sample/io/config_loader.py`](../src/sample/io/config_loader.py) e encaminhados a [`../src/sample/io/dataset_loader.py`](../src/sample/io/dataset_loader.py). O YAML de runtime da avaliação é analisado e validado por [`../src/eval/core/schemas.py`](../src/eval/core/schemas.py).

## Ordem de leitura recomendada

1. Leia o [README principal](../README.pt-BR.md) para conhecer os comandos principais.
2. Para `sample`, examine os arquivos baseline, runtime e dataset usados na execução.
3. Para `eval`, examine `runtime/eval_default.yaml`.
4. Para `rft`, examine também `runtime/rft_default.yaml` e `datasets/profiles_rft.yaml`.
