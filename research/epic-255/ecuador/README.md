# Pré-freeze da auditoria de fundos do Equador

Execução das issues #289 a #293, com data de corte em 2026-07-30. Este recorte
chega até o gate de revisão independente e não contém manifesto de freeze nem
arquivos de publicação.

O universo consolidado possui 15 candidatos: 1 elegível proposto, 3 duplicatas,
5 encaminhamentos e 6 casos com evidência insuficiente. IMPAQTO Capital veio do
handoff auditado do Peru e não foi contado como descoberta nova. As outras 14
identidades vieram de fontes não regulatórias.

Uma consulta à SCVS foi usada somente para confirmar a identidade jurídica do
veículo CREAS Ecuador. Isso representa 6,7% do universo e não sustenta descoberta
ou elegibilidade.

A busca cega percorreu mapa de ecossistema, relatório setorial e programa
municipal com vocabulário diferente. Seus quatro achados retornaram à validação;
nenhum alterou o elegível proposto. O resultado expressa cobertura auditada das
fontes enumeradas, não totalidade absoluta do mercado.

```powershell
python research/epic-255/ecuador/build_prefreeze.py
python -m unittest research.epic-255.tests.test_ecuador_prefreeze
```
