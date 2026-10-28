# `prompts/`

This directory contains the prompt assets used by the project, including Jinja2 templates and plain-text scoring prompts. Prompts are part of runtime behavior. They are loaded by:

- `src/sample/core/prompt_manager.py`
- `src/sample/prompt_manager.py`
- `src/sample/skill_manager.py`
- `src/eval/utils.py`

## Prompt groups

- Generation prompts: client simulation, counselor dialogue, summaries, and profile updates.
- Skill prompts: skill selection and rewriting when the skill library is enabled.
- Evaluation prompts: standardized scoring instructions for scales and metrics.

### `public/`

Shared prompts used by `src/sample/core/prompt_manager.py`: `counselor_system.jinja2`, `session_opening.jinja2`, and `public_recap.jinja2`. They define shared context such as background information, conversation history, homework review, and session openings.

### `client/`

`dialogue.jinja2` is the client simulator's core template, called by `ClientSimulator.generate_client_utterance()`. It includes `intake_profile`, conversation history, prior homework, and the counselor's most recent utterance.

### `psychagent/`

Prompts used directly by `sample` and `rft`, organized under `bt/`, `cbt/`, `het/`, `pdt/`, `pmt/`, and `skill/`. Modality prompt directories use this structure:

```text
<modality>/
  counsel/system.jinja2
  summary/system.jinja2
  summary/user.jinja2
  profile/system.jinja2
  profile/user.jinja2
```

The paths and filenames are read directly by `src/sample/prompt_manager.py`. Counseling prompts commonly require `<think>` and `<response>` sections; `src/sample/runner.py` extracts `<response>` for the transcript. Skill prompts under `skill/select_skill/` and `skill/rewrite/` are loaded by `src/sample/skill_manager.py`.

### `eval/`

Scoring prompts for `src.eval`, usually stored as `prompts/eval/<method_name>/<prompt_name>.txt`, for example `ctrs/collaboration.txt`, `miti/empathy.txt`, `psc/transference.txt`, and `tes/warmth.txt`. Some prompts, such as `human_vs_llm_eval.txt`, are directly in `prompts/eval/`; `src/eval/utils.py::load_prompt()` supports both layouts.

## Compatibility and safe editing

Prompt directory structure and filenames are referenced by code and should not be changed casually. Preserve Jinja placeholders, output tags, and expected formats. Translating a prompt can affect model behavior, so treat prompt translation as a separately scoped change and validate it explicitly. Skill prompt files exist in the repository, but the example runtime disables skill-library loading by default.

## Suggested reading order

1. Read `public/counselor_system.jinja2` and `client/dialogue.jinja2`.
2. Inspect the counseling, summary, and profile prompts for one modality.
3. Compare evaluation prompts with their implementations in `src/eval/methods/`.
