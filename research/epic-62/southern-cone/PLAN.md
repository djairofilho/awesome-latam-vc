# Plano de auditoria de aceleradoras no Cone Sul

Este plano congela o recorte anterior à coleta da issue #74. A data de corte é
27 de julho de 2026 e o contrato aplicável é a issue #68.

## Recorte

A auditoria cobre Argentina, Chile, Paraguai e Uruguai. A busca combina fontes
oficiais nacionais, programas privados de tecnologia e impacto, iniciativas
universitárias e mecanismos públicos de apoio a startups.

O recorte separa programas estruturados de aceleração de incubação, desafios,
consultoria, venture building contratado e investimento recorrente. Esses casos
permanecem no inventário e recebem decisão explícita. Programas públicos e
veículos de investimento são encaminhados à epic ou ao diretório correspondente
quando sua função dominante não pertence à Epic 62.

## Fontes e workers congelados

| Worker | País | Fonte | Objetivo |
| --- | --- | --- | --- |
| `worker-sc-01` | Argentina | GRID Exponential | Validar programa setorial, atividade e acesso externo |
| `worker-sc-02` | Argentina | CITES | Separar venture building e veículo de investimento |
| `worker-sc-03` | Argentina | IncuBAte | Aplicar a fronteira de programa público |
| `worker-sc-04` | Chile | Start-Up Chile | Aplicar a fronteira de programa público com capital |
| `worker-sc-05` | Chile | Platanus Ventures | Separar aceleração e investimento |
| `worker-sc-06` | Chile | Magical | Verificar programa, atividade e termos |
| `worker-sc-07` | Paraguai | Koga | Validar programa de impacto e atividade |
| `worker-sc-08` | Paraguai | MIC | Procurar programa nacional estruturado para startups |
| `worker-sc-09` | Paraguai | INCUNA | Aplicar a fronteira de incubação universitária |
| `worker-sc-10` | Uruguai | ThalesLab | Validar programa de aceleração e atividade |
| `worker-sc-11` | Uruguai | Ingenio | Aplicar a fronteira de incubação |
| `worker-sc-12` | Uruguai | ANII | Aplicar a fronteira de apoio público e capital |

## Ownership e redução

Cada worker escreve somente em
`research/epic-62/southern-cone/shards/<worker-id>/`. O coordenador reduz apenas
os shards desta partição, em ordem determinística, sem misturar auditorias
regionais. Fontes de terceiros servem apenas para descoberta. Elegibilidade
exige fonte oficial para identidade, programa estruturado, acesso externo,
geografia e atividade nos últimos 24 meses.

## Gates

1. este plano, a matriz e o manifesto são versionados antes da coleta;
2. cada fonte recebe estado, justificativa e ownership;
3. cada candidato recebe decisão e evidência por afirmação;
4. lacunas são resumidas por país e setor;
5. a redução é repetida com hashes idênticos;
6. todos os links inventariados passam por auditoria;
7. nenhum perfil é criado;
8. elegíveis e híbridos seguem para revisão independente na issue #77.
