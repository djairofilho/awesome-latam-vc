# Worker 210 — alocadores institucionais

Este shard registra a auditoria não-CVM de divulgações públicas de alocadores institucionais para fundos com atuação potencial no Brasil. A data de corte é **2026-07-30**. Todos os candidatos permanecem em `researching`, com `decision: null`; a decisão pertence à validação final da issue #210.

## Estratégia auditável

Foram executadas duas passagens com vocabulário independente:

1. **Passagem por produto e mandato:** combinações de `Brazil`, `venture capital fund`, `startup fund`, `equity investment`, `commitment` e `project disclosure`, restritas a IFC, IDB Invest, IDB Lab e DFC.
2. **Passagem por processo de alocação:** combinações de `anchor investor`, `first close`, `limited partner`, `manager selection`, `call for venture capital funds` e `institutional investor`, incluindo EIB e uma nova leitura transversal das fontes anteriores.

Os resultados encontrados por busca foram aceitos como evidência apenas quando levavam a páginas oficiais do próprio alocador. Não houve consulta à CVM, leitura do arquivo local de startups ou decisão final de elegibilidade.

## Deduplicação e aliases

Cada nome foi comparado com:

- `research/epic-207/baseline/catalog-baseline.jsonl`;
- `research/epic-207/baseline/identity-index.jsonl`;
- `research/epic-207/baseline/prior-sources.jsonl`.

Canary, Valor Capital Group, Monashees, SP Ventures e Quona Capital têm `canonical_profile` no baseline. Os nomes dos veículos e gestores revelados pelos alocadores foram preservados em `aliases` e IDs separados, sem criar decisão de duplicidade nesta etapa.

Good Karma e DNA Capital não tiveram correspondência nominal no baseline e são as duas lacunas potenciais. Nenhum dos dois está pronto para publicação: ainda faltam domínio/site oficial, deduplicação por identidade e confirmação de recorrência; para DNA Capital também é necessário confirmar o fechamento posterior à aprovação da DFC.

## Cobertura e limitações

- 12 fontes inventariadas: 8 novas completas, 1 nova parcial e 3 benchmarks congelados.
- 7 candidatos: 2 potenciais lacunas e 5 sobreposições com perfis existentes.
- 7 registros de evidência oficial de alocadores.
- O mapa interativo da DFC retornou uma superfície sem resultados estáveis no HTML. A lacuna ficou explícita e não foi tratada como evidência de ausência.
- A divulgação do EIB sobre Quona confirma América Latina, mas não nomeia o Brasil.
- A ficha IFC de Monashees tem última atualização anterior à janela de 24 meses.
- A chamada contínua do IDB Lab explica critérios e processo, mas não divulga propostas em diligência.

BNDES, Finep e Sebrae foram mantidos somente como benchmark/delta por seus IDs prévios. Suas páginas não foram reabertas nem usadas para gerar novos candidatos.

## Arquivos

- `source-inventory.jsonl`: fontes, escopo percorrido e limitações.
- `candidates.jsonl`: identidades encontradas e estado pré-decisão.
- `evidence.jsonl`: claims com localizador e resumo.
- `coverage-matrix.jsonl`: cobertura das duas passagens.

## Validação

A validação deste shard deve verificar cada linha contra os quatro schemas correspondentes em `research/epic-207/schemas/`, unicidade dos IDs, referências entre arquivos, UTF-8 e ausência de artefatos de mojibake. O validador agregado da epic não é executado diretamente sobre este diretório porque ele exige os artefatos de consolidação que estão fora do escopo do worker.
