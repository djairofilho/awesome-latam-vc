# Pré-freeze da auditoria de fundos do Peru

Execução das issues #279 a #282 até o gate obrigatório de revisão
independente, com data de corte em 2026-07-30.

Resultado provisório: 15 candidatos, 1 elegível, 2 com evidência insuficiente,
4 encaminhados e 8 duplicatas. Toda descoberta foi não regulatória. Uma consulta
à SMV foi usada somente para resolver a divergência de identidade da CAPIA,
equivalente a 6,7% dos candidatos.

O freeze, os perfis e a publicação estão bloqueados em
`review-request.json` até a aprovação do integrador.

```powershell
python research/epic-253/peru/build_prefreeze.py
python -m unittest research.epic-253.tests.test_peru_prefreeze
```
