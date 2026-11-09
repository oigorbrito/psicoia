# Cliente Android offline da PsicoIA

## Estado e escopo autorizado

O checkout-base era `ce74d8e29f30fae4faee56a2bd3b36b7df79cc87`. Nesse commit não havia `AndroidManifest.xml`, projeto Gradle Android, Kotlin/Java Android nem APK. Esta implementação nova fica isolada em `android/`; os fluxos web/Python existentes e os textos, IDs e hierarquias dos catálogos não foram modificados. A exceção funcional foi autorizada nesta tarefa e está registrada em `docs/ROADMAP.md` e `docs/ROADMAP.pt-BR.md`.

## Componentes PsicoIA reutilizados

- **Catálogos:** os 30 arquivos `*.pt-BR.json` de `assets/skills/sect/` são copiados sem alteração para os assets do aplicativo. A suíte verifica igualdade byte a byte, IDs e `parent_ids`: 5.158 registros (677 metahabilidades e 4.481 micro-habilidades), cinco abordagens e três etapas.
- **Taxonomia:** os códigos de abordagem (`bt`, `cbt`, `het`, `pdt`, `pmt`) e os números de etapa são preservados; a UI Android só mostra rótulos em PT-BR.
- **Não portados:** `src/sample/skill_manager.py` depende do cliente de embeddings configurado por API e de arquivos/cache Python; `src/web/backend/psychagent_engine.py` depende da stack web, dos prompts e do backend OpenAI-compatible. Nenhum deles executa inferência integral no Android. Os prompts clínicos existentes não foram copiados nem alterados.

## Comparação de implementações Android verificadas

Inspeção estática dos repositórios públicos e caminhos abaixo; presença de código não prova que os recursos foram testados neste checkout ou em um aparelho PsicoIA.

