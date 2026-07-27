# Plano de auditoria de aceleradoras estrangeiras

Este plano congela o recorte anterior à coleta da issue #75. A data de corte é
27 de julho de 2026 e o contrato aplicável é a issue #68.

## Recorte

A auditoria cobre programas operados fora da América Latina que aceitem
startups latino-americanas de forma explícita. A prova pode citar a região,
países latino-americanos ou uma regra global aplicável, desde que a fonte
oficial também ofereça uma rota de candidatura utilizável.

Portfólio, localização de alumni e presença comercial não comprovam acesso.
Programas regionais já auditados permanecem deduplicados. Veículos de
investimento recorrente seguem para `funds/`. Benefícios permanentes,
comunidades e plataformas sem percurso definido são excluídos.

## Fontes e workers congelados

| Worker | Base | Fonte | Objetivo |
| --- | --- | --- | --- |
| `worker-for-01` | Estados Unidos | Google for Startups Accelerator: AI First, Latin America | Validar acesso regional e atividade |
| `worker-for-02` | Estados Unidos | Founder Institute Latin America | Validar programas locais e candidatura |
| `worker-for-03` | Estados Unidos | AWS Generative AI Accelerator | Verificar regra global e coorte atual |
| `worker-for-04` | Estados Unidos | Berkeley SkyDeck | Verificar seleção global e programa estruturado |
| `worker-for-05` | Estados Unidos | Y Combinator | Verificar candidatura global e turma atual |
| `worker-for-06` | Estados Unidos | Alchemist Accelerator | Verificar programa global B2B e atividade |
| `worker-for-07` | Estados Unidos | 500 Global Flagship Accelerator | Separar programa e veículo de investimento |
| `worker-for-08` | Estados Unidos | Techstars Anywhere | Verificar programa remoto e acesso global |
| `worker-for-09` | Estados Unidos | Microsoft for Startups Founders Hub | Aplicar a fronteira de plataforma de benefícios |
| `worker-for-10` | Estados Unidos | NVIDIA Inception | Aplicar a fronteira de programa permanente |
| `worker-for-11` | Suíça | Seedstars | Validar programa para mercados emergentes e acesso regional |
| `worker-for-12` | Singapura | Antler Residency | Separar residência estruturada e investimento recorrente |

## Ownership e redução

Cada worker escreve somente em
`research/epic-62/foreign/shards/<worker-id>/`. O coordenador reduz apenas os
shards desta partição, em ordem determinística, sem incorporar outras
auditorias. Toda elegibilidade exige evidência oficial de programa estruturado,
atividade, seleção externa, acesso latino-americano e candidatura.

## Gates

1. este plano, a matriz e o manifesto são versionados antes da coleta;
2. cada fonte recebe estado, justificativa e ownership;
3. cada candidato recebe decisão e evidência por afirmação;
4. acesso latino-americano nunca é inferido por portfólio;
5. duplicados e encaminhamentos recebem destino canônico;
6. a redução é repetida com hashes idênticos;
7. todos os links inventariados passam por auditoria;
8. nenhum perfil é criado;
9. elegíveis seguem para revisão independente na issue #77.
