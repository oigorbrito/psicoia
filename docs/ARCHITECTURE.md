# Arquitetura observada

**Estado: descrição inicial, baseada na árvore local; não é diagrama completo nem revisão de segurança.**

## Componentes

- `src/sample/`: geração de diálogos multi-sessão.
- `src/eval/`: orquestração e métodos de avaliação.
- `src/rft/`: rollouts e seleção orientada por recompensas, reutilizando código de `sample` e `eval`.
- `src/web/`: frontend e backend da aplicação web.
- `src/shared/`: utilitários compartilhados.
- `prompts/`, `configs/`, `assets/` e `data/`: prompts, configurações e entradas/recursos consumidos pelos fluxos.

Esta lista identifica diretórios observados; não afirma que todos os fluxos foram executados nem que suas interfaces estejam estáveis.

## Limites e integrações

Os fluxos podem depender de serviços de modelo/API configurados pelo usuário, credenciais e recursos externos. A extensão e os limites de confiança dessas integrações dependem da configuração de execução; este documento não constitui uma análise de ameaças.

Atualize este documento quando alterações materiais mudarem componentes, interfaces, persistência, dependências ou limites de confiança.
