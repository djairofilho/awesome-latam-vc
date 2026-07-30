# Revisão canônica dos fundos brasileiros

Este diretório é a saída determinística da revisão independente da issue #221.
O builder parte, em memória, da adjudicação da issue #220, aplica as correções
da revisão e incorpora o shard `worker-221-review`.

## Geração e validação

```powershell
python research/epic-207/brazil/build_review.py
python research/epic-207/brazil/build_review.py --check
python research/epic-207/validate.py research/epic-207/brazil
python -m unittest discover -s research/epic-207/tests -v
```

Os sete JSONL centrais são ordenados deterministicamente e recebem hashes
SHA-256 no manifesto. O arquivo `review-report.json` registra as métricas
auxiliares que não pertencem ao schema estrito de `audit-report.json`.

## Resultado

O bundle final contém 76 linhas de candidato e 63 identidades canônicas:

| Decisão | Total |
| --- | ---: |
| `eligible` | 27 |
| `duplicate` | 13 |
| `routed_accelerators` | 3 |
| `routed_angel_networks` | 4 |
| `routed_funding_platforms` | 1 |
| `insufficient_evidence` | 28 |

A amostra de revisão cobre todos os 27 elegíveis, todos os oito roteados, os
dois candidatos consultados na CVM, seis insuficientes escolhidos pelos
menores hashes SHA-256 e os achados das buscas cegas e passagens finais.

## CVM e origem

A CVM permanece restrita às duas consultas herdadas sobre Vinci e Jatobá.
Nenhuma nova descoberta usa CVM ou baseline como origem. As consultas não
comprovam tese, recorrência, atividade, acesso ao Brasil ou elegibilidade.

## Correções antes do congelamento

- Vinci Partners não agrega duas gestoras distintas como aliases e não recebe
  um `manager_id` genérico.
- DNA Capital, Jatobá Gestora e Mundi Ventures mantêm nomes de veículos somente
  em `vehicle_ids`.
- Quatro evidências sem `observed_on` tiveram o claim de atividade rebaixado
  para `inconclusive`.
- A evidência da AgroVen passa a refletir que os aportes são realizados pelos
  membros do clube.

O relatório auxiliar também explicita os 17 casos originais com uma única
fonte, a sobreposição entre famílias de descoberta, a curva cumulativa e as
passagens finais de saturação.
