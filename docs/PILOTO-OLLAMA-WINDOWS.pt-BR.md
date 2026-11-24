# Piloto técnico local no Windows

Somente dados sintéticos. Não é atendimento clínico, produto homologado ou implantação pública. A autenticação e a proteção de dados ainda não são adequadas para informações reais.

Requisitos: Python 3.12, ambiente virtual e dependências web instalados, Node/npm, Ollama ativo e os modelos `phi4-mini:3.8b` e `nomic-embed-text` disponíveis em `ollama list`. Não é necessária chave para Ollama HTTP em loopback. As configurações em `configs/baselines/ollama_local.yaml` e `configs/runtime/ollama_local.yaml` não substituem as configurações originais.

Em PowerShell, a partir da raiz deste worktree, escolha portas livres e crie um diretório para o SQLite isolado:

```powershell
Set-Location D:\projetos\psicoia-localization-reconciled
New-Item -ItemType Directory -Force "$env:TEMP\psicoia-pilot" | Out-Null
$env:DB_URL = 'sqlite:///' + ("$env:TEMP\psicoia-pilot\pilot.db" -replace '\\','/')
$env:PSYCHAGENT_WEB_BASELINE_CONFIG = 'configs/baselines/ollama_local.yaml'
$env:PSYCHAGENT_WEB_RUNTIME_CONFIG = 'configs/runtime/ollama_local.yaml'
.\src\web\.venv\Scripts\python.exe -m uvicorn main:app --app-dir src/web --host 127.0.0.1 --port 8001
```

Em outro PowerShell:

```powershell
Set-Location D:\projetos\psicoia-localization-reconciled\src\web
$env:VITE_API_BASE = 'http://127.0.0.1:8001'
npm run dev -- --host 127.0.0.1 --port 5174 --strictPort
```

Abra `http://127.0.0.1:5174`; a saúde do backend está em `http://127.0.0.1:8001/health`. Se as portas estiverem ocupadas, escolha outras e ajuste `VITE_API_BASE`. O arquivo SQLite indicado é persistente; preserve-o para testar reinício e não compartilhe dados privados.

Os embeddings locais são calculados sob demanda e mantidos em memória para não sobrescrever os catálogos. Na primeira solicitação de uma abordagem/etapa pode haver espera de minutos e o cálculo se repete após reiniciar o backend. A qualidade dos modelos e a relevância das habilidades ainda não foram validadas clinicamente. Trocar de idioma ou abordagem exige testes adicionais. O serviço local de IA sem autenticação é aceito somente via HTTP loopback; não exponha o Ollama ou a aplicação na rede.
