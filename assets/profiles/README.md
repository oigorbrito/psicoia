# `assets/profiles/`

This directory contains minimal synthetic smoke-test fixtures for the supported counseling modalities. They can be used by `src/sample` and `src/rft` through dataset configuration. They are not real client profiles, clinical evidence, or clinically equivalent cases.

The directory structure follows the `DatasetLoader` convention:

```text
profiles/
  bt/sample/*.json
  bt/rft/*.json
  cbt/sample/*.json
  cbt/rft/*.json
  ...
```

- `sample/`: profile split used by `src/sample`.
- `rft/`: profile split used by `src/rft`.
- Only the `sample` and `rft` splits are currently organized here; historical `dev` and `rl` splits were not included in the formal `v0402` asset directory.

Recommended configurations:

- [`../../configs/datasets/profiles_sample.yaml`](../../configs/datasets/profiles_sample.yaml)
- [`../../configs/datasets/profiles_rft.yaml`](../../configs/datasets/profiles_rft.yaml)
