# Fontes e afirmações externas

Este arquivo separa referências externas de evidência específica do repositório.

## Referências usadas pelo modelo de controles

- OpenSSF OSPS Baseline 2026.08.28: https://baseline.openssf.org/versions/2026-08-28
- OpenSSF Scorecard: https://github.com/ossf/scorecard
- NIST SSDF: https://csrc.nist.gov/projects/ssdf
- DORA capabilities: https://dora.dev/capabilities/

A referência a um padrão ou projeto externo não implica adoção integral, certificação ou conformidade. Os controles do harness são adaptações locais e devem ser descritos como tais.

## Evidência do projeto

Afirmações sobre comandos, componentes e testes devem apontar para arquivos versionados ou execução reproduzível. Afirmações sobre GitHub, releases publicados, usuários, mantenedores e implantação precisam de consulta externa autoritativa; a árvore local, isoladamente, não as comprova.

## Proveniência e licenças verificadas no Block 17

- Repositório upstream PsychAgent: <https://github.com/ECNU-ICALK/PsychAgent>. Consulta somente leitura de `main` em 2026-10-30 retornou `469f45ef468b968b3fccd1936d7e6a0a574e4c5c`; o inventário local e os limites dessa observação estão em [`../PSICOIA_BLOCK17_PROVENANCE_RESULT.md`](../PSICOIA_BLOCK17_PROVENANCE_RESULT.md).
- Artigo associado: <https://arxiv.org/abs/2604.00931>. A página oficial exibia link para CC BY 4.0 (<https://creativecommons.org/licenses/by/4.0/>); isso não é licença do código ou dos demais arquivos do repositório.
- Metadados oficiais consultados para versões Python fixadas: <https://pypi.org/pypi/fastapi/0.110.2/json>, <https://pypi.org/pypi/httpx/0.27.0/json>, <https://pypi.org/pypi/sqlmodel/0.0.21/json> e <https://pypi.org/pypi/uvicorn/0.30.1/json>. As demais dependências não têm resolução completa versionada.
- Licenças npm foram lidas dos campos do `src/web/package-lock.json`; isso é um inventário local, não uma avaliação de compatibilidade ou de obrigações de distribuição.
