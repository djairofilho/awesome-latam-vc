# Fila consolidada de programas públicos

Este bundle consolida as quatro auditorias regionais da epic #65 na data de
corte 2026-07-27. A revisão independente está concluída e nenhum perfil é
publicado nesta etapa.

## Before / after

| Entidade | Antes | Depois |
| --- | ---: | ---: |
| Agências | 27 | 29 |
| Programas | 39 | 45 |
| Chamadas | 21 | 21 |
| Evidências | 90 | 98 |
| Linhas de cobertura | 55 | 55 |

Não havia IDs duplicados entre regiões. A redução preservou todos os registros,
ordenou-os por ID, materializou seis transferências antes pendentes e
reconciliou suas relações.

## Decisões

- Agências elegíveis: 12.
- Programas elegíveis: 17.
- Agências com evidência insuficiente: 8.
- Programas com evidência insuficiente: 9.
- Transferências recebidas da epic #62: 13.
- Transferências materializadas na fila pública: 8.
- Transferências rejeitadas pelo contrato público: 5.
- Fronteiras encaminhadas para fundos ou aceleradoras: 5.

## Revisão independente

A revisão de 100% dos grupos obrigatórios está em
`independent-review.jsonl`, com narrativa em `INDEPENDENT_REVIEW.md`.
Fondo Emprender e Capital Pioneras foram rebaixados por não confirmarem uma rota
específica para startups. Seis transferências antes pendentes foram
materializadas, além das duas já ligadas a programas; cinco receberam outro
destino canônico. Não restam divergências altas abertas e o manifesto está
congelado com hashes SHA-256.

## Reprodução

```text
python research/epic-65/consolidation/build_queue.py
python research/epic-65/consolidation/build_queue.py --check
python research/epic-65/validate.py research/epic-65/consolidation
python -m unittest discover -s research/epic-65/consolidation/tests -p "test_*.py"
```
