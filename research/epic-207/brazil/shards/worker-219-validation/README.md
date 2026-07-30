# Validação oficial — issue #219

Este shard encerra a validação dos 15 candidatos da fila `validation-shards/issue-219`. A pesquisa usou somente fontes públicas não CVM, priorizando páginas controladas pelas próprias gestoras e anúncios oficiais das startups investidas.

## Resultado

| Decisão | Quantidade |
|---|---:|
| `eligible` | 2 |
| `duplicate` | 4 |
| `insufficient_evidence` | 9 |
| Total decidido | 15 |

Elegíveis: 1616 Ventures e Parceiro Ventures.

Duplicados: monashees, Quona Capital, Canary e Triaxis Capital. Cada overlay aponta para o perfil ou candidato canônico de destino.

## Regra aplicada

Uma página institucional acessível em 2026-07-30 comprova apenas as afirmações que ela publica. A data de acesso não foi convertida em data de atividade. A decisão `eligible` foi usada somente quando fontes oficiais, em conjunto, confirmaram identidade, investimento direto, recorrência, acesso explícito ao Brasil e atividade observada entre 2024-07-30 e 2026-07-30.

Por isso, AMZ Venture Capital, Seedstars, Arar Capital, LH Invest e Sororitê Ventures permanecem insuficientes apesar de terem identidade e tese claras: faltou atividade oficial datada. BFF, Farout e Four Rivers têm aporte confirmado por anúncio oficial da startup, mas a identidade do investidor e/ou a recorrência não puderam ser resolvidas sem inferência. A Nido descreve seleção de fundos e possibilidade de coinvestimento, sem histórico oficial suficiente de investimento direto recorrente.

## Artefatos

- `candidates.jsonl`: overlay completo dos 15 candidatos, todos com `status: decided`.
- `evidence.jsonl`: uma passagem oficial atual por candidato, com lacunas marcadas como `inconclusive`.
- `source-inventory.jsonl`: inventário das 14 fontes oficiais consultadas e vínculos com fontes anteriores.
- `coverage-matrix.jsonl`: fechamento auditável da cobertura.
- `build_validation.py`: geração determinística dos JSONL a partir da fila imutável.

Nenhuma fonte CVM foi consultada e nenhum dado de cheque, estágio, tese ou recorrência foi estimado.
