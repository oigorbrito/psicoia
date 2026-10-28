# Harness local de evidências

O `scripts/harness.py` é um verificador pequeno e específico deste repositório. Ele não é uma implementação integral do OpenSSF OSPS, NIST SSDF ou DORA e não produz certificação, auditoria de segurança nem nível de maturidade alcançado.

## Como executar

Na raiz do repositório:

```bash
python scripts/harness.py
```

O comando carrega `policy/project-state.json`, verifica um subconjunto dos campos e relata a referência OSPS e o nível-alvo registrado. Esse nível é apenas uma meta declarada, não um resultado de avaliação.

## Verificações locais atuais

- `CONTRIBUTING.md` existe;
- há uma localização reconhecida de licença (`LICENSE`, `COPYING` ou `LICENSES`);
- existem testes Python em `tests/test_*.py`;
- existem testes da interface web em `src/web/tests/*.test.js`.

Para cada item, `PASS` significa somente que o arquivo ou conjunto de arquivos esperado foi encontrado. `GAP` significa que ele não foi encontrado. O harness não avalia a qualidade nem executa os testes. A ausência de licença é uma lacuna reportada, não uma escolha automática de licença.

O harness classifica como `UNKNOWN_EXTERNAL` configurações do GitHub, MFA, usuários ativos, releases, canal privado de relato de segurança e implantação. Esses itens exigem consulta externa autoritativa; o estado local não os comprova.

## Validação do estado e códigos de saída

O harness faz validação estrutural limitada do estado: versão de esquema e baseline, nível-alvo, valores enumerados e tipos de alguns campos. O schema completo está em `policy/project-state.schema.json`; o harness não executa um validador JSON Schema independente.

- Código `0`: o estado foi lido e os resultados foram impressos. Pode haver itens `GAP`; código zero não significa que todos passaram.
- Código `2`: o estado está ausente, não é JSON válido ou falha na validação limitada do harness.

O comando não executa pytest, testes Node, builds, validação de catálogo nem consultas à API do GitHub. Execute essas verificações separadamente conforme `docs/TESTING.md` e registre os resultados reais.

## Mudanças no harness

Quando um controle for adicionado, removido ou alterado, atualize este documento e os testes correspondentes. Cada verificação deve declarar o que observa e seus limites; evidência não consultada deve permanecer desconhecida, não ser apresentada como aprovação.
