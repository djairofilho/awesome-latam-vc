# Publicação de programas públicos

Esta pasta materializa a issue #103 a partir da fila congelada pela issue #102.
A data de corte permanece em 27 de julho de 2026.

## Resultado

- 29 perfis publicados;
- 12 perfis de agências;
- 17 perfis de programas;
- 0 perfis de chamadas;
- 3 lotes determinísticos, com 10, 10 e 9 perfis;
- 0 IDs ou caminhos duplicados;
- 0 referências órfãs;
- 0 perfis fora da fila elegível congelada.

As chamadas temporárias aparecem dentro do perfil do programa como snapshots.
Status, valores, contrapartidas, datas e regras de uma chamada não são
generalizados para o programa. Um programa `fechado agora, recorrente` não é
apresentado como aberto.

## Lotes

| Lote | Sub-issue | Branch | Perfis |
| --- | --- | --- | ---: |
| `public-programs-01` | #145 | `agent/issue-103-public-programs-batch-01` | 10 |
| `public-programs-02` | #146 | `agent/issue-103-public-programs-batch-02` | 10 |
| `public-programs-03` | #147 | `agent/issue-103-public-programs-batch-03` | 9 |

O plano completo, os caminhos fechados e os hashes dos lotes estão em
`publication-plan.json`. O `publication-manifest.json` registra os hashes de
cada perfil e do índice final.

## Relações preservadas

- Cada agência lista seus programas elegíveis publicados.
- Cada programa aponta para sua agência operadora.
- Cada chamada permanece vinculada ao programa por `call_id`.
- Cada perfil registra aliases, IDs de evidência e links oficiais.
- Os índices em inglês, espanhol e português continuam apontando uma única vez
  para o índice canônico da categoria.

## Reprodução

Na raiz do repositório:

```text
python research/epic-65/publication/build_publication.py --check
python research/epic-65/publication/verify_publication.py
python -m unittest discover -s research/epic-65/publication/tests -v
python research/epic-65/validate.py research/epic-65/consolidation
python tools/research/validate.py --base-ref origin/main
```

O gerador nunca pesquisa nem completa dados. Ele transforma apenas as entidades
elegíveis, relações e fontes oficiais presentes na fila congelada.
