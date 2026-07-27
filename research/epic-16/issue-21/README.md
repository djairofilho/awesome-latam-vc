# Issue 21 — fundos regionais e setoriais do Brasil

Segunda onda da matriz reproduzível `região x tese` da
[#21](https://github.com/djairofilho/awesome-latam-vc/issues/21).

## Recorte

- Data de corte e acesso: 2026-07-27.
- Regiões: Norte, Nordeste, Centro-Oeste, Sudeste fora de São Paulo e Rio de
  Janeiro, e Sul.
- Teses: IA, deep tech, climate tech, bioeconomia, agtech, healthtech, fintech
  e impacto.
- Total: 40 células.
- Executadas acumuladas: 9 células.
- Executadas nesta onda: Centro-Oeste/agtech, Centro-Oeste/climate tech,
  Sudeste fora de SP/RJ/deep tech, Sudeste fora de SP/RJ/impacto,
  Nordeste/climate tech e Norte/bioeconomia.
- Na fila: 31 células.

A matriz completa está em [coverage-matrix.jsonl](coverage-matrix.jsonl). Uma
célula em `fila` contém consultas planejadas, mas não representa pesquisa
executada nem cobertura.

## Resultado da segunda onda

| Célula | Resultado |
| --- | --- |
| Centro-Oeste/agtech | VivaTerra declara capital seed e growth para AgTech e opera o AgroValley MS, mas ainda não há aporte concluído comprovado. |
| Centro-Oeste/climate tech | A mesma gestora declara tese Climate-Tech; o acordo regional comprova operação de ecossistema, não investimento. |
| Sudeste fora de SP/RJ/deep tech | Fundepar foi validada como investidora de empresas tecnológicas originadas em universidades e centros de pesquisa. |
| Sudeste fora de SP/RJ/impacto | Arapy realizou o primeiro investimento em 2026 e continua analisando propostas. |
| Nordeste/climate tech | IN3 investe em negócios socioambientais do Norte e Nordeste, inclusive energia limpa e agricultura sustentável, sem especialização climática exclusiva. |
| Norte/bioeconomia | Sinergia publica faixa, participação, estágio e seleção para startups da bioeconomia amazônica, mas falta evidência datada de atividade recente. |

Foram registrados doze candidatos nas duas ondas:

- seis `elegível`;
- seis `evidência insuficiente`, incluindo uma colisão de identidade com o
  baseline e três casos que exigem confirmação de atividade ou aporte.

Hubs, associações e eventos foram mantidos apenas no inventário de descoberta.
ACATE, Porto Digital e FIINSA não foram tratados como investidores.

## Limitações e próximas ações

- Resolver a identidade entre Primus Ventures, Sul Ventures, Catarina Capital e
  Cventures sem unir automaticamente gestor e veículo.
- Encontrar fonte oficial que combine explicitamente Nordeste e bioeconomia; o
  fundo regional encontrado não basta para afirmar essa tese.
- Confirmar entidade, atividade recente e acesso externo da AMZ Venture
  Capital.
- Confirmar o primeiro aporte da VivaTerra, atualizar o Seed4Science e validar
  atividade recente e estrutura jurídica da Sinergia Investimentos.
- Separar gestoras e veículos na publicação: Fundepar, Seed4Science e Arapy não
  devem ser fundidos automaticamente.
- Executar as 31 células restantes antes de alegar cobertura da matriz.

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
- [run-manifest.jsonl](run-manifest.jsonl): execução das duas ondas.
