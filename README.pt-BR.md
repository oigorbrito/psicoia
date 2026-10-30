# PsicoIA

**PsicoIA — projeto local de software baseado na pesquisa PsychAgent**

[README em inglês](README.md)

PsicoIA é a identidade canônica deste repositório de software local. Seu código de pesquisa para aconselhamento em múltiplas sessões deriva do projeto PsychAgent; atribuição upstream, referências acadêmicas, identificadores de compatibilidade e caminhos técnicos são preservados. A apresentação de software não clínico auditada está localizada em PT-BR e inglês; catálogos e conteúdo clínicos protegidos permanecem parciais e não são apresentados como validados.

Artigo: [PDF](paper/PsychAgent.pdf) | [arXiv 2604.00931](https://arxiv.org/abs/2604.00931)
Modelo: [ecnu-icalk/PsychAgent-Qwen3-32B](https://huggingface.co/ecnu-icalk/PsychAgent-Qwen3-32B)

## Visão geral

Este repositório é o projeto PsicoIA e contém um snapshot local de código baseado na base de pesquisa PsychAgent. Ele inclui fluxos para:

- geração de diálogos em múltiplas sessões;
- avaliação de métricas do lado do terapeuta e do cliente;
- seleção de rollouts best-of-n orientada por recompensa;
- prompts, configurações, recursos do artigo e dados mínimos de exemplo.

A versão atual permite executar os fluxos públicos de geração, avaliação e RFT. Os recursos completos de treinamento em escala do artigo e o fluxo completo de evolução de habilidades pós-sessão não estão incluídos.

## Como o projeto de pesquisa PsychAgent funciona

A arquitetura descrita pela pesquisa PsychAgent se organiza em três componentes práticos:

- **Memória e planejamento** mantêm a continuidade entre sessões, para que sessões posteriores se apoiem nas anteriores em vez de recomeçar do zero.
- **Recuperação de habilidades** disponibiliza habilidades explícitas de aconselhamento durante a interação.
- **Rollouts orientados por recompensa** geram várias trajetórias candidatas e selecionam as melhores para etapas posteriores.

No código, esses componentes correspondem a:

- [`src/sample/`](src/sample/) para geração em múltiplas sessões;
- [`src/eval/`](src/eval/) para avaliação e métricas relacionadas a recompensas;
- [`src/rft/`](src/rft/) para rollouts best-of-n e seleção por recompensa.

## Estrutura do repositório

- [`paper/`](paper/): PDF do artigo e figuras usadas no README;
- [`configs/`](configs/): configurações de baseline, datasets, avaliação e RFT;
- [`assets/profiles/`](assets/profiles/): perfis incluídos usados por `sample` e `rft`;
- [`assets/skills/`](assets/skills/): biblioteca de habilidades; consulte o [guia de localização do catálogo em PT-BR](assets/skills/README.pt-BR.md);
- [`data/eval/`](data/eval/): exemplos de avaliação no formato nativo;
- [`prompts/`](prompts/): prompts públicos, de cliente, do PsychAgent e de avaliação;
- [`src/sample/`](src/sample/): fluxo de geração em múltiplas sessões;
- [`src/eval/`](src/eval/): orquestração de avaliação e implementações de métricas;
- [`src/rft/`](src/rft/): geração de rollouts e seleção baseada em recompensa;
- [`src/web/`](src/web/): espaço web para demonstração e interação local;
- [`src/shared/`](src/shared/): utilitários compartilhados para YAML e arquivos.

Para começar, consulte [`src/README.pt-BR.md`](src/README.pt-BR.md), com os principais pontos de entrada do código, e [`configs/README.pt-BR.md`](configs/README.pt-BR.md), sobre as responsabilidades das configurações. Antes de alterar conteúdo localizado, leia a [política e o estado da localização](LOCALIZATION.pt-BR.md).

## Instalação

O repositório PsicoIA ainda não inclui um arquivo de ambiente com versões fixadas. A instalação abaixo é um ponto de partida para a versão pública atual:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install openai httpx jinja2 pydantic PyYAML aiolimiter tenacity pytest
```

- Recomenda-se Python **3.10 ou superior**.
- Instale `torch` somente se precisar carregar ou preencher a biblioteca de habilidades usando embeddings.
- As configurações incluídas apontam para endpoints internos compatíveis com OpenAI. Substitua-os pelas configurações do seu serviço antes de executar.
- O checkpoint lançado está disponível no Hugging Face: [ecnu-icalk/PsychAgent-Qwen3-32B](https://huggingface.co/ecnu-icalk/PsychAgent-Qwen3-32B).

## Variáveis de ambiente necessárias

Os exemplos padrão usam algumas variáveis de ambiente:

- `SGLANG_API_KEY`: chave do backend do terapeuta, usada nos exemplos de `sample` e RFT;
- `API_KEY`: chave do simulador de cliente em `sample`, ou chave de cliente/recompensa em RFT;
- `CHAT_API_KEY`: chave alternativa usada por `eval` e, opcionalmente, pela avaliação de recompensa;
- `CHAT_API_BASE`: URL base usada por `eval` quando não definida na configuração nem na CLI;
- `CHAT_MODEL_NAME`: substituição opcional do modelo de avaliação;
- `PSYCHAGENT_EMBEDDING_API_KEY`: necessária para a configuração atual de recuperação de habilidades.

## Início rápido

### 1. Gerar diálogos em múltiplas sessões

```bash
export SGLANG_API_KEY=your_key_here
export API_KEY=your_client_simulator_key_here

python -m src.sample \
  --mode psychagent \
  --baseline configs/baselines/psychagent_sglang_local.yaml \
  --runtime configs/runtime/psychagent_sglang_local.yaml \
  --dataset configs/datasets/profiles_sample.yaml \
  --strict-config
```

Os resultados são gravados em:

```text
sample_outputs/before_rft/<modality>/<case_id>/
```

Cada pasta de caso normalmente contém `course.json` e `session_*.json`.

### 2. Executar a avaliação

Para avaliar os exemplos incluídos:

```bash
export CHAT_API_KEY=your_eval_key_here
export CHAT_API_BASE=https://your-openai-compatible-endpoint/v1

python -m src.eval \
  --config configs/runtime/eval_default.yaml \
  --input-format auto \
  --modalities bt,cbt,het,pdt,pmt
```

Para avaliar resultados gerados por `sample`:

```bash
python -m src.eval \
  --config configs/runtime/eval_default.yaml \
  --input-format sample \
  --data-root sample_outputs/before_rft \
  --output-root data/eval_outputs_from_sample \
  --modalities cbt
```

### 3. Executar rollouts best-of-n orientados por recompensa

```bash
export SGLANG_API_KEY=your_key_here
export API_KEY=your_client_or_reward_key_here

python -m src.rft \
  --baseline configs/baselines/psychagent_sglang_local.yaml \
  --runtime configs/runtime/psychagent_sglang_local.yaml \
  --dataset configs/datasets/psycheval_bt_cbt_het_pdt_pmt.yaml \
  --rft-config configs/runtime/rft_default.yaml \
  --save_dir rft_outputs \
  --strict-config
```

Para executar `rft` com os perfis incluídos, altere `--dataset` para [`configs/datasets/profiles_rft.yaml`](configs/datasets/profiles_rft.yaml).

### 4. Experimentar o espaço web

Para experimentar no navegador o fluxo de aconselhamento em múltiplas sessões, use o espaço web em [`src/web/`](src/web/). Consulte o [guia completo de uso em PT-BR](src/web/README.pt-BR.md).

A ordem recomendada de inicialização é: implantar o serviço do modelo terapeuta, iniciar o backend web e, por fim, iniciar o frontend. Um exemplo de inicialização do serviço com `sglang`:

```bash
nohup python -m sglang.launch_server \
    --model-path /path/to/psychagent-checkpoint \
    --trust-remote-code \
    --port 30000 \
    --tp 8 \
    --host 0.0.0.0 \
    > /path/to/logs/sglang_server.log 2>&1 &
```

Atualize `base_url` em [`configs/baselines/psychagent_sglang_local.yaml`](configs/baselines/psychagent_sglang_local.yaml) para corresponder ao endpoint do serviço do modelo.

Crie um `.env.local` mínimo na raiz do projeto:

```bash
SGLANG_API_KEY=your-sglang-key
PSYCHAGENT_EMBEDDING_API_KEY=your-embedding-key
BACKEND_PORT=8000
FRONTEND_PORT=5173
BACKEND_HOST=localhost
```

Na raiz do projeto, inicie os serviços:

```bash
./run_backend.sh
./run_frontend.sh
```

Endpoints padrão:

```text
Frontend: http://localhost:5173
Backend:  http://localhost:8000
Health:   http://localhost:8000/health
```

Fluxo de uso típico:

1. entre ou cadastre-se;
2. escolha uma abordagem;
3. crie um curso;
4. inicie a sessão;
5. encerre a sessão atual para continuar na próxima.

As capturas mantidas em `paper/web/` são artefatos originais de pesquisa/demonstração upstream (incluindo os rótulos da interface de origem), não capturas da interface PsicoIA. Elas permanecem inalteradas por proveniência; nenhum logotipo ou ícone da aplicação foi substituído.

## Guia de configuração

Os três fluxos principais usam combinações distintas de configurações:

- `sample`: `baseline + runtime + dataset`;
- `eval`: `runtime`;
- `rft`: `baseline + runtime + dataset + rft-config`.

Consulte [`configs/README.pt-BR.md`](configs/README.pt-BR.md) para detalhes sobre endpoints de modelos e chaves de API, idioma de saída, concorrência e retomada, datasets e divisões, cobertura de modalidades, endpoints de recompensa e quantidade de rollouts.

## Dados e recursos incluídos

O repositório inclui uma biblioteca inicial de habilidades em [`assets/skills/sect/`](assets/skills/sect/), perfis em [`assets/profiles/`](assets/profiles/), exemplos nativos de avaliação em [`data/eval/`](data/eval/), prompts para `bt`, `cbt`, `het`, `pdt` e `pmt`, prompts e implementações de métricas compartilhadas e específicas de cada abordagem, recursos do artigo em [`paper/`](paper/) e o checkpoint lançado no Hugging Face.

Esta versão **não** inclui todos os recursos de treinamento e avaliação do `PsychEval` usados no artigo, o fluxo completo de extração e evolução de habilidades pós-sessão, uma receita completa de pós-treinamento para internalização reforçada nem um arquivo de licença do repositório.

## Recorte dos resultados

O artigo de origem avalia o PsychAgent no benchmark `PsychEval`, com múltiplas sessões e abordagens terapêuticas.

- O `PsychAgent` (Qwen3-32B) reporta `7.32 / 7.91 / 5.92 / 8.24` nas métricas compartilhada e específica do terapeuta e compartilhada e específica do cliente.
- Em relação ao `Qwen3-Max`, os ganhos reportados são `+1.44 / +0.17 / +0.51 / +0.43`.
- Em relação ao `TheraMind`, os ganhos reportados são `+1.07 / +0.97 / +0.44 / +0.41`.
- Na avaliação do artigo de origem com 522 diálogos pareados, o PsychAgent ficou em primeiro lugar tanto nas avaliações humanas quanto na avaliação por LLM Gemini-3; o QWK entre avaliadores humanos foi `0.675`.

Recursos relacionados do artigo: [`paper/radar_v1.pdf`](paper/radar_v1.pdf), [`paper/trend.pdf`](paper/trend.pdf) e [`paper/fig_11_qwk_heatmap_abc.png`](paper/fig_11_qwk_heatmap_abc.png).

## Estado do projeto

O código migrado para PsicoIA deve ser entendido como um lançamento de pesquisa, não como um pacote de produção pronto. O repositório oferece fluxos executáveis para geração, avaliação e seleção best-of-n por recompensa. Para uma disponibilização pública mais ampla, ainda são necessários, entre outros itens, uma licença do repositório, um arquivo de ambiente com versões fixadas, configurações de serviço apropriadas para uso público, notas mais completas de reprodução dos experimentos em escala do artigo e orientações mais explícitas para implantação do checkpoint.

## Citação

Página do artigo: [arXiv:2604.00931](https://arxiv.org/abs/2604.00931)

```bibtex
@misc{yang2026psychagent,
  title         = {PsychAgent: An Experience-Driven Lifelong Learning Agent for Self-Evolving Psychological Counselor},
  author        = {Yutao Yang and Junsong Li and Qianjun Pan and Jie Zhou and Kai Chen and Qin Chen and Jingyuan Zhao and Ningning Zhou and Xin Li and Liang He},
  year          = {2026},
  eprint        = {2604.00931},
  archiveprefix = {arXiv},
  primaryclass  = {cs.AI},
  url           = {https://arxiv.org/abs/2604.00931},
  doi           = {10.48550/arXiv.2604.00931}
}
```

## Aviso de segurança

- Este repositório destina-se **somente a pesquisa e experimentação**.
- Ele não substitui profissionais de saúde mental licenciados, diagnóstico médico, atendimento de emergência ou intervenção em crises.
- Uma implantação no mundo real exigiria trabalho adicional em segurança, privacidade, consentimento informado, monitoramento, encaminhamento e governança clínica.
- Se alguém estiver sob risco imediato de sofrer danos, procure serviços locais de emergência ou apoio a crises; não dependa de um sistema automatizado.

## Agradecimentos

- [`PsychEval`](configs/datasets/psycheval_bt_cbt_het_pdt_pmt.yaml), pelo benchmark e protocolo de avaliação adotados no artigo;
- ferramentas de API compatíveis com OpenAI, templates Jinja2 e validação baseada em Pydantic usados no código disponibilizado.

## Práticas do repositório

A migração copia literalmente o código upstream: não inclui correções, melhorias ou mudanças funcionais. São permitidas apenas traduções aprovadas de conteúdo voltado a pessoas para PT-BR/inglês e a marca PsicoIA em prosa de apresentação. Consulte a [política de migração e tradução](docs/MIGRATION-POLICY.pt-BR.md).

- O [roadmap de migração e localização](docs/ROADMAP.pt-BR.md) registra prioridades baseadas em evidências, sem prometer prazos.
- [Instruções para agentes](AGENTS.md) descrevem regras locais de evidência e segurança das alterações.
- O [guia de testes](docs/TESTING.md) lista comandos de verificação e seus limites.
- As [notas de maturidade](docs/MATURITY.md) e o [estado do projeto](policy/project-state.json) registram o alvo e as incógnitas conhecidas; não declaram conformidade.
- O [estado do relato de segurança](SECURITY.md) informa que um canal privado de relato ainda não foi verificado.
