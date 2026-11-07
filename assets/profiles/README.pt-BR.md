# `assets/profiles/`

Este diretório armazena arquivos de perfil de clientes para diferentes modalidades de aconselhamento psicológico. Eles podem ser usados por `src/sample` e `src/rft` por meio da configuração de datasets.

A estrutura de diretórios segue a convenção de `DatasetLoader`:

```text
profiles/
  bt/sample/*.json
  bt/rft/*.json
  cbt/sample/*.json
  cbt/rft/*.json
  ...
```

- `sample/`: divisão de perfis usada por `src/sample`.
- `rft/`: divisão de perfis usada por `src/rft`.
- Atualmente, somente as divisões `sample` e `rft` estão organizadas aqui; as divisões históricas `dev` e `rl` não foram incluídas no diretório oficial de recursos `v0402`.

Configurações recomendadas:

- [`../../configs/datasets/profiles_sample.yaml`](../../configs/datasets/profiles_sample.yaml)
- [`../../configs/datasets/profiles_rft.yaml`](../../configs/datasets/profiles_rft.yaml)
