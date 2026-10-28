# `configs/`

This guide explains which configuration files are used by `sample`, `eval`, and `rft`, and where to adjust settings.

## Configuration by workflow

```text
sample: baseline + runtime + dataset
eval: runtime
rft: baseline + runtime + dataset + RFT runtime
```

The root [`../README.md`](../README.md) contains commands for getting started. Use this guide when changing parameters, endpoints, dataset size, or configuration boundaries.

## `sample`

A typical run reads:

- [`baselines/psychagent_sglang_local.yaml`](baselines/psychagent_sglang_local.yaml)
- [`runtime/psychagent_sglang_local.yaml`](runtime/psychagent_sglang_local.yaml)
- [`datasets/profiles_sample.yaml`](datasets/profiles_sample.yaml) or another dataset YAML

`baseline` controls the counselor model endpoint and generation parameters, including `backend`, `model`, `base_url`, `api_key_env`, `temperature`, `max_tokens`, `max_sessions`, `max_counselor_turns`, and `end_token`.

`runtime` controls execution, including `concurrency`, `resume`, `overwrite`, `save_dir`, `output_language`, client simulator settings (`client_*`), session and skill retrieval settings (`psychagent_*`), and embedding settings (`psychagent_embedding_*`).

In this integration candidate, the upstream sample prompts/defaults remain Chinese. The local PT-BR/English response-language implementation is pending separate review and is not included. Do not treat the presence of `output_language` in config as proof that PT-BR localization is enabled.

`dataset` selects cases using settings such as `root_data_path`, `supported_modalities`, `split`, `max_cases`, `max_cases_per_modality`, `case_selection_strategy`, and `filename_sort_policy`.

Common changes: edit `baselines/*.yaml` to switch model services, the runtime YAML to adjust upstream execution settings, and `datasets/*.yaml` to switch or limit data. Changes to output-language behavior remain outside this literal-copy candidate.

## `eval`

Evaluation uses [`runtime/eval_default.yaml`](runtime/eval_default.yaml). It controls input/output paths, input format, evaluation endpoint, concurrency, resume/overwrite behavior, case limits, supported modalities, and method mapping. CLI options such as `--input-format`, `--data-root`, `--output-root`, and `--modalities` can override YAML values for a run.

## `rft`

`rft` reuses the three `sample` configuration types and adds [`runtime/rft_default.yaml`](runtime/rft_default.yaml). This runtime controls rollout count and concurrency, reward concurrency and endpoint (`reward_api_*`), transcript retention, and reward method mapping. Configure `reward_api_*` to use a separate reward evaluator endpoint.

## Example files

- `baselines/psychagent_sglang_local.yaml`: counselor model connection.
- `datasets/profiles_sample.yaml` and `datasets/profiles_rft.yaml`: datasets based on bundled profiles.
- `datasets/psycheval.yaml` and `datasets/psycheval_bt_cbt_het_pdt_pmt.yaml`: `PsychEval` dataset configurations.
- `runtime/psychagent_sglang_local.yaml`: main runtime shared by `sample` and `rft`.
- `runtime/eval_default.yaml`: evaluation runtime.
- `runtime/rft_default.yaml`: rollout and reward settings.

## Paths and parsing

Relative paths in `datasets/*.yaml` are resolved relative to the configuration file's directory, not the current shell directory. `sample` and `rft` dataset YAML files are parsed by [`../src/sample/io/config_loader.py`](../src/sample/io/config_loader.py) and passed to [`../src/sample/io/dataset_loader.py`](../src/sample/io/dataset_loader.py). Evaluation runtime YAML is parsed and validated by [`../src/eval/core/schemas.py`](../src/eval/core/schemas.py).

## Suggested reading order

1. Read [`../README.md`](../README.md) for the main commands.
2. For `sample`, inspect the baseline, runtime, and dataset files used by your run.
3. For `eval`, inspect `runtime/eval_default.yaml`.
4. For `rft`, also inspect `runtime/rft_default.yaml` and `datasets/profiles_rft.yaml`.
