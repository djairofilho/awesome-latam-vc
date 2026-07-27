# Auditoria final da epic #65

Auditoria determinística executada para a issue #104 com data de corte
2026-07-27. Resultado: **passed**.

## Resultado

- Agências: 29.
- Programas: 45.
- Chamadas: 21.
- Entidades com destino: 95 de 95.
- Evidências oficiais: 98 de 98.
- URLs oficiais únicas: 69.
- Cobertura e tarefas: 55 de 55.
- Perfis elegíveis e publicados: 29 de 29.
- Perfis de chamadas: 0.
- Transfers: 13 entradas, 8 materializadas e 5 saídas.
- Itens de revisão independente: 58.
- Hashes declarados verificados: 73.
- Problemas críticos: 0.
- Problemas altos: 0.

## Gates

| Gate | Status | Registros | Resultado |
| --- | --- | ---: | --- |
| `schemas-and-contract` | passed | 304 | Os seis schemas e as invariantes do contrato validam o bundle consolidado. |
| `frozen-publication` | passed | 29 | A fila congelada, os lotes, perfis e hashes da #103 reconciliam. |
| `entity-destinations` | passed | 95 | As 29 agências, 45 programas e 21 chamadas têm destino terminal. |
| `relationships` | passed | 95 | Relações agência → programa → chamada fecham nos dois sentidos. |
| `coverage-and-tasks` | passed | 110 | As 55 células correspondem às tarefas; 25 lacunas estão justificadas. |
| `category-transfers` | passed | 18 | As 13 entradas e 5 saídas têm adjudicação e destino canônico. |
| `official-links` | passed | 98 | As 98 evidências são oficiais, têm URL HTTP(S) e vínculo bidirecional. |
| `declared-hashes` | passed | 73 | Todos os hashes declarados da coleta à publicação reconciliam. |
| `profiles-and-indexes` | passed | 32 | Os 29 perfis aparecem uma vez no índice e nos três índices multilíngues. |
| `deterministic-ordering` | passed | 248 | JSONL, fila, lotes e índice seguem chaves determinísticas. |
| `corfo-and-boundaries` | passed | 10 | CORFO, Start-Up Chile, rebaixamentos e cinco fronteiras foram revalidados. |
| `utf8-and-mojibake` | passed | 156 | Todos os artefatos textuais da epic e da categoria usam UTF-8 íntegro. |
| `independent-review` | passed | 58 | Os 58 itens da revisão independente estão resolvidos, sem risco alto aberto. |

## Limitações

- A auditoria de links é estrutural e determinística: valida fonte oficial, URL HTTP(S), sujeito e vínculo com perfis. Disponibilidade HTTP ao vivo não bloqueia o CI; a coleta registra accessed_on em 2026-07-27.
- Decisões com evidência insuficiente permanecem fora do catálogo e só mudam mediante nova fonte oficial e nova revisão.

## Reprodução

```text
python research/epic-65/final-audit/audit.py --check
python -m unittest discover -s research/epic-65/final-audit/tests -v
```

O artefato legível por máquina e todos os hashes de entrada estão em
`audit-report.json`.
