# Auditoria de seleções públicas de venture capital

Este diretório registra a primeira onda da
[#19](https://github.com/djairofilho/awesome-latam-vc/issues/19), conforme o
contrato da #17. A data de corte e de acesso é 2026-07-27.

## Resultado

- 9 fontes ou recortes inventariados.
- 5 recortes concluídos.
- 4 recortes parciais.
- 40 candidatos canônicos.
- 40 evidências oficiais.
- 17 gestores.
- 18 veículos.
- 3 instituições públicas ou de apoio.
- 2 programas de seleção ou investimento indireto.

As decisões ficaram assim:

| Decisão | Total |
| --- | ---: |
| `evidência insuficiente` | 27 |
| `duplicado` | 5 |
| `ecossistema` | 5 |
| `excluído` | 3 |
| `elegível` | 0 |

Nenhum candidato foi marcado como elegível apenas por aparecer em uma seleção
pública.

## BNDES

O shard de fundos ativos percorreu integralmente as seções de Capital Semente e
Venture Capital da página oficial. Foram registrados 6 veículos e 7 gestores:

- Fundo Criatec 4, gerido por Crescera Venture e E, H & R Investimentos;
- GEF LatAm Climate Solutions, gerido pela GEF Brasil Investimentos;
- Astella Journey V, gerido pela Astella;
- Valor Opportunity, gerido pelo Valor Capital Group;
- Canary IV Brasil, gerido pela Canary;
- DNA Capital VC II, gerido pela DNA Capital.

O BNDES confirma tese, período de investimento e, quando divulgado, canal de
propostas. Astella, Canary, Crescera, KPTL e Valor Capital Group foram
deduplicados contra o baseline. Os demais gestores e veículos permanecem com
`evidência insuficiente` até a validação em páginas controladas pelos gestores.

O resultado final da Chamada de Clima registrou 5 fundos de equity e 2 fundos
de crédito. A página informa que seleção, diligência, contratação e aprovação
da subscrição são etapas diferentes. Por isso, os fundos de equity e seus
gestores permanecem pendentes. Os dois fundos de crédito foram excluídos da
fila de VC direto.

As requisições ao domínio BNDES respeitaram intervalo mínimo de 2 segundos.

## Finep

O `robots.txt` da Finep contém `Disallow: /` para todos os agentes. Nenhum
scraping automatizado foi executado no domínio.

As fontes da Finep foram localizadas por busca manual em páginas e PDFs
oficiais:

- investimento indireto e Programa Inovar;
- FIP Finep Startup I, com KPTL como gestora;
- FIP Primatec;
- resultado final do FIP Nordeste Capital Semente, com Triaxis Capital
  aprovada;
- chamada aberta do FIP Startup Inteligência Artificial.

O resultado da seleção do FIP Nordeste não comprova que o veículo foi
constituído ou iniciou investimentos. A chamada de IA ainda não apresentava
gestor selecionado no recorte consultado. Esses veículos permanecem com
`evidência insuficiente`.

## Sebrae

O sitemap público foi consultado com termos específicos de fundos, FIP,
FIC-FIP e capital. O resultado oficial de 2025 indicou o BTG Pactual para
estruturar e administrar um FIC-FIP dedicado ao Sistema Sebrae.

O FIC-FIP foi classificado como `excluído` porque é um fundo de cotas e não
investe diretamente em startups. A seleção do BTG para esse veículo não
comprova, isoladamente, atividade de venture capital direto.

A URL original do PDF redireciona atualmente para uma página genérica de
conteúdo. O resultado continua indexado em busca, mas precisa de uma URL oficial
estável.

## Distinção entre entidades

O arquivo [candidates.jsonl](candidates.jsonl) usa:

- `organização` para BNDES, Finep e Sebrae;
- `programa corporativo` para programas e processos de seleção, pois este é o
  rótulo disponível no schema atual;
- `gestor` para a entidade responsável pela gestão;
- `veículo` para cada fundo ou FIP.

Veículos com um único gestor identificado apontam para ele por
`canonical_candidate_id`. O Fundo Criatec 4 possui dois gestores e permanece
sem um único destino canônico.

## Lacunas e fila restante

- Validar os 12 gestores novos em sites próprios.
- Validar operação, acesso externo e vínculo atual dos 15 veículos pendentes.
- Revisitar o resultado da chamada de IA após a seleção do gestor.
- Confirmar constituição e início de operação do FIP Nordeste Capital Semente.
- Revisar manualmente os demais fundos da Finep, sem crawler.
- Encontrar URL estável para o resultado FIC-FIP do Sebrae.
- Abrir chamadas antigas do BNDES somente quando houver veículo ainda em
  período de investimento.

O [source-inventory.jsonl](source-inventory.jsonl) registra os recortes,
resultados e limites de acesso. O [evidence.jsonl](evidence.jsonl) separa
afirmações oficiais por entidade. O [run-manifest.jsonl](run-manifest.jsonl)
mantém os shards concluídos e a fila restante.

A execução continua como `em execução` porque há fontes parciais e validações
de gestores pendentes. O arquivo local de startups não foi usado para
descoberta, priorização, comprovação ou decisão.
