# Plano determinístico de publicação

## Entrada congelada

- Issue: #103.
- Contrato: #97 e epic #65.
- Consolidação: issue #102, mergeada pelo PR #143.
- Data de corte: 2026-07-27.
- Ordem: `entity_id` crescente.
- Tamanho máximo: 10 perfis por lote.
- Fila elegível: 12 agências e 17 programas, total de 29 perfis.
- Quantidade de lotes: `ceil(29 / 10) = 3`.
- Chamadas publicáveis: zero; chamadas temporárias aparecem somente como
  relações dos programas.

O arquivo `publication-plan.json` congela os 29 IDs, seus caminhos, os três
lotes e os hashes SHA-256 das entradas. O hash de um lote é calculado sobre o
array `profiles` serializado como JSON UTF-8 compacto, com chaves ordenadas e
sem escape de Unicode.

## Lotes

| Lote | Perfis | Intervalo de IDs | Branch |
| --- | ---: | --- | --- |
| 1 | 10 | `agency-ande` a `agency-proinnovate` | `agent/issue-103-public-programs-batch-01` |
| 2 | 10 | `agency-sebrae` a `program-brde-labs-rs` | `agent/issue-103-public-programs-batch-02` |
| 3 | 9 | `program-conquito-fonquito` a `program-start-up-chile` | `agent/issue-103-public-programs-batch-03` |

Cada lote será materializado em um commit próprio e reversível. A atualização
do índice e a verificação final serão serializadas depois dos três lotes.

## Restrições

- Publicar somente IDs elegíveis na fila congelada.
- Não promover chamadas a perfis.
- Não generalizar valores, contrapartidas, datas ou disponibilidade.
- Preservar aliases e relações agências → programas → chamadas.
- Usar somente as fontes oficiais já adjudicadas na consolidação.
- Rejeitar perfis duplicados, caminhos repetidos, referências órfãs, lotes
  vazios e lotes acima de 10 perfis.
- Manter os links da categoria nos índices em inglês, espanhol e português.
