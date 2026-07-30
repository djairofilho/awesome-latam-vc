# Validação do shard 1: issue #218

Este shard valida os 19 candidatos atribuídos por `sha256(candidate_id) mod 3 = 1`.
A data de corte é 30 de julho de 2026.

## Resultado

| Decisão | Total |
| --- | ---: |
| `duplicate` | 5 |
| `eligible` | 4 |
| `routed_accelerators` | 1 |
| `routed_angel_networks` | 1 |
| `insufficient_evidence` | 8 |
| **Total** | **19** |

## Método

Cada ID foi reaberto individualmente em fonte oficial ou institucional atual.
Elegibilidade exigiu as cinco claims oficiais do contrato: identidade, investimento
direto, recorrência, atividade observada entre 2024-07-30 e 2026-07-30 e relação
explícita com o Brasil. Data de acesso em página sem data não foi usada como
atividade.

Não houve consulta à CVM. O arquivo local de startups não foi lido nem usado.
Notícias não sustentam nenhuma decisão deste shard. Cheque, estágio, tese e
recorrência ausentes não foram estimados.

`source-inventory.jsonl` registra 25 fontes não-CVM e a chave SHA-256 da URL final.
`evidence.jsonl` contém 25 evidências oficiais. `candidates.jsonl` é um overlay
completo dos 19 IDs e preserva as fontes e evidências anteriores.

## Decisões por candidato

| ID | Nome | Decisão | Destino |
| --- | --- | --- | --- |
| `fund-br-210-canary` | Canary | `duplicate` | funds/regional/canary.md |
| `fund-br-210-good-karma` | Good Karma | `insufficient_evidence` | não se aplica |
| `fund-br-210-sp-ventures` | SP Ventures | `duplicate` | funds/regional/sp-ventures.md |
| `fund-br-210-valor-capital-group` | Valor Capital Group | `duplicate` | funds/multi-country/valor-capital-group.md |
| `fund-br-213-30n-ventures` | 30N Ventures | `insufficient_evidence` | não se aplica |
| `fund-br-213-fhe-ventures` | FHE Ventures | `insufficient_evidence` | não se aplica |
| `fund-br-213-primus-ventures` | Primus Ventures | `duplicate` | funds/brazil/primus-ventures.md |
| `fund-br-213-quartzo-capital` | Quartzo Capital | `eligible` | não se aplica |
| `fund-br-213-sororite-ventures` | Sororitê Ventures | `duplicate` | fund-br-sororite-ventures |
| `fund-br-214-agroven` | AgroVen | `routed_angel_networks` | epic-63-angel-networks |
| `fund-br-214-ipe-investe` | IPÊ Investe | `routed_accelerators` | epic-62-accelerators |
| `fund-br-214-jatoba-impacto-amazonia` | Jatobá Gestora | `insufficient_evidence` | não se aplica |
| `fund-br-214-parallax-ventures` | Parallax Ventures | `eligible` | não se aplica |
| `fund-br-bs2-ventures` | BS2 Ventures | `eligible` | não se aplica |
| `fund-br-canaan` | Canaan | `insufficient_evidence` | não se aplica |
| `fund-br-lightspeed` | Lightspeed | `insufficient_evidence` | não se aplica |
| `fund-br-lux-capital` | Lux Capital | `insufficient_evidence` | não se aplica |
| `fund-br-mundi-ventures-latam` | Mundi Ventures | `eligible` | não se aplica |
| `fund-br-sagol-holdings` | Sagol Holdings | `insufficient_evidence` | não se aplica |

## Pendências explícitas

- Good Karma: resolver a mudança cadastral para Just Climate e a continuidade da
  identidade pública e da carteira.
- 30N, Canaan, Lightspeed, Lux e Sagol: uma investida, presença comercial ou
  menção regional isolada não prova acesso recorrente ao Brasil.
- FHE Ventures: faltam fonte oficial substantiva, veículo, carteira, recorrência
  e atividade datada.
- Jatobá: faltam primeiro investimento, carteira e atividade oficial datada do
  Fundo Impacto Amazônia.

## Fronteiras de categoria

- AgroVen foi encaminhada para `epic-63-angel-networks`: o site informa que os
  aportes são feitos pelos membros do clube.
- IPÊ Investe foi encaminhada para `epic-62-accelerators`: a fonte descreve a
  primeira edição de um programa de aceleração com aportes por fases.
- Mundi Ventures foi tratada como organização investidora. LatAm Fund I continua
  preservado em `vehicle_ids`, sem gerar um segundo perfil para o veículo.
