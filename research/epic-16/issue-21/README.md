# Issue 21 — fundos regionais e setoriais do Brasil

Auditoria concluída da matriz reproduzível `região x tese` da
[#21](https://github.com/djairofilho/awesome-latam-vc/issues/21).

## Recorte

- Data de corte e acesso: 2026-07-27.
- Regiões: Norte, Nordeste, Centro-Oeste, Sudeste fora de São Paulo e Rio de
  Janeiro, e Sul.
- Teses: IA, deep tech, climate tech, bioeconomia, agtech, healthtech, fintech
  e impacto.
- Total: 40 células.
- Executadas: 40 células.
- Na fila: 0 células.

A matriz completa está em [coverage-matrix.jsonl](coverage-matrix.jsonl). Cada
célula registra consultas, fontes percorridas, resultado, lacunas e próxima
ação. `executada` significa que a busca limitada foi concluída, não que um
investidor especializado necessariamente foi encontrado.

## Resultado consolidado

| Região | Achados mais fortes | Lacunas principais |
| --- | --- | --- |
| Norte | AMAZ em impacto e clima; Sinergia em bioeconomia | Sem gestor especializado confirmado em IA, deep tech ou healthtech |
| Nordeste | FIP Nordeste em agtech, healthtech, fintech e climate tech; IN3 em impacto | IA e deep tech aparecem como tecnologia ampla, sem tese especializada |
| Centro-Oeste | VivaTerra declara AgTech e Climate-Tech e opera o AgroValley MS | Falta aporte concluído da VivaTerra; demais teses sem gestor de VC confirmado |
| Sudeste fora de SP/RJ | Fundepar em deep tech e Arapy em impacto e clima | IA, bioeconomia, agtech e fintech sem tese regional especializada confirmada |
| Sul | Sul Ventures declara agtech, healthtech, fintech, energia e tecnologia | Identidade entre Primus, Catarina Capital e veículo exige revisão; deep tech, bioeconomia e impacto permanecem lacunas |

Foram registrados doze candidatos:

- sete `elegível`;
- cinco `evidência insuficiente`, incluindo a identidade de Sul Ventures, a
  atividade de Cventures e Seed4Science, a operação da AMZ Venture Capital e o
  primeiro aporte da VivaTerra.

Hubs, associações e eventos foram mantidos apenas no inventário de descoberta.
ACATE, Porto Digital e FIINSA não foram tratados como investidores.

## Método e limites

- A execução foi dividida em três ondas com 3, 6 e 31 tarefas.
- Foram priorizadas fontes oficiais do candidato e fontes institucionais
  primárias. Resultados setoriais de portfólio não foram convertidos
  automaticamente em tese.
- Hubs, aceleração sem aporte, grants, crédito e fundos de desenvolvimento foram
  usados somente para descoberta ou documentação de lacunas.
- A ausência de candidato significa apenas que a busca limitada e reproduzível
  não confirmou evidência suficiente até a data de corte.

## Próximas ações

- Resolver a identidade entre Primus Ventures, Sul Ventures, Catarina Capital e
  Cventures sem unir automaticamente gestor e veículo.
- Confirmar entidade, atividade recente e acesso externo da AMZ Venture
  Capital.
- Confirmar o primeiro aporte da VivaTerra e atualizar a atividade do
  Seed4Science.
- Separar gestoras e veículos na publicação: Fundepar, Seed4Science e Arapy não
  devem ser fundidos automaticamente.
- Publicar somente os sete elegíveis após revisão editorial e deduplicação
  final.

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
- [run-manifest.jsonl](run-manifest.jsonl): execução das três ondas.
