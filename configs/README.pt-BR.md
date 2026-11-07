# Configurações

Este guia indica quais configurações usar nos fluxos `sample`, `eval` e `rft`, e onde ajustar parâmetros sem alterar o código.

## Configurações por fluxo

```text
sample: baseline + runtime + dataset
eval: runtime
rft: baseline + runtime + dataset + RFT runtime
```

### `sample`

Exemplo típico:

- [`baselines/psychagent_sglang_local.yaml`](baselines/psychagent_sglang_local.yaml)
- [`runtime/psychagent_sglang_local.yaml`](runtime/psychagent_sglang_local.yaml)
- [`datasets/profiles_sample.yaml`](datasets/profiles_sample.yaml)

`baseline` define endpoint e parâmetros do modelo, como `backend`, `model`, `base_url`, `api_key_env`, `temperature` e `max_tokens`. `runtime` controla execução, como `concurrency`, `resume`, `overwrite`, `save_dir`, `output_language` e opções `client_*` e `psychagent_*`. `dataset` determina os casos de entrada, por meio de opções como `root_data_path`, `supported_modalities`, `split` e limites de casos.

No fluxo `sample`, a instrução inicial e os objetivos padrão da sessão estão disponíveis em `English` e `Português (Brasil)`. O idioma configurado também é enviado ao prompt do conselheiro; inglês é o padrão.

Para trocar o serviço do modelo, ajuste `baselines/*.yaml`; para alterar idioma de saída ou comportamento de execução, ajuste o runtime; para trocar ou limitar os dados, ajuste `datasets/*.yaml`.

### `eval`

A avaliação usa o runtime [`runtime/eval_default.yaml`](runtime/eval_default.yaml), que controla caminhos (`data_root`, `output_root`), formato de entrada, endpoint, concorrência, retomada e métodos/modalidades. Opções de linha de comando como `--input-format`, `--data-root`, `--output-root` e `--modalities` podem substituir valores do YAML numa execução.

### `rft`

`rft` reutiliza as configurações de `sample` e acrescenta [`runtime/rft_default.yaml`](runtime/rft_default.yaml), que define quantidade e concorrência de rollouts, endpoint de recompensa, métodos e política de retenção de resultados. Para separar o avaliador de recompensa do endpoint principal, configure `reward_api_*` nesse arquivo.

## Arquivos de exemplo

- `baselines/psychagent_sglang_local.yaml`: conexão do modelo de aconselhamento.
- `datasets/profiles_sample.yaml` e `datasets/profiles_rft.yaml`: datasets baseados nos perfis incluídos.
- `datasets/psycheval.yaml` e `datasets/psycheval_bt_cbt_het_pdt_pmt.yaml`: configurações do benchmark `PsychEval`.
- `runtime/psychagent_sglang_local.yaml`: runtime compartilhado por `sample` e `rft`.
- `runtime/eval_default.yaml`: runtime de avaliação.
- `runtime/rft_default.yaml`: opções de rollout e recompensa.

## Caminhos e validação

Caminhos relativos nos YAML de dataset são resolvidos em relação ao diretório do arquivo de configuração. `sample` e `rft` carregam datasets por `src/sample/io/config_loader.py` e `src/sample/io/dataset_loader.py`; o schema de avaliação fica em `src/eval/core/schemas.py`.

## Ordem de leitura recomendada

1. Consulte o [README principal](../README.md) para os comandos de execução.
2. Para `sample`, examine baseline, runtime e dataset correspondentes.
3. Para `eval`, examine `runtime/eval_default.yaml`.
4. Para `rft`, examine `runtime/rft_default.yaml` e `datasets/profiles_rft.yaml`.
