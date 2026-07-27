# Auditoria final da epic 16

Auditoria executada em 2026-07-27.

## Escopo

- Base anterior à epic: `eb07ea5596c148b7b79aaf4bc5927f42196fbeef`.
- Último merge de publicação auditado: `6d7dd76845c830365bd700953382aea12e0e0329`.
- 96 caminhos alterados pela epic.
- 52 perfis auditados: 51 novos e 1 atualizado.
- 152 perfis e 152 entradas únicas em cada um dos três índices.

## Comandos principais

```powershell
git diff --check eb07ea5596c148b7b79aaf4bc5927f42196fbeef..HEAD
python tools/research/validate.py --base-ref origin/main
python tools/research/generate_indexes.py --check
python -m unittest discover -s tools/research/tests -v
```

Os quatro tipos de JSONL foram validados linha a linha com
`jsonschema.Draft202012Validator` e `FormatChecker`, usando os schemas em
`research/epic-16/schemas/`. A auditoria de links usou GET concorrente com 24
workers, redirects habilitados, User-Agent explícito e timeout de 18 segundos.
Falhas foram repetidas individualmente com `curl.exe`, timeout de 30 segundos e
User-Agent de navegador.

## Correções realizadas

### Schemas

Quatro valores de `finding` em `issue-26/evidence.jsonl` não pertenciam ao enum
do schema. Eles foram normalizados para `confirmado` ou `não divulgado`,
preservando as limitações e o contexto nos respectivos campos `summary`.

Resultado após a correção: 1.359 registros dos quatro tipos de JSONL, em 36
arquivos, com zero erro de schema.

### Estágios

Dez campos de estágio foram normalizados para o vocabulário definido em
`contributing.md`. Os campos sem uma etapa pública precisa passaram a usar
`Not publicly disclosed`. EDP Ventures passou a usar
`Seed, Series A, and Series B`, e Ahead Ventures passou a usar
`Series B and Growth` no campo de follow-on.

As quatro linhas afetadas nos índices, Açolab Ventures, Eurofarma Ventures,
IN3 e EDP Ventures, foram sincronizadas nos três idiomas.

### Links de perfis

- O link Finep que retornava 404 foi removido de FIP Nordeste Capital Semente
  e substituído pelo site oficial ativo do fundo em Triaxis Capital.
- O hostname de homologação `qas-brasil` de Açolab Ventures foi substituído
  pela página pública da ArcelorMittal Brasil, que respondeu HTTP 200.

Não restou link quebrado confirmado nos perfis publicados pela epic.

## Auditoria de links

Foram verificadas 475 URLs únicas em 1.145 ocorrências:

- 348 responderam 2xx diretamente;
- 56 chegaram a 2xx após redirect;
- 49 foram bloqueadas por 401, 403, 429 ou WAF e não foram classificadas como
  quebradas;
- 5 responderam 404;
- 4 responderam 5xx;
- 2 mantiveram timeout;
- 11 mantiveram falha de DNS, TLS ou conexão.

Os 404, 5xx, timeouts e falhas de conexão remanescentes estão apenas nos
artefatos de pesquisa congelados. Eles incluem páginas da Bradesco Asset,
Finep e Procomer; páginas da Eqwow e um relatório da SLC Agrícola; além de
URLs em `manutara.ventures`, `sulventures.com.br`, `endeavor.org.ec`,
`mific.gob.ni`, `cvca.law`, `inbusiness.com.br`, `jupter.co`, `senprende.hn`,
`spectrainvest.com`, `wulaiaconsultoria.com.br`, `genialgestao.com.br` e
`pronacom.org`.

Decisão: preservar essas URLs nos inventários e evidências, pois registram a
proveniência pública e a data de acesso da pesquisa. A indisponibilidade
posterior da fonte foi documentada e não altera as decisões sustentadas por
outras evidências congeladas. Esses links não são fontes ativas dos perfis
publicados.

## Integridade e proveniência

- 52 de 52 perfis possuem os 14 campos obrigatórios, as quatro seções, ao menos
  uma fonte HTTP(S) e `Last verified`.
- Todos os tipos de fundo pertencem à lista permitida.
- Os três READMEs têm 152 entradas, os mesmos caminhos e a mesma ordem.
- Todos os 152 caminhos indexados existem; não há perfil ausente, órfão ou
  repetido.
- UTF-8 estrito, mojibake e caracteres de controle: zero ocorrência real nos
  arquivos alterados.
- Referências entre candidatos, evidências, fontes e perfis canônicos estão
  resolvidas.
- Não existe perfil novo inelegível, elegível sem publicação ou pendência,
  colisão entre `funds/` e `ecosystem/`, nem uso do arquivo local de startups.
- Lightrock e IMPAQTO são as duas não publicações explícitas registradas na
  issue #28.
- O domínio de Fundepar aparece em Arapy e Fundepar por uma relação intencional
  entre veículo e gestora, documentada nos perfis e na consolidação.

## Dívida preexistente

A auditoria separou na issue #59 os 23 perfis cuja localização já era
incompatível com a regra geográfica atual antes da epic, além da inversão
alfabética preexistente na seção Peru. Esses itens não foram introduzidos nem
agravados pela epic e não alteram seus resultados.

## Resultado

Após as correções, não existe inconsistência crítica ou alta atribuível à epic.
Validator, sincronização dos índices, 17 testes, schemas, UTF-8 e
`git diff --check` passam.

O validator não deve ser executado contra o intervalo acumulado inteiro para
testar o limite de lote: esse intervalo contém 51 perfis adicionados por vários
PRs. Cada PR de publicação foi validado separadamente e ficou limitado a, no
máximo, 10 investidores.
