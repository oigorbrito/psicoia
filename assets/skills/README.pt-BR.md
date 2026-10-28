# Localização do catálogo de habilidades do PsychAgent — planejada, não habilitada

Os catálogos de habilidades ficam em `sect/<approach>/stageN/`. Os arquivos `meta_skills.json` e `micro_skills.json` sem sufixo de idioma continuam sendo os catálogos upstream. Neste candidato de integração, o carregador por idioma e os catálogos traduzidos não foram incluídos; as convenções abaixo descrevem trabalho pendente e não significam que a seleção por idioma esteja ativa.

## Nomes dos arquivos por idioma

Para um catálogo localizado, mantenha a mesma estrutura JSON e adicione o sufixo do idioma antes de `.json`:

- `meta_skills.en.json` / `micro_skills.en.json`
- `meta_skills.pt-BR.json` / `micro_skills.pt-BR.json`

A implementação local de carregamento por idioma está pendente. Não presuma que o carregador upstream seleciona esses arquivos por `output_language`. Se a seleção por idioma for aprovada no futuro, a cobertura deverá ser acompanhada por etapa e catálogo, com fallback explicitamente testado.

## Dados e invariantes dos embeddings

- Mantenha as chaves do catálogo e os valores de `skill_id`, `parent_ids` e `sect` exatamente iguais aos dados de origem.
- Traduza os campos legíveis por pessoas (`skill_name`, `skill_description`, `when_to_use` e `trigger`, quando presentes) sem alterar o sentido ou o escopo clínico da habilidade.
- Não altere o cache de origem `micro_skills.pt` para armazenar texto traduzido ou embeddings traduzidos.
- Os embeddings dependem do texto da habilidade e do modelo/provedor. Qualquer catálogo localizado futuro deverá usar seu próprio cache `micro_skills.<locale>.pt` e não poderá reutilizar embeddings do idioma de origem. A geração e invalidação desses caches ainda estão pendentes de integração e validação.
- Não afirme que a recuperação de habilidades é equivalente entre idiomas sem avaliar sua qualidade.

Catálogos sem arquivos localizados não são considerados traduzidos: usam o conteúdo de origem até que as traduções sejam revisadas e adicionadas.

## Validação

O validador de locale é uma ferramenta local e não foi incluído neste candidato de integração. Se o trabalho de catálogo for aprovado e adicionado, execute o validador e uma avaliação de recuperação antes de habilitar a seleção por idioma.
