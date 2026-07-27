# Publicação de plataformas de captação

A issue #95 publicou exatamente os 9 candidatos `eligible` da fila
congelada da issue #94. Nenhum candidato `insufficient_evidence`,
`other_category`, `excluded` ou `inactive` foi promovido.

## Lote

- lote: `platforms-001`;
- sub-issue: [#151](https://github.com/djairofilho/awesome-latam-vc/issues/151);
- branch: `agent/issue-95-platforms-publication`;
- owner: `issue-95-publisher`;
- perfis: 9;
- hash: `0ab4c169f89a202a2fe34de56ebaf1850a714d962b45720182fc69250f4aa8c3`.

Os perfis e os índices em inglês, português e espanhol são gerados a partir dos
artefatos congelados. O manifesto fixa hashes dos insumos, perfis e índices.

## Reprodução

```text
python research/epic-64/publication/build_publication.py
python research/epic-64/publication/build_publication.py --check
python -m unittest discover -s research/epic-64/publication/tests -p "test_*.py"
```
