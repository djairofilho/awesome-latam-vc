# Publicação das aceleradoras

Esta etapa materializa a fila congelada pela revisão independente da epic #62.
O gerador lê o manifesto publicado na issue #77, valida seu hash e só então
cria os perfis e o índice da categoria.

## Resultado congelado

- Issue de publicação: #78
- Contrato: #68
- Data de corte: 2026-07-27
- Candidatos publicados: 26
- Batches: 3, com tamanhos 10, 10 e 6
- Perfis excluídos, insuficientes ou roteados: 0
- Branch: `agent/issue-78-accelerators-publication`

## Artefatos

- [Plano](PLAN.md)
- [Batch 01](batches/batch-01.md), subissue #155
- [Batch 02](batches/batch-02.md), subissue #156
- [Batch 03](batches/batch-03.md), subissue #157
- [Manifesto dos batches](frozen-batches.json)
- [Manifesto da publicação](publication-manifest.json)
- [Hashes dos artefatos](sha256sums.txt)

Execute `python research/epic-62/publication/build_publication.py` para
reproduzir os arquivos gerados e
`python -m unittest discover -s research/epic-62/publication/tests -v` para
verificar completude, exclusividade, determinismo, relações e links internos.

## Limite do validador central

O validador central interpreta todo o diff da branch como uma única PR e, por
isso, reporta 26 adições contra o limite de 10. Esta execução não abre PR. O
contrato de tamanho é aplicado aos três batches e testado em
`test_batches_are_complete_small_and_deterministic`, que exige exatamente
10, 10 e 6 perfis, sem repetição ou lacuna.
