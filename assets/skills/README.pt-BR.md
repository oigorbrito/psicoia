# Estado dos idiomas do catálogo de habilidades — parcial e sensível ao comportamento

Os catálogos de habilidades são entradas de recuperação derivadas da pesquisa, não simples textos de interface. Os arquivos sem sufixo `meta_skills.json` e `micro_skills.json` continuam sendo os catálogos de origem. O carregador por idioma usa um arquivo lateral disponível para o idioma selecionado e mantém o catálogo de origem quando não existe arquivo localizado; catálogos localizados ausentes são registrados em log. A falta de tradução não é considerada tradução concluída.

## Cobertura estrutural atual

- Português brasileiro: 16 de 30 arquivos de catálogo; 1.233 de 5.158 registros.
- Inglês: 8 de 30 arquivos de catálogo; 141 de 5.158 registros.

Esses números descrevem somente a cobertura de arquivos/registros. Não comprovam qualidade da tradução, equivalência clínica, qualidade da recuperação ou paridade entre idiomas. O validador estrito continua apontando catálogos ausentes.

## Nomes de arquivos e invariantes

Arquivos localizados mantêm a estrutura JSON e acrescentam o sufixo do idioma antes de `.json`, por exemplo `meta_skills.en.json` e `meta_skills.pt-BR.json`.

- Preserve exatamente as chaves do catálogo e os valores `skill_id`, `parent_ids` e `sect`.
- Não modifique catálogos de origem nem traduza conteúdo clínico/de benchmark como limpeza incidental.
- Campos legíveis por pessoas exigem proveniência/autorização verificadas e revisão adequada de tradução e conteúdo clínico antes de qualquer tradução ou uso adicional.
- Embeddings dependem do texto do catálogo e do modelo/provedor. Um catálogo localizado não pode reutilizar embeddings do idioma de origem; qualquer cache por idioma exige geração e invalidação próprias, validadas.
- Não afirme equivalência de recuperação entre idiomas sem avaliação específica.

## Validação

Execute `python scripts/validate_skill_catalog_locales.py --locale pt-BR --allow-missing` e o comando correspondente com `--locale en` para inspecionar a cobertura estrutural. O validador estrito falha enquanto houver catálogos ausentes. O validador não avalia qualidade da tradução nem validade clínica. Consulte [`../../LOCALIZATION.pt-BR.md`](../../LOCALIZATION.pt-BR.md) para o estado e as limitações atuais.
