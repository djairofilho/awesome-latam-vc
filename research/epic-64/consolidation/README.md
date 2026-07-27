# Fila provisória consolidada de plataformas

Este bundle materializa a redução mecânica da issue #94 na data de corte
2026-07-27. Ele não publica perfis.

## Before / after

| Artefato | Antes | Depois |
| --- | ---: | ---: |
| Candidatos | 38 | 38 |
| Evidências | 62 | 62 |
| Fontes | 117 | 117 |
| Países | 20 | 20 |

As duas passagens de deduplicação não encontraram colisões conhecidas. Valores
como “operador legal não divulgado” foram corretamente ignorados como chave.

## Decisões

- `eligible`: 9.
- `insufficient_evidence`: 17.
- `other_category`: 6.
- `excluded`: 4.
- `inactive`: 2.
- Transferências recebidas da epic #63: 3.
- Transferências recebidas ainda não materializadas: 3.

## Gate

A redução é reproduzível e possui hashes, mas a fila permanece `provisional`.
Um agente diferente do consolidador deve revisar 100% dos elegíveis, pendências,
fronteiras e transferências antes de congelar o manifesto.

## Reprodução

```text
python research/epic-64/consolidation/build_queue.py
python research/epic-64/consolidation/build_queue.py --check
python research/epic-64/validate.py --dataset research/epic-64/consolidation
python -m unittest discover -s research/epic-64/consolidation/tests -p "test_*.py"
```
