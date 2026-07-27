# Fila estrangeira descoberta na auditoria do Brasil

Este diretório registra o fechamento da
[#24](https://github.com/djairofilho/awesome-latam-vc/issues/24), conforme o
contrato da #17. A fila foi congelada em 2026-07-27, antes do início das
auditorias regionais #25, #26 e #27.

## Resultado final

- 15 candidatos estrangeiros consolidados a partir da fila da #18.
- 17 fontes inventariadas e concluídas: a fila de origem e 16 páginas oficiais.
- 4 candidatos com `evidência insuficiente`, encaminhados para auditoria
  regional.
- 11 candidatos `excluído` por estratégia oficialmente incompatível com o
  recorte de venture capital.
- 0 duplicatas nos diretórios `funds/regional/` e `funds/multi-country/`.
- 0 candidatos publicados.
- Nenhum candidato permaneceu sem decisão.

## Encaminhamentos

| Candidato | #25 | #26 | #27 | Motivo |
| --- | :---: | :---: | :---: | --- |
| BASF Venture Capital | sim | sim | sim | CVC global com atuação oficial na América Latina e na América do Sul; falta confirmar aderência e acesso por país. |
| Lightrock | sim | sim | sim | Estratégia de growth para América Latina, com México, Colômbia e outros mercados regionais. |
| Qualcomm Ventures | sim | sim | sim | CVC de tecnologia com equipe e portfólio ativos na América Latina; falta validar o recorte por país. |
| StepStone Group | sim | não | não | Estratégia global de venture e growth com presença comercial no México; falta comprovar investimento regional direto. |

Os demais candidatos foram excluídos da fila regional de VC:

- Actis: infraestrutura sustentável.
- Advent International: private equity.
- Blue Like an Orange Sustainable Capital: crédito privado.
- CPP Investments: investidor institucional e private equity.
- CVC Capital Partners: private equity, crédito, infraestrutura e secundários.
- KfW IPEX-Bank: financiamento de exportação e projetos.
- KKR: private equity, crédito e ativos reais.
- Lexington Partners: primários, secundários e coinvestimentos em fundos
  privados.
- Mubadala Capital: private equity e situações especiais.
- Partners Group: private markets.
- Warburg Pincus: growth private equity.

## Origem e deduplicação

A origem canônica é
[foreign-candidates.jsonl](../issue-18/foreign-candidates.jsonl), produzido
pela auditoria da #18 a partir do diretório público de membros da ABVCAP e do
PDF oficial de associados. Os identificadores dos 15 candidatos foram
preservados.

A deduplicação comparou domínio oficial normalizado, nome e aliases contra
`funds/regional/` e `funds/multi-country/`. Nenhum candidato possuía perfil
canônico nesses diretórios na data de corte. A fila também não continha
duplicatas internas.

## Decisões

Uma fonte oficial foi percorrida para cada candidato. A #24 não declara
elegibilidade e não publica perfis. Os quatro candidatos compatíveis com VC ou
growth receberam `evidência insuficiente` porque a decisão por país, a atividade
local e o acesso externo pertencem às auditorias #25, #26 e #27.

Entidades cuja estratégia oficial é private equity, crédito, infraestrutura,
financiamento de projetos, alocação em fundos ou private markets foram
marcadas como `excluído`. A exclusão vale para a fila regional de VC e não
afirma inatividade.

## Artefatos

- [candidates.jsonl](candidates.jsonl): fila canônica congelada.
- [evidence.jsonl](evidence.jsonl): evidência oficial usada na triagem.
- [source-inventory.jsonl](source-inventory.jsonl): origem e recorte das fontes.
- [run-manifest.jsonl](run-manifest.jsonl): execução das 15 revisões.

O arquivo local de startups não foi usado para descoberta, priorização,
comprovação ou decisão.
