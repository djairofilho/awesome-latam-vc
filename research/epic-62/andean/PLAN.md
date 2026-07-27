# Plano de auditoria de aceleradoras nos países andinos

Este plano congela o recorte anterior à coleta da issue #73. A data de corte é
27 de julho de 2026 e o contrato aplicável é a issue #68.

## Recorte

A auditoria cobre Bolívia, Colômbia, Equador, Peru e Venezuela. Cada país começa
com três fontes oficiais: uma rota institucional ou universitária, uma fonte
pública ou de ecossistema e um programa corporativo, setorial ou de impacto.

Programas públicos, fundos, venture studios, incubadoras, desafios pontuais e
serviços de inovação não são tratados automaticamente como aceleradoras. Eles
permanecem no inventário e recebem decisão ou encaminhamento explícito.

## Fontes e workers congelados

| Worker | País | Fonte | Objetivo |
| --- | --- | --- | --- |
| `worker-and-01` | Bolívia | SOLYDES Aceleradora | Validar programa e atividade |
| `worker-and-02` | Bolívia | Aceleradora 100+ | Aplicar a fronteira de desafio corporativo |
| `worker-and-03` | Bolívia | AgroInnovatec 2026 | Aplicar a fronteira de venture studio público |
| `worker-and-04` | Colômbia | Aceleradora InnovaLab | Validar Mujeres Tech 2026 |
| `worker-and-05` | Colômbia | Emprendimiento Digital 2026 | Encaminhar programa público |
| `worker-and-06` | Colômbia | Rockstart LATAM | Separar programa e fundo |
| `worker-and-07` | Equador | Kruger Labs | Revalidar o candidato do piloto |
| `worker-and-08` | Equador | BuenTrip Hub | Validar programa e atividade |
| `worker-and-09` | Equador | IMPAQTO | Separar aceleração, incubação e serviços |
| `worker-and-10` | Peru | UTEC Ventures | Validar aceleradora de 12 semanas |
| `worker-and-11` | Peru | StartUp Perú | Encaminhar política pública |
| `worker-and-12` | Peru | LIQUID Venture Studio | Aplicar a fronteira de venture studio |
| `worker-and-13` | Venezuela | IESA Emprende | Verificar programa estruturado atual |
| `worker-and-14` | Venezuela | Impact Hub Caracas | Verificar aceleração versus comunidade |
| `worker-and-15` | Venezuela | Wayra Venezuela | Verificar atividade e eventual encerramento |

## Ownership e gates

Cada worker escreve somente em
`research/epic-62/andean/shards/<worker-id>/`. O coordenador reduz os shards em
ordem determinística. Elegibilidade exige fonte oficial para programa, acesso
externo, geografia, candidatura e atividade recente.

1. plano, matriz e manifesto versionados antes da coleta;
2. inventário e decisões com estado e justificativa;
3. cobertura e lacunas por país e setor;
4. redução idempotente e validação de links, schemas e UTF-8;
5. zero perfil publicado;
6. revisão independente dos elegíveis e híbridos na issue #77.
