# Auditoria congelada de fundos do Equador

Execução das issues #289 a #293, com data de corte em 2026-07-30 e revisão
independente reconciliada.

O universo consolidado possui 15 candidatos: 1 elegível, 3 duplicatas,
6 encaminhamentos ou casos fora do escopo e 5 casos com evidência insuficiente.
IMPAQTO Capital veio do
handoff auditado do Peru e não foi contado como descoberta nova. As outras 14
identidades vieram de fontes não regulatórias.

Uma consulta à SCVS foi usada somente para confirmar a identidade jurídica do
veículo CREAS Ecuador. Isso representa 6,7% do universo e não sustenta descoberta
ou elegibilidade.

A revisão independente aprovou o único elegível, reconciliou BuenaVista Capital
como private equity e substituiu o endpoint indisponível da Kruger Labs por sua
página inicial acessível e pelo roster atual da ECUACAP. O freeze registra zero
inconsistência crítica ou alta aberta.

A busca cega percorreu mapa de ecossistema, relatório setorial e programa
municipal com vocabulário diferente. Seus quatro achados retornaram à validação;
nenhum alterou o elegível congelado. O resultado expressa cobertura auditada das
fontes enumeradas, não totalidade absoluta do mercado.

O único lote congelado publica IMPAQTO Capital em um perfil regional com
geografia-base estrita no Equador e conteúdo equivalente em inglês, português
brasileiro e espanhol.

```powershell
python research/epic-255/ecuador/build_prefreeze.py
python -m unittest research.epic-255.tests.test_ecuador_prefreeze
```
