# Auditoria congelada de fundos do Peru

Execução das issues #279 a #283, com data de corte em 2026-07-30 e revisão
independente reconciliada.

Resultado final: 15 candidatos, zero elegíveis locais, 2 com evidência
insuficiente, 5 encaminhados e 8 duplicatas. Toda descoberta foi não regulatória. Uma consulta
à SMV foi usada somente para resolver a divergência de identidade da CAPIA,
equivalente a 6,7% dos candidatos.

IMPAQTO Capital foi confirmado como fundo direto e recorrente com cobertura do
Peru, mas sua sede oficial é Quito. Por isso, sua publicação canônica foi
encaminhada ao epic do Equador #255 e às issues #289–#293. Nenhum perfil novo
foi criado no recorte peruano.

```powershell
python research/epic-253/peru/build_prefreeze.py
python -m unittest research.epic-253.tests.test_peru_prefreeze
```
