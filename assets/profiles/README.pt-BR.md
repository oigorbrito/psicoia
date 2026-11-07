# `assets/profiles/`

Este diretório contém fixtures sintéticas mínimas para testes dos fluxos nas modalidades disponíveis. Elas podem ser usadas por `src/sample` e `src/rft` por meio da configuração de datasets. Não são perfis de clientes reais, evidência clínica nem casos clinicamente equivalentes.

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
