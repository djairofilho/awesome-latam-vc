# Plano de auditoria de aceleradoras no México, América Central e Caribe

Este plano congela o recorte anterior à coleta da issue #72. A data de corte é
27 de julho de 2026 e o contrato aplicável é a issue #68.

## Recorte

A auditoria cobre México, Belize, Costa Rica, El Salvador, Guatemala, Honduras,
Nicarágua, Panamá, Cuba, Haiti, Porto Rico e República Dominicana. A busca
combina fontes nacionais, uma fonte regional centro-americana e programas
setoriais de tecnologia, impacto e empreendedorismo inclusivo.

O recorte não trata diretórios, concursos, incubação, coworking ou investimento
recorrente como aceleração. Esses casos permanecem no inventário e recebem uma
decisão explícita. Programas de operadoras internacionais e programas públicos
são encaminhados à epic correspondente quando o papel dominante não pertence à
Epic 62.

## Fontes e workers congelados

| Worker | País ou recorte | Fonte | Objetivo |
| --- | --- | --- | --- |
| `worker-mxcac-01` | México | 500 LatAm | Separar programa de aceleração e veículo de investimento |
| `worker-mxcac-02` | México | New Ventures | Validar aceleração de impacto e atividade |
| `worker-mxcac-03` | México | MassChallenge México | Verificar atividade recente e recorrência |
| `worker-mxcac-04` | México | SparkLabs México | Verificar programa local e acesso externo |
| `worker-mxcac-05` | Costa Rica | Carao Ventures | Separar aceleração e investimento |
| `worker-mxcac-06` | Guatemala | Alterna | Validar Ruta Alterna e seu fundo |
| `worker-mxcac-07` | Panamá | Ciudad del Saber | Aplicar a fronteira de incubação |
| `worker-mxcac-08` | Honduras | Honduras Digital Challenge | Aplicar a fronteira de concurso pontual |
| `worker-mxcac-09` | Porto Rico | Parallel18 | Validar P18, atividade e chamada |
| `worker-mxcac-10` | República Dominicana | CREE Banreservas | Validar programa e rota pública |
| `worker-mxcac-11` | Haiti | Banj | Verificar programa estruturado e atividade |
| `worker-mxcac-12` | Cuba | CubaEmprende | Aplicar a fronteira de formação/incubação |
| `worker-mxcac-13` | Belize | BELTRAIDE | Verificar programas nacionais para startups |
| `worker-mxcac-14` | América Central | CENPROMYPE | Procurar cobertura oficial para El Salvador e Nicarágua |

## Ownership e redução

Cada worker escreve somente em
`research/epic-62/mexico-cac/shards/<worker-id>/`. O coordenador reduz os shards
em ordem determinística. Fontes de terceiros servem apenas para descoberta.
Elegibilidade exige fonte oficial para identidade, programa estruturado, acesso
externo, geografia e atividade nos últimos 24 meses.

## Gates

1. este plano, a matriz e o manifesto são versionados antes da coleta;
2. cada fonte recebe estado, justificativa e ownership;
3. cada candidato recebe decisão e evidência por afirmação;
4. lacunas são resumidas por país e setor;
5. nenhum perfil é criado;
6. elegíveis e híbridos seguem para revisão independente na issue #77.
