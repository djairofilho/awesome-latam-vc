# Adjudicação canônica dos fundos brasileiros

Este diretório é a saída determinística da issue #220. O builder parte da
consolidação da descoberta da #216, aplica os 51 overlays das issues
#217–#219 e incorpora a adjudicação direcionada de identidade da #220.

## Geração

```powershell
python research/epic-207/brazil/build_adjudicated.py
python research/epic-207/brazil/build_adjudicated.py --check
python research/epic-207/validate.py research/epic-207/brazil
```

O builder de adjudicação chama o builder da descoberta em memória. Assim, a
saída final não depende do estado anterior dos arquivos canônicos. Todos os
JSONL são ordenados por ID e os sete artefatos centrais recebem hashes SHA-256.

A saída contém 143 fontes, 51 linhas de candidato, 128 evidências, 23
resoluções de identidade e 12 células de cobertura. O resultado por decisão é:

| Decisão | Total |
| --- | ---: |
| `eligible` | 14 |
| `duplicate` | 11 |
| `routed_accelerators` | 1 |
| `routed_angel_networks` | 1 |
| `insufficient_evidence` | 24 |

As 11 duplicatas deixam 40 identidades canônicas.

## Identidade

As resoluções da descoberta e da validação são preservadas. A issue #220
atualiza somente os dois casos que justificaram consulta à CVM:

- Vinci Capital Gestora e Vinci Gestora são organizações distintas. Os
  veículos VCP IV estão ligados à primeira, mas o candidato genérico Vinci
  Partners não identifica uma estratégia ou um veículo único;
- Jatobá Gestora de Recursos é a gestora do Jatobá Impacto Amazônia FIP Capital
  Semente. Gestora e veículo continuam entidades separadas.

Os dois candidatos permanecem `insufficient_evidence`. A CVM não foi usada
para decidir elegibilidade.

## Validação paralela

As filas em `validation-shards/` aplicam:

```text
int(sha256(candidate_id), 16) % 3
```

| Issue | Resto | Candidatos |
| --- | ---: | ---: |
| #217 | 0 | 17 |
| #218 | 1 | 19 |
| #219 | 2 | 15 |

Os três shards cobrem os 51 candidatos uma única vez. A cobertura publicada
pelas issues #217 e #219 foi reduzida a uma célula
`official_portfolios/brazil` com 32 fontes e 32 candidatos. A issue #218 não
publicou célula própria, portanto suas fontes permanecem no inventário e nas
evidências sem uma cobertura retroativa fabricada.

## Limite CVM

O manifesto registra sete tarefas de descoberta, três de validação não-CVM e
uma tarefa de adjudicação CVM. Com isso:

- `non_cvm_task_share = 10 / 11 = 90,91%`;
- `cvm_task_share = 1 / 11 = 9,09%`;
- `cvm_query_rate = 2 / 40 = 5%`.

As duas consultas confirmam somente identidade jurídica e relação
gestora-veículo. Elas não comprovam tese, recorrência, atividade recente,
acesso a startups, acesso ao Brasil ou elegibilidade.

## Correção de atividade

As evidências antigas `ev-fund-br-215-accion-ventures` e
`ev-fund-br-215-antler-brazil` não possuem data de publicação. A adjudicação
remove `observed_on` e rebaixa o claim de atividade para `inconclusive`, pois a
data de acesso não prova atividade. Accion e Antler continuam elegíveis pelas
novas evidências oficiais datadas de 23 de março de 2026 e 16 de junho de 2026.
