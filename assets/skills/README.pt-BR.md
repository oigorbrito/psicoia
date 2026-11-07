# Localização do catálogo de habilidades do PsychAgent

Os catálogos de habilidades ficam em `sect/<approach>/stageN/`. Os arquivos `meta_skills.json` e `micro_skills.json` sem sufixo de idioma continuam sendo os catálogos de origem e servem como alternativa quando não há um catálogo localizado.

## Nomes dos arquivos por idioma

Para um catálogo localizado, mantenha a mesma estrutura JSON e adicione o sufixo do idioma antes de `.json`:

- `meta_skills.en.json` / `micro_skills.en.json`
- `meta_skills.pt-BR.json` / `micro_skills.pt-BR.json`

O carregador seleciona o idioma correspondente a `output_language`. A cobertura de localização é independente para cada etapa e catálogo; arquivos localizados ausentes continuam usando o catálogo de origem.

## Dados e invariantes dos embeddings

- Mantenha as chaves do catálogo e os valores de `skill_id`, `parent_ids` e `sect` exatamente iguais aos dados de origem.
- Traduza os campos legíveis por pessoas (`skill_name`, `skill_description`, `when_to_use` e `trigger`, quando presentes) sem alterar o sentido ou o escopo clínico da habilidade.
- Não altere o cache de origem `micro_skills.pt` para armazenar texto traduzido ou embeddings traduzidos.
- Os embeddings dependem do texto da habilidade e do modelo/provedor de embeddings. Um catálogo localizado deve usar seu próprio cache `micro_skills.<locale>.pt`. Se esse cache não existir ou sua impressão digital SHA-256 não corresponder ao catálogo e à configuração de embeddings, o runtime recalculará os embeddings a partir do JSON localizado e os gravará no cache específico daquele idioma.
- Não afirme que a recuperação de habilidades é equivalente entre idiomas sem avaliar sua qualidade.

Catálogos sem arquivos localizados não são considerados traduzidos: usam o conteúdo de origem até que as traduções sejam revisadas e adicionadas.

## Validação

Execute `python scripts/validate_skill_catalog_locales.py --locale en` ou `python scripts/validate_skill_catalog_locales.py --locale pt-BR` para exigir cobertura completa e validar as chaves do catálogo, os IDs, os relacionamentos e caracteres Han não traduzidos. Durante a localização, adicione `--allow-missing` para informar a cobertura atual e ainda validar todos os arquivos de idioma existentes.
