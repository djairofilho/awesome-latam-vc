# Fila consolidada de plataformas

Este bundle materializa a redução e a revisão independente da issue #94 na data
de corte 2026-07-27. Ele não publica perfis.

## Before / after

| Artefato | Antes | Depois |
| --- | ---: | ---: |
| Candidatos | 38 | 39 |
| Evidências | 62 | 63 |
| Fontes | 117 | 118 |
| Países | 20 | 20 |

As duas passagens de deduplicação não encontraram colisões conhecidas. Valores
como “operador legal não divulgado” foram corretamente ignorados como chave.

## Decisões

- `eligible`: 9.
- `insufficient_evidence`: 18.
- `other_category`: 6.
- `excluded`: 4.
- `inactive`: 2.
- Transferências recebidas da epic #63: 3.
- Transferências materializadas: 1.
- Transferências rejeitadas pelo contrato: 2.

## Gate

A redução é reproduzível, possui hashes e está `frozen`. A revisão independente
cobriu 100% dos elegíveis, `other_category`, transferências recebidas e enviadas,
além de 21.74% dos demais candidatos. Não há
divergência alta aberta.

## Reprodução

```text
python research/epic-64/consolidation/build_queue.py
python research/epic-64/consolidation/build_queue.py --check
python research/epic-64/validate.py --dataset research/epic-64/consolidation
python -m unittest discover -s research/epic-64/consolidation/tests -p "test_*.py"
```
