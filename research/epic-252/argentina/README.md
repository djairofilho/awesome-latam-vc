# Reauditoria de fundos — Argentina

Data de corte: `2026-07-30`. Cobertura auditada, sem alegar totalidade.

- 12 fontes não regulatórias;
- 8 candidatos: 4 elegíveis, 2 duplicatas, 1 insuficiente e 1 encaminhado;
- zero consultas à Comisión Nacional de Valores de Argentina;
- amostra determinística de exclusões: ordenar `candidate_id` e revisar o primeiro `ceil(n/3)` de `candidates.jsonl` com decisões `duplicate` ou `insufficient_evidence` (fund-ar-galicia-ventures);
- revisão independente de #277 aprovada por `integrator` em 2026-07-30, sem achados críticos ou altos.
