# Issue 215: acesso estrangeiro recorrente ao Brasil

## Escopo e regra de evidência

Esta auditoria procura organizações de investimento sediadas fora do Brasil que mantenham acesso explícito e recorrente a founders brasileiros. Uma investida brasileira isolada foi tratada como `brazil_incidental`. A expressão “América Latina” também não foi expandida automaticamente para Brasil.

Para marcar `accessible_to_brazil`, a fonte oficial atual precisava mostrar pelo menos uma combinação forte de:

- tese ou página geográfica específica para o Brasil;
- equipe ou escritório no país;
- formulário, candidatura ou programa aberto a founders brasileiros;
- histórico oficial com várias investidas brasileiras.

Notícias serviram para descoberta. A confirmação veio de páginas controladas pelo investidor. Não foram usados dados da CVM nem arquivos locais de startups. Todos os candidatos continuam em `researching`, com `decision: null`.

## Duas passagens

### Passagem 1: leads de 210 a 212

Foram revisados os candidatos estrangeiros ou de base ainda indefinida dos shards de alocadores, rodadas e lançamentos. A busca combinou nome do investidor com `Brazil`, `São Paulo`, `portfolio`, `team`, `office`, `contact`, `apply`, `pitch` e `Latin America`.

| Lead | Resultado |
| --- | --- |
| 17Sigma | Acesso recorrente confirmado por tese latino-americana, escritório em São Paulo, várias investidas brasileiras e contato aberto. Duplicata do shard 211. |
| Quona Capital | Acesso recorrente confirmado por escritório em São Paulo, formulário e várias investidas brasileiras. Duplicata do baseline e do shard 210. |
| Kalei Ventures | Acesso recorrente confirmado por deal sourcing regional, portfólio em vários países incluindo Brasil e pitch aberto. Duplicata do baseline. |
| 1616 Ventures | Presença em São Paulo e apoio na América Latina confirmados, mas a página não prova histórico direto recorrente no Brasil. Duplicata do shard 211. |
| Mundi Ventures LatAm Fund I | A tese cobre América Latina e Caribe, mas o anúncio do veículo não nomeia Brasil nem oferece canal brasileiro permanente. A investida Sami, sozinha, não resolve recorrência. Duplicata do shard 212. |
| Firestreak Ventures | Site oficial sem tese, equipe ou canal brasileiro. A BotCity continua sendo ocorrência incidental. Duplicata do shard 211. |
| Lux Capital | O material da Magie descreve a primeira aposta da Lux no Brasil. Isso confirma uma ocorrência, não recorrência. Duplicata do shard 211. |
| Canaan, Farout, BFF, Four Rivers e Sagol Holdings | Permanecem incidentais ou sem identidade geográfica suficiente. Cada nome deriva de uma rodada brasileira isolada no shard 211. |
| Lightspeed | A Cumbuca confirma investimento, mas a auditoria não encontrou tese ou canal brasileiro permanente em fonte oficial atual. Duplicata do shard 211. |
| Upload Ventures | A triagem pública aponta operação em São Paulo; portanto não foi tratada como fundo estrangeiro nesta etapa. Duplicata do shard 211. |
| Parceiro Ventures e DNA Capital | A base operacional não ficou resolvida com segurança para classificá-las como estrangeiras; não foram promovidas. |
| Canary, Monashees, Good Karma, SP Ventures, Sororitê, Nido, BS2, L4 e Big Bets | Leads baseados no Brasil ou associados a operação brasileira, fora do recorte estrangeiro. |
| Valor Capital Group | Acesso Brasil já estava coberto e o perfil existe no baseline; não foi recriado. |

### Passagem 2: novas buscas

As novas consultas combinaram:

- `foreign venture capital fund Brazil office founders apply official`
- `venture capital São Paulo Latin America submit your pitch official`
- `Brazil portfolio official venture fund`
- `global VC Brazil location investment portfolio`
- `Latin America VC Brazil excluded official`

A passagem encontrou três candidatos novos com evidência oficial forte:

| Candidato | Base | Evidência de acesso |
| --- | --- | --- |
| Antler | Singapura | [Página Brasil](https://www.antler.co/location/brazil) com candidatura ativa, escritório em São Paulo, termos de investimento, equipe e mais de 30 empresas brasileiras |
| Prosus Ventures | Países Baixos | [Tese e portfólio](https://www.prosus.com/prosus-ventures) latino-americanos com várias empresas brasileiras e [aporte oficial na VOA Health](https://www.prosus.com/news-insights/2025/prosus-ventures-invests-in-voa-health-seed-round-to-advance-its-ai-powered-assistant) em 2025-03-24 |
| Accion Ventures | Estados Unidos | [Estratégia oficial](https://www.accion.org/how-we-work/investment-strategies/accion-impact-management/accion-ventures/) com quatro parceiros no Brasil, histórico global recorrente, pitch aberto e conteúdo brasileiro em 2026-04-27 |

## LATAM sem Brasil verificável

- [Fen Ventures](https://fenventures.com/) declara de forma explícita que investe na América Latina de língua espanhola e que o Brasil está excluído.
- [AVP Ventures](https://avpventures.com/) declara alcance latino-americano com foco na região andina, sem Brasil verificável na página inspecionada.
- Mundi Ventures LatAm Fund I cobre a região, mas a fonte do veículo não confirma acesso brasileiro permanente.

Esses casos não viraram candidatos novos. A separação evita usar `LATAM` como sinônimo de Brasil.

## Deduplicação

Os nomes e domínios foram comparados com o índice de identidade, candidatos anteriores e candidatos dos shards já integrados. Foram evitadas seis recriações relevantes:

- baseline: Quona Capital, Kalei Ventures, Valor Capital Group;
- shards integrados: 17Sigma, 1616 Ventures e Mundi Ventures LatAm Fund I.

Outras entidades do baseline, como 500 Global LatAm, Kaszek, Magma Partners, QED Investors, SoftBank Latin America Fund e Latitud Ventures, ficaram fora da lista de candidatos novos. Esta issue não reabre perfis já existentes.

## Limites

- A amostra não garante totalidade. Sites dinâmicos, portfólios sem filtro geográfico e páginas não indexadas podem ocultar acesso real.
- Escritório no Brasil sem investimento direto recorrente não basta.
- Portfólio com uma empresa brasileira sem tese, equipe ou canal local não basta.
- Formulário global sem menção ao Brasil não basta.
- Antler combina investimento e uma Residency. O programa foi registrado separadamente em `program_ids`; o candidato representa a organização de investimento.
- Accion Ventures é uma estratégia da Accion Impact Management e antes se chamava Accion Venture Lab. A resolução editorial dessa identidade fica para a validação final.
- Prosus Ventures é uma marca de investimento da Prosus e tem o alias histórico Naspers Ventures. A identidade final também precisa ser resolvida antes da publicação.

Resultado: 16 fontes oficiais percorridas, três candidatos novos, seis duplicatas relevantes e dois fundos LATAM explicitamente separados por falta de Brasil verificável.