| Base e evidência consultada | Inferência offline | Embeddings | RAG/recuperação | Persistência de conversa | Decisão |
|---|---|---|---|---|---|
| [`ataraxialab/LM-playground`](https://github.com/ataraxialab/LM-playground/tree/c68b28c9e2d36d61c13ed899a63b02882db7d2d1), árvore em `c68b28c9e2d36d61c13ed899a63b02882db7d2d1` | Não verificada em Android | Não encontrado | Não encontrado | Não encontrado | O nome não identifica de forma inequívoca o projeto citado anteriormente; a árvore examinada não contém caminhos Android, embeddings, RAG ou persistência, e a API do GitHub não informa licença SPDX. Não reutilizado. |
| [`ggml-org/llama.cpp/examples/llama.android`](https://github.com/ggml-org/llama.cpp/tree/f477f795cb071baf5b8af6488378366a72034ac4/examples/llama.android), commit `f477f795cb071baf5b8af6488378366a72034ac4` | Sim: exemplo Android carrega arquivo GGUF local e gera texto pela JNI | Há suporte no projeto C++, mas o exemplo Android não expõe um pipeline de embeddings para este catálogo | Não implementado no exemplo Android | O exemplo mantém mensagens em memória | Base escolhida para inferência GGUF local e independente de API/provedor. O app PsicoIA implementa recuperação e persistência separadamente. A licença MIT permanece no submódulo e é incluída nos assets do app. |
| [`google-ai-edge/gallery`](https://github.com/google-ai-edge/gallery/tree/3972f0663b7c0a01836e9ed52acd2f6ae8b4096e/Android/src/app/src/main/java/com/google/ai/edge/gallery/services/semanticretrieval), commit `3972f0663b7c0a01836e9ed52acd2f6ae8b4096e` | Sim, runtimes locais | Sim: `services/semanticretrieval/OnDeviceEmbedder.kt` | Sim: `SemanticRetrievalService.kt` e `SqliteVectorStore` | Sim: `data/ChatSessionRepository.kt` | Implementação mais completa para as quatro capacidades, sob Apache-2.0, mas a aplicação e os runtimes LiteRT/MediaPipe são uma base extensa e específica. Não copiada para evitar acoplar este protótipo a esse runtime/modelo. |
| [`mlc-ai/mlc-llm/android/MLCChat`](https://github.com/mlc-ai/mlc-llm/tree/44fd06d04f22c87820e205b0f2b2e5e6a1f6ca85/android/MLCChat), commit `44fd06d04f22c87820e205b0f2b2e5e6a1f6ca85` | Sim, chat Android com modelos locais compilados | O repositório contém componentes de embeddings fora do app Android; integração no `MLCChat` não foi verificada | Não localizado no app Android examinado | Nenhum repositório/banco de chat identificado nos arquivos examinados | Alternativa local viável, mas com pipeline de compilação/modelos MLC; não adotada. |
| [`kumar-gautam24/playground`](https://github.com/kumar-gautam24/playground/tree/da5e16c46cd90112e7081ab74723210d3187fea6), README e árvore Android em `da5e16c46cd90112e7081ab74723210d3187fea6` | O README descreve chat offline via `flutter_gemma` | Não encontrado | Não encontrado | Não encontrado | Exemplo Flutter de chat/modelos, sem as três funções de recuperação/persistência no código examinado; metadados de licença ausentes. Não reutilizado. |

A referência anterior a “LM Playground” permanece ambígua: não tratei um repositório homônimo como base Android sem evidência. A base escolhida é o exemplo Android oficial do `llama.cpp`, cujo runtime GGUF não exige Ollama, Gemini nem endpoint remoto.

## Implementação desta branch

- **Inferência:** o app referencia `llama.cpp` como submódulo Git fixado no commit acima. O usuário seleciona um arquivo `.gguf`; o app valida a assinatura, copia-o para o armazenamento privado do aplicativo e carrega-o localmente. Não há permissão `INTERNET`, cliente HTTP ou fallback remoto.
- **Recuperação:** índice BM25 local sobre as 4.481 micro-habilidades, filtrado por abordagem e etapa. O resultado inclui a micro-habilidade e registros-meta disponíveis na sua hierarquia; esse contexto é acrescentado à mensagem enviada ao modelo. É recuperação lexical real, determinística e offline — **não é busca semântica por embeddings**.
- **Persistência:** mensagens e contexto da conversa ficam em JSON no diretório privado do app. A gravação usa arquivo temporário, `fsync` e rename atômico quando suportado. `allowBackup=false`. Isso não equivale a banco criptografado.
- **Falhas:** arquivo GGUF inválido, modelo ausente, geração vazia/exceção e falha de gravação são expostos como erros locais. A falha do modelo não produz uma resposta fictícia nem tenta outro serviço.
- **Dados incluídos:** os 5.158 registros PT-BR são empacotados byte a byte. Os arquivos de origem continuam sendo a fonte canônica; para sincronizar uma atualização aprovada, execute `python scripts/sync_android_catalog.py` e revise a comparação/testes.

## Testes e estado de validação

Executado nesta implementação:

- **PASS — build Android:** `gradlew.bat --no-daemon --max-workers=2 :app:assembleDebug`, com JDK 17.0.21, Gradle 8.14.3 e Android SDK Platform 36. Compilados os componentes Kotlin/Java e as bibliotecas nativas de `llama.cpp` para `arm64-v8a` e `x86_64`. A configuração inicial revelou `android.useAndroidX` ausente e o módulo app procurando a ferramenta de stripping no NDK padrão 27, não instalado; `android/gradle.properties` e `android/app/build.gradle.kts` agora habilitam AndroidX e alinham o NDK do app a `29.0.13113456`, permitindo stripping nativo. O aviso do parser de SDK XML v4 continuou, mas não bloqueou o build.
- **PASS — testes JVM Android:** `gradlew.bat --no-daemon --max-workers=2 :core:test :app:testDebugUnitTest`: 5 testes do core passaram; `:app:testDebugUnitTest` não tem fontes de teste (`NO-SOURCE`). Os testes cobrem os catálogos, busca BM25, filtros, contexto, persistência e falha de geração.
- **PASS — testes Python:** `python -m pytest -q`: 50 testes e 2 subtestes passaram.
- `python scripts/harness.py` foi executado na raiz do checkout. Ele registrou evidências locais limitadas (`PASS` para presença de testes, `GAP` para licença reconhecida e `UNKNOWN_EXTERNAL` para configurações externas); **não executa os testes nem confirma maturidade ou conformidade**.
- **PASS — artefato:** `aapt dump badging`, `apksigner verify` (assinatura de debug v2) e `unzip -t` passaram. O APK contém 34 bibliotecas ELF verificadas: 14 `arm64-v8a` e 20 `x86_64`. Caminho: `android/app/build/outputs/apk/debug/app-debug.apk`; tamanho: 66.483.901 bytes; SHA-256: `f02917271f0d0af80e04f2a58d512b015a66b550e1bd0410330b3747ca04a179`. É um APK debug, não uma assinatura de release.
- **NOT_RUN — testes instrumentados:** não há teste Android instrumentado executado nesta sessão.
- **NOT_RUN — aparelho:** `adb devices -l` não listou dispositivos. Não houve instalação, teste E2E físico ou instrumentado; não foi validada velocidade, memória ou compatibilidade em hardware Android.
- **NOT_RUN — importação/inferência GGUF no app:** inspeção estática confirmou o seletor local de documentos, checagem da assinatura `GGUF`, cópia para armazenamento privado e chamada ao motor nativo `llama.cpp`. O manifesto não declara `INTERNET` e não foi encontrado cliente HTTP no app/core; o fluxo projetado não depende de API paga. Um GGUF local de 776.066.240 bytes foi identificado pelo cabeçalho no cache Ollama desta máquina, mas não foi copiado nem carregado no app. Portanto, importação real, compatibilidade do modelo, geração e funcionamento offline continuam sem validação em runtime.

## Build reproduzível

Requisitos: Git com suporte a submódulos, JDK 17, Android SDK Platform 36, Build Tools 36.0.0, NDK `29.0.13113456` e CMake `3.31.6`. O usuário/desenvolvedor deve instalar o SDK e aceitar seus termos no próprio ambiente.

No PowerShell, a partir da raiz do repositório:

```powershell
git switch integration/psicoia-localization-reconciled
git submodule update --init --recursive
python scripts/sync_android_catalog.py
$env:JAVA_HOME = "C:\caminho\para\jdk-17"
$env:ANDROID_HOME = "$env:LOCALAPPDATA\Android\Sdk"
$env:ANDROID_SDK_ROOT = $env:ANDROID_HOME
Set-Location android
.\gradlew.bat --no-daemon --max-workers=2 :app:assembleDebug
.\gradlew.bat --no-daemon --max-workers=2 :core:test :app:testDebugUnitTest
```

Requisitos do SDK Manager: `platforms;android-36`, `build-tools;36.0.0`, `ndk;29.0.13113456` e `cmake;3.31.6`. O SDK desta execução foi instalado fora do repositório em `D:/projetos/psicoia-android-toolchain/android-sdk`; configure `ANDROID_HOME`/`ANDROID_SDK_ROOT` para o seu ambiente. O app declara Android 13+ (API 33) e ABIs `arm64-v8a`/`x86_64`. Para completar a validação pendente, instale o APK com `adb install -r`, importe um GGUF compatível, teste busca e resposta, desligue a rede, reabra o app e confira o histórico; repita com um arquivo inválido. Esses passos permanecem **NOT_RUN** nesta sessão.
