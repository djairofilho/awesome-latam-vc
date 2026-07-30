# Baseline offline de fundos com acesso ao Brasil

Este diretório implementa a issue #209 sob o contrato da
[epic #207](../README.md). A baseline é construída exclusivamente a partir do
catálogo publicado e da consolidação da epic #16 congelados no commit
`876eb331f84371410ea442dbc1f457685e36a460`.

Não há acesso à rede, consulta à CVM, descoberta de candidatos nem
revalidação de decisões. Fontes anteriores permanecem memória de proveniência
e nunca contam como nova descoberta.

## Entradas

- perfis canônicos em `funds/**/*.md` no commit-base;
- candidatos, evidências e fontes consolidados em
  `research/epic-16/issue-22/` no mesmo commit.

O PR #225 é registrado apenas como mudança pendente. Nenhum arquivo, nome ou
decisão desse PR é importado.

## Artefatos

| Arquivo | Responsabilidade |
| --- | --- |
| `catalog-baseline.jsonl` | Snapshot de todos os perfis publicados |
| `identity-index.jsonl` | Nomes, aliases, domínios e colisões conhecidas |
| `prior-candidates.jsonl` | Memória integral dos candidatos da epic #16 |
| `prior-sources.jsonl` | Fontes anteriores classificadas como baseline |
| `queue-manifest.jsonl` | Partições exclusivas de perfis, fontes e candidatos |
| `pending-changes.jsonl` | Mudanças externas conhecidas e não importadas |
| `baseline-summary.json` | Contagens derivadas, política offline e hashes |

Domínios são auxiliares de identidade. Hosts secundários e domínios
compartilhados permanecem marcados para adjudicação; o builder nunca os usa
para unir perfis automaticamente.

## Geração e validação

```powershell
python research/epic-207/baseline/build_baseline.py
python research/epic-207/baseline/build_baseline.py --check
python -m unittest discover -s research/epic-207/baseline/tests -v
```

O modo `--check` relê as entradas do commit-base no banco de objetos Git,
recalcula tudo e falha se qualquer artefato canônico estiver ausente ou
divergente. Mudanças posteriores no catálogo não reinterpretam o snapshot.
