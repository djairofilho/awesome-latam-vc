# Issue 211: descoberta reversa por rodadas brasileiras

## Escopo

Este shard cobre anúncios de rodadas de startups brasileiras entre 2023-07-30 e 2026-07-30. Notícias e bases públicas serviram somente para descoberta. A inclusão de um candidato exigiu confirmação do nome e da participação em página oficial da startup ou do investidor.

A pesquisa não usou a CVM nem arquivos locais de startups. Uma rodada isolada confirma investimento direto, mas não prova recorrência, disponibilidade contínua para o Brasil nem elegibilidade final. Por isso, todos os candidatos permanecem em `researching`, com `decision: null` e `recurring_vc: null`.

## Estratégia auditável

Foram executados dois passos com vocabulários diferentes:

1. Português, com foco em `capta`, `rodada`, `investidores`, `startup brasileira` e `rodada seed`, incluindo buscas direcionadas a Exame, Startups, NeoFeed e Fintechs.
2. Inglês, com foco em `Brazil startup raises`, `funding round`, `seed`, `led by` e `investors`, incluindo buscas direcionadas a TechCrunch, LatamList e Contxto.

As consultas centrais foram:

- `site:startups.com.br capta rodada investidores startup 2025 Brasil`
- `site:neofeed.com.br startup capta rodada investidores 2024`
- `site:exame.com startup brasileira capta rodada 2023 investidores`
- `site:fintechs.com.br rodada investimento startup 2026 Brasil`
- `Brazil startup raises seed 2025 "led by" venture official announcement`
- `site:techcrunch.com Brazilian startup raises 2024 seed investors`
- `site:latamlist.com Brazil startup raised 2025 investors`
- `site:contxto.com Brazil startup funding round 2023 investors`

O inventário registra as fontes efetivamente levadas até a confirmação. Resultados sem anúncio oficial correspondente ficaram documentados como lacunas, sem virar candidatos.

## Rodadas confirmadas

| Data | Startup | Descoberta | Confirmação oficial | Resultado |
| --- | --- | --- | --- | --- |
| 2023-08-31 | Cumbuca | [Exame](https://exame.com/bussola/primeira-startup-brasileira-voltada-para-o-finshare-capta-r-15-milhoes/) | [Cumbuca](https://www.cumbuca.com/) | Lightspeed confirmada como investidora; página oficial não associa a uma data ou rodada específica |
| 2024-08-22 | Magie | [TechCrunch](https://techcrunch.com/2024/08/22/lux-capital-made-its-first-investment-in-brazil-a-4m-seed-for-ai-fintech-magie/) | [Magie](https://magie.com.br/depoimentos) | Lux Capital confirmada como líder da segunda rodada; data completa não publicada na página oficial |
| 2025-02-05 | Neofin | [GlobeNewswire](https://www.globenewswire.com/news-release/2025/02/05/3021495/0/en/Neofin-Secures-7M-Seed-Round-to-Revolutionize-Accounts-Receivable-in-Brazil-with-AI-Powered-Solutions.html) | [Neofin](https://www.neofin.com.br/release/janeiro-2025) | Seis candidatos novos confirmados; Quona Capital e Norte Ventures já estavam no baseline |
| 2025-09-30 | BotCity | [Exame](https://exame.com/negocios/baba-de-robos-startup-brasileira-capta-r-65-milhoes-de-investidores-globais/) | [BotCity](https://blog.botcity.dev/pt-br/2025/09/30/levantamos-r-65-milhoes-para-governar-automacoes-criadas-por-ai/) | Quatro candidatos confirmados, sendo Upload repetida; Astella já estava no baseline |
| 2026-06-21 | Loopia | [Exame](https://exame.com/inteligencia-artificial/loopia-capta-r-65-milhoes-em-rodada-seed-para-escalar-agentes-de-ia-no-e-commerce-brasileiro/) | [Parceiro Ventures](https://parceiroventures.com/) | Parceiro Ventures confirmada por portfólio e notícia oficial |

Os anúncios descrevem rodadas de venture ou seed, mas não divulgam o instrumento jurídico. Nenhum evento foi classificado como dívida ou grant sem evidência explícita.

## Resultado e deduplicação

Foram percorridas 10 fontes, cobrindo cinco rodadas. O resultado contém 12 candidatos e 13 registros de evidência oficial:

- Upload Ventures, 17-Sigma, 1616V, Farout, BFF e Canaan, a partir da Neofin;
- Four Rivers, Firestreak Ventures, Sagol Holdings e Upload Ventures, a partir da BotCity;
- Lux Capital, a partir da Magie;
- Parceiro Ventures, a partir da Loopia;
- Lightspeed, a partir da Cumbuca.

O baseline tinha 152 perfis de identidade. Quona Capital, Norte Ventures e Astella foram reconhecidas no baseline e não foram recriadas. Nenhum dos 12 candidatos novos coincidiu com o índice de identidade ou com os candidatos anteriores.

## Separação por papel

- Fundos e organizações de investimento: somente nomes confirmados em anúncio oficial viraram candidatos.
- Programas e aceleradoras: Y Combinator e Scale Up by Endeavor aparecem no anúncio da BotCity, mas foram separados dos candidatos a fundo.
- Anjos: pessoas citadas nas rodadas da Neofin e da BotCity foram mantidas fora deste shard.
- Parceiros: Serasa aparece como parceira da Neofin, não como investidora.
- Assessoria: prestadores e assessores encontrados em materiais adjacentes não foram tratados como participantes da rodada.
- Dívida e grants: nenhum caso explicitamente divulgado nas cinco rodadas.

## Lacunas e limites

- Supera Capital aparece na descoberta sobre a Cumbuca, mas não foi confirmada na página oficial inspecionada.
- Funses I, ACE Founders e BVC Latam aparecem em cobertura sobre a Loopia, mas não foram confirmados pela fonte oficial inspecionada.
- As páginas oficiais da Cumbuca e da Magie confirmam a relação de investimento, mas não fornecem data completa para a atividade. Esses candidatos ficam com atividade `unknown`.
- Uma única rodada não comprova recorrência. Mesmo Upload Ventures, encontrada em duas rodadas, continua sem decisão porque a identidade, a estratégia e o acesso atual ao Brasil precisam de validação própria.
- Mecanismos de busca não garantem cobertura total: indexação incompleta, páginas dinâmicas, paywalls, anúncios removidos e investidores não divulgados geram falsos negativos.
- A expressão “rodada seed” não determina sozinha se o instrumento foi participação societária, mútuo conversível, SAFE ou outra estrutura.
- A ligação com o Brasil foi classificada como incidental nesta etapa: houve investimento confirmado em startup brasileira, mas isso não basta para afirmar mandato recorrente ou disponibilidade nacional.

Este shard é uma amostra auditável de descoberta reversa, não uma declaração de totalidade do universo brasileiro.
