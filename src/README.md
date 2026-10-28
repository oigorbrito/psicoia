# Source code guide (`src/`)

This guide describes the code entry points, module boundaries, and suggested reading order. The root [`../README.md`](../README.md) provides a high-level overview.

## Modules and execution flow

- `sample/`: generates multi-session counseling dialogues.
- `eval/`: evaluates scales and metrics.
- `rft/`: selects best-of-n trajectories using rollouts and rewards.
- `shared/`: shared path, file, and YAML utilities.

The overall flow is:

1. `sample` reads cases from `assets/profiles` and writes `course.json` and `session_*.json`.
2. `eval` evaluates standard cases or adapts `sample` outputs for evaluation.
3. `rft` reuses `sample` for multiple rollouts and `eval.reward` for reward-based selection.
4. `shared` provides common infrastructure.

## `sample/`

Entry points: `sample/__main__.py` and `sample/main.py`.

Useful files:

- `sample/main.py`: CLI arguments, configuration loading, and runner initialization.
- `sample/runner.py`: case concurrency, session dialogue, summary/profile updates, output persistence, and resume behavior.
- `sample/io/dataset_loader.py`: case discovery and validation.
- `sample/io/store.py`: output layout, including `save_root/<baseline>/<modality>/<case_id>/session_*.json` and `course.json`.
- `sample/core/prompt_manager.py`: loads `prompts/public/` and `prompts/client/`.
- `sample/prompt_manager.py`: loads `prompts/psychagent/<modality>/...`.
- `sample/client/simulator.py`: client simulator.
- `sample/skill_manager.py`: skill retrieval, used when the skill library is enabled.
- `sample/models.py`: summary/profile schemas by modality.

The two prompt managers load different prompt directories.

## `eval/`

Entry points: `eval/__main__.py` and `eval/main.py`.

- `eval/main.py`: CLI arguments and runtime configuration.
- `eval/manager/evaluation_orchestrator.py`: case discovery, session orchestration, method concurrency, and result aggregation.
- `eval/io/input_adapter.py`: adapts between `eval_case` and `sample` outputs.
- `eval/reward.py`: programmatic reward interface reused by `rft`.
- `eval/methods/`: evaluation registry and implementations, grouped into `client/`, `counselor/`, and root-level methods such as `rro.py`.

Evaluation methods commonly load scoring prompts from `prompts/eval/` and reuse JSON output repair logic from `core/base.py`.

## `rft/`

Entry points: `rft/__main__.py` and `rft/main.py`.

- `rft/main.py`: loads baseline, sample runtime, dataset, and RFT runtime.
- `rft/runner.py`: extends `sample.runner.PsychAgentRunner` to add rollout and reward selection at the session level.
- `rft/reward.py`: aggregates rewards and computes scores.

Compare `sample/runner.py` and `rft/runner.py` to understand their boundary.

## `shared/`

- `shared/file_utils.py`: `project_root()`, safe filenames, and JSON writing utilities.
- `shared/config_utils.py`: YAML loading with a lightweight fallback when `PyYAML` is unavailable.

## Relationships and notes

- `configs/` supplies configuration to module entry points.
- `prompts/` contains prompt assets loaded by `sample`, `rft`, and `eval`.
- `data/` and `assets/` provide evaluation and generation inputs.
- Tests, when available, provide an executable reference for expected behavior.

Run the modules with `python -m src.<module>`. `rft` explicitly reuses `sample` and `eval`; it is not an independent stack. Several evaluation methods use Pydantic v2 APIs such as `ConfigDict` and `model_validate()`.
