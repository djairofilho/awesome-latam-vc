# Publicação de redes-anjo

A issue #87 publica exatamente os seis perfis pendentes da fila congelada e
revisada da issue #86. Os cinco perfis já existentes são preservados e aparecem
nos três índices. O PAD/UDEP não integra a publicação.

## Lote

- lote: `angels-001`;
- sub-issue: [#159](https://github.com/djairofilho/awesome-latam-vc/issues/159);
- branch: `agent/issue-87-angels-publication`;
- owner: `issue-87-publisher`;
- perfis novos: 6;
- perfis preservados: 5;
- hash: `cdb068e4ba3c2769da4c65b8653dfb73ae2f0d6332ed56867283f28ac119b174`.

## Reprodução

```text
python research/epic-63/publication/build_publication.py
python research/epic-63/publication/build_publication.py --check
python -m unittest discover -s research/epic-63/publication/tests -p "test_*.py"
```
