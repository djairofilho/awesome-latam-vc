# Issue 21 — fundos regionais e setoriais do Brasil

Primeira onda da matriz reproduzível `região x tese` da
[#21](https://github.com/djairofilho/awesome-latam-vc/issues/21).

## Recorte

- Data de corte e acesso: 2026-07-27.
- Regiões: Norte, Nordeste, Centro-Oeste, Sudeste fora de São Paulo e Rio de
  Janeiro, e Sul.
- Teses: IA, deep tech, climate tech, bioeconomia, agtech, healthtech, fintech
  e impacto.
- Total: 40 células.
- Executadas nesta onda: Sul/agtech, Nordeste/bioeconomia e Norte/impacto.
- Na fila: 37 células.

A matriz completa está em [coverage-matrix.jsonl](coverage-matrix.jsonl). Uma
célula em `fila` contém consultas planejadas, mas não representa pesquisa
executada nem cobertura.

## Resultado da primeira onda

| Célula | Resultado |
| --- | --- |
| Sul/agtech | Sul Ventures inclui agritech entre os setores, mas seu domínio já aparece no perfil de Primus Ventures. Cventures possui empresa agro no portfólio, sem tese agtech declarada. |
| Nordeste/bioeconomia | FIP Nordeste Capital Semente e Triaxis estão ativos, porém as fontes percorridas não confirmam tese específica de bioeconomia. |
| Norte/impacto | AMAZ possui evidência oficial de investimento direto. AMZ Venture Capital permaneceu com evidência insuficiente. |

Foram registrados seis candidatos:

- três `elegível`;
- dois `evidência insuficiente`;
- três `evidência insuficiente`, incluindo uma colisão de identidade com o
  baseline.

Hubs, associações e eventos foram mantidos apenas no inventário de descoberta.
ACATE, Porto Digital e FIINSA não foram tratados como investidores.

## Limitações e próximas ações

- Resolver a identidade entre Primus Ventures, Sul Ventures, Catarina Capital e
  Cventures sem unir automaticamente gestor e veículo.
- Encontrar fonte oficial que combine explicitamente Nordeste e bioeconomia; o
  fundo regional encontrado não basta para afirmar essa tese.
- Confirmar entidade, atividade recente e acesso externo da AMZ Venture
  Capital.
- Executar as 37 células restantes antes de alegar cobertura da matriz.

As fontes ACATE e Porto Digital declaram `ai-train=no` e
`use=reference` em `robots.txt`. Elas foram usadas somente para referência e
descoberta. O arquivo local de startups não foi usado para descoberta,
priorização, evidência ou decisão.

## Artefatos

- [coverage-matrix.jsonl](coverage-matrix.jsonl): 40 células e estado de
  execução.
- [source-inventory.jsonl](source-inventory.jsonl): fontes e recortes
  efetivamente percorridos.
- [candidates.jsonl](candidates.jsonl): fila canônica e decisões.
- [evidence.jsonl](evidence.jsonl): evidências oficiais e institucionais.
- [run-manifest.jsonl](run-manifest.jsonl): execução da primeira onda.
