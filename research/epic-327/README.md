# Auditoria delta de fundos da América Latina

Este diretório implementa a epic [#327](https://github.com/djairofilho/awesome-latam-vc/issues/327).
O ciclo valida uma fila externa de nomes contra o catálogo atual e contra fontes
oficiais independentes. A fila serve apenas para descoberta: descrições, teses,
estágios, cheques e outros fatos de terceiros não entram nos artefatos públicos.

## Limite do resultado

O resultado representa a revisão dos candidatos fornecidos na data de corte. Ele
não comprova cobertura total do mercado latino-americano. Os freezes das epics
#207 e #248 a #258 permanecem históricos e não podem ser regenerados por este
ciclo.

## Camadas

1. `baseline/`: snapshot determinístico dos perfis de fundos em `4190d8c`.
2. fila privada: nomes e países indicados, mantidos fora do Git.
3. shards de triagem: identidade oficial e rota de categoria.
4. reducer: aliases, gestoras, marcas, veículos e programas canônicos.
5. shards de validação: `int(sha256(candidate_id), 16) mod 3`.
6. revisão independente, freeze e publicação em lotes de até dez fundos.

Somente evidências oficiais podem sustentar elegibilidade ou fatos publicados.
Informações ausentes permanecem `not_disclosed` ou resultam em
`insufficient_evidence`.

## Topologia

O arquivo `workers/topology.json` reserva um integrador e três writers paralelos.
Cada writer possui worktree, branch e diretório de artefatos exclusivos. Apenas
o integrador altera índices globais, traduções, exports e expectativas de
contagem.

## Reprodução do baseline

```text
python research/epic-327/baseline/build_baseline.py --check
python -m unittest discover -s research/epic-327/tests -v
```

Sem `--check`, o primeiro comando regenera somente os três arquivos do novo
baseline. Ele lê os objetos Git do commit congelado e não acessa a rede.

## Issues

- #328: contrato, baseline e topologia
- #329: intake e deduplicação
- #330 a #332: triagem geográfica
- #333: consolidação de identidade
- #334 a #336: validação oficial
- #337: revisão independente e freeze
- #338: publicação e auditoria final
