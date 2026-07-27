# Fila provisória consolidada de programas públicos

Este bundle consolida as quatro auditorias regionais da epic #65 na data de
corte 2026-07-27. Nenhum perfil é publicado nesta etapa.

## Before / after

| Entidade | Antes | Depois |
| --- | ---: | ---: |
| Agências | 27 | 27 |
| Programas | 39 | 39 |
| Chamadas | 21 | 21 |
| Evidências | 90 | 90 |
| Linhas de cobertura | 55 | 55 |

Não havia IDs duplicados entre regiões. A redução preservou todos os registros,
ordenou-os por ID e reconciliou suas relações.

## Decisões

- Agências elegíveis: 12.
- Programas elegíveis: 15.
- Agências com evidência insuficiente: 5.
- Programas com evidência insuficiente: 5.
- Transferências recebidas da epic #62: 13.
- Transferências já ligadas a programas existentes: 2.
- Transferências que exigem revisão pelo contrato público: 11.
- Fronteiras encaminhadas para fundos ou aceleradoras: 5.

## Estado do gate

A redução mecânica está concluída, mas a fila ainda é `provisional`. Um agente
diferente do consolidador deve revisar 100% dos elegíveis, pendências e casos de
fronteira antes de congelar os hashes.

## Reprodução

```text
python research/epic-65/consolidation/build_queue.py
python research/epic-65/consolidation/build_queue.py --check
python research/epic-65/validate.py research/epic-65/consolidation
python -m unittest discover -s research/epic-65/consolidation/tests -p "test_*.py"
```
