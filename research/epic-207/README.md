# Contrato de auditoria de fundos com acesso ao Brasil

Este diretório é o artefato canônico da issue
[#208](https://github.com/djairofilho/awesome-latam-vc/issues/208). Ele define
como a epic [#207](https://github.com/djairofilho/awesome-latam-vc/issues/207)
descobre, valida, decide e publica fundos com atuação verificável no Brasil.

A auditoria complementa a epic #16. Fontes já percorridas naquela epic formam
o baseline e não contam como novas famílias de descoberta.

## Resultado que a epic pode declarar

O resultado será uma **cobertura auditada na data de corte**, limitada às
fontes e aos recortes registrados no inventário. A epic não pode declarar que
encontrou literalmente todos os fundos existentes.

Cada execução registra:

- data de corte;
- catálogo usado como baseline;
- fontes planejadas e efetivamente percorridas;
- consultas e vocabulários utilizados;
- bloqueios e lacunas;
- decisões por candidato;
- métricas de cobertura, sobreposição e rendimento.

## Unidade canônica

O perfil publicado representa a organização investidora que opera de forma
recorrente. Gestora, marca, veículo e programa de investimento permanecem
entidades distintas durante a pesquisa.

| Entidade | Campo de identidade | Regra |
| --- | --- | --- |
| Organização investidora | `candidate_id` | Unidade canônica da fila e possível perfil |
| Gestora | `manager_id` | Entidade que administra ou decide pelo veículo |
| Marca | `brand_id` | Nome público atual e aliases |
| Veículo | `vehicle_id` | Fundo, FIP, corporate fund ou outro veículo específico |
| Programa | `program_id` | Programa recorrente de investimento operado pela organização |
| Sucessor | `successor_id` | Organização que assumiu uma operação anterior |

O domínio oficial normalizado inicia a deduplicação, mas não decide identidade
sozinho. O reducer também considera operador, equipe, portfólio oficial,
redirects, relação gestor-veículo, aquisições e sucessões.

Veículos diferentes administrados pela mesma gestora não são unidos
automaticamente. Uma gestora também não recebe dois perfis ativos apenas porque
opera mais de um veículo. O revisor decide a unidade publicável com base no
modelo operacional e na forma como a organização se apresenta oficialmente.

`candidate_id`, `manager_id`, `brand_id`, `vehicle_id` e `program_id` são
imutáveis depois do primeiro freeze. Mudanças de nome entram em `aliases`.

## Recorte geográfico

Cada candidato recebe uma das relações abaixo:

- `based_in_brazil`: a organização ou sua operação principal está baseada no
  Brasil;
- `accessible_to_brazil`: a organização está baseada fora do Brasil, mas
  mantém acesso recorrente e explícito ao mercado brasileiro;
- `brazil_incidental`: existe apenas um investimento brasileiro isolado, sem
  evidência de acesso recorrente;
- `brazil_unconfirmed`: a relação com o Brasil ainda não foi comprovada.

`based_in_brazil` e `accessible_to_brazil` podem sustentar elegibilidade.
`brazil_incidental` e `brazil_unconfirmed` não sustentam publicação nesta
auditoria.

País-base e geografia de investimento são campos independentes. Um fundo
estrangeiro não vira brasileiro por ter uma empresa brasileira no portfólio.

## Elegibilidade

Um candidato é elegível somente quando fontes oficiais atuais confirmam:

1. investimento de capital diretamente em startups;
2. operação recorrente de venture capital, corporate venture capital,
   coinvestimento, accelerator fund, studio fund ou veículo equivalente;
3. atividade oficial nos 24 meses anteriores à data de corte;
4. relação `based_in_brazil` ou `accessible_to_brazil`;
5. identidade suficiente para evitar duplicação de gestora, marca e veículo.

Uma página de portfólio isolada pode confirmar empresas investidas, mas não
comprova sozinha o modelo operacional atual. Uma rodada isolada também não
comprova recorrência ou acesso contínuo ao Brasil.

Não inferir:

- cheque;
- estágio;
- tese;
- preferência por liderança;
- frequência de investimento;
- abertura a fundadores externos;
- atividade atual;
- geografia declarada.

Informação ausente permanece `not_disclosed` ou `unconfirmed`, conforme o
campo. Ausência pública não se transforma em conclusão negativa.

## Fronteiras de categoria

Use `funds/` quando a organização decide e aporta capital agrupado diretamente
em startups de forma recorrente.

Encaminhe:

- programas estruturados de aceleração sem veículo elegível para a epic #62;
- redes, clubes e syndicates de investidores membros para a epic #63;
- plataformas de captação e intermediação para a epic #64;
- agências e programas públicos para a epic #65;
- fundos que investem somente em outros fundos para a categoria de ecossistema
  aplicável ou para backlog explícito.

Uma organização híbrida pode possuir mais de uma rota, mas cada perfil
representa uma categoria e uma função. A decisão registra o destino de cada
rota sem duplicar a mesma atividade.

## Status e decisões

Status operacional:

1. `discovered`: identificado, ainda sem validação suficiente;
2. `researching`: validação oficial em andamento;
3. `decided`: decisão revisada;
4. `published`: perfil incorporado ao catálogo.

Decisões:

- `eligible`;
- `duplicate`;
- `routed_accelerators`;
- `routed_angel_networks`;
- `routed_funding_platforms`;
- `routed_public_programs`;
- `routed_other`;
- `inactive`;
- `insufficient_evidence`;
- `excluded`.

`discovered` e `researching` exigem `decision: null`. `decided` e `published`
exigem uma decisão. Toda decisão diferente de `eligible` exige motivo.

`duplicate` exige `canonical_candidate_id` ou `canonical_profile`.
`insufficient_evidence` exige responsável e próxima ação. Nenhum candidato
indeciso chega ao freeze.

## Famílias de fontes

A descoberta usa famílias independentes:

1. `allocators`: DFIs, investidores institucionais, investidores-âncora,
   fundos de fundos e seleções de gestores;
2. `rounds`: notícias de rodadas, comunicados de startups e anúncios de
   investidores;
3. `launches`: lançamentos, primeiros fechamentos, novos veículos e primeiros
   investimentos;
4. `events`: listas públicas de investidores, participantes e palestrantes;
5. `sector_maps`: mapas de climate tech, impacto, bioeconomia, agtech, fintech,
   healthtech, deep tech, proptech, SaaS e outros setores;
6. `regional_sources`: universidades, parques, hubs, associações e imprensa
   regional;
7. `official_portfolios`: portfólios e notícias oficiais usados para confirmar
   identidade e atividade;
8. `foreign_access`: fontes oficiais que comprovem acesso recorrente ao Brasil.

ABVCAP, Endeavor, Shizune, LAVCA, BNDES, Finep, Sebrae e outras fontes já
percorridas na #16 são classificadas no baseline. Elas podem servir como
benchmark ou delta, mas não contam automaticamente como nova descoberta.

Terceiros podem descobrir candidatos. Categoria, investimento direto,
atividade e acesso ao Brasil exigem evidência oficial para elegibilidade.

## Política de 90% a 95% e CVM

O planejamento reserva 90% a 95% do esforço de pesquisa para fontes abertas
não regulatórias. Consultas à CVM são pontuais e ocupam no máximo 10% dos
candidatos únicos.

A execução mede esforço por tarefas concluídas no `run-manifest.jsonl`. Uma
tarefa possui uma única `research_channel`: `non_cvm` ou `cvm`. Tempo humano
não é usado como denominador porque não é reproduzível entre workers.

As métricas operacionais são:

```text
cvm_query_rate = candidatos_com_consulta_cvm / candidatos_únicos
non_cvm_task_share = tarefas_non_cvm_concluídas / tarefas_de_pesquisa_concluídas
cvm_task_share = tarefas_cvm_concluídas / tarefas_de_pesquisa_concluídas
```

O denominador de `cvm_query_rate` é a quantidade de candidatos canônicos depois
da deduplicação da #216. Aliases e duplicatas não aumentam o denominador. O
limite inteiro é:

```text
max_cvm_candidates = floor(candidatos_canônicos * 0.10)
```

Regras obrigatórias:

- 100% dos candidatos nascem de uma fonte não-CVM;
- `cvm_query_rate` deve ser menor ou igual a 10%;
- `non_cvm_task_share` deve ser maior ou igual a 90%;
- `cvm_task_share` deve ser menor ou igual a 10%;
- 5% a 10% é faixa de planejamento, não quota mínima;
- zero consulta CVM é um resultado válido;
- nenhuma consulta é criada apenas para alcançar um percentual;
- toda consulta ocorre depois da descoberta e da validação oficial inicial;
- a consulta precisa responder uma pergunta específica ainda não resolvida;
- ausência de resultado na CVM não exclui automaticamente;
- não há varredura ampla, scraping ou redistribuição de linhas brutas.

A CVM pode ajudar a resolver:

- identidade jurídica;
- nome da gestora;
- relação entre gestor e veículo;
- situação regulatória quando ela for relevante para uma afirmação publicada;
- divergência entre marca pública e entidade legal.

A CVM não comprova:

- tese de venture capital;
- atividade recente;
- recorrência;
- acesso a startups;
- abertura a fundadores;
- acesso ao Brasil;
- elegibilidade editorial.

Cada consulta registra:

| Campo | Conteúdo |
| --- | --- |
| `candidate_id` | Candidato já descoberto fora da CVM |
| `question` | Pergunta específica que motivou a consulta |
| `searched_identifier` | Nome, CNPJ, gestor ou veículo consultado |
| `reference` | URL ou referência oficial |
| `accessed_on` | Data da consulta |
| `minimum_fact` | Fato mínimo confirmado |
| `divergence` | Divergência encontrada ou `null` |
| `outcome` | Decisão ou próxima ação |

Se o teto de 10% for atingido com casos ainda pendentes, a execução para e
exige decisão explícita na epic. O worker não amplia o teto automaticamente.

## Evidência

Cada evidência registra:

- `evidence_id`;
- sujeito e ID ao qual se aplica;
- URL, título, publicador e tipo de fonte;
- data de publicação, quando disponível;
- data observada do fato;
- data de acesso;
- afirmações atômicas confirmadas, refutadas ou não divulgadas;
- localizador;
- resumo factual parafraseado.

Tipos oficiais aceitos:

- `official_website`;
- `official_thesis`;
- `official_portfolio`;
- `official_application`;
- `official_announcement`;
- `official_filing`;
- `official_regulator`;
- `official_document`.

Notícias, diretórios, eventos e mapas usam tipos de descoberta. Eles não
substituem evidência oficial nos gates de elegibilidade.

Atividade recente precisa de `observed_on` dentro da janela de 24 meses e de
uma fonte oficial. A data de acesso de uma página sem data não prova atividade.

## Execução paralela

Cada sub-issue usa branch e worktree próprios quando produzir arquivos.
Workers escrevem somente em:

```text
research/epic-207/brazil/shards/<worker-id>/
```

Um `worker_id` possui exatamente um `shard_path`. Dois workers nunca escrevem
no mesmo arquivo. O reducer é o único escritor dos artefatos canônicos.

Limites operacionais:

- até quatro agentes ativos, incluindo o coordenador;
- até duas requisições simultâneas por domínio;
- intervalo mínimo de 500 ms por domínio;
- cache obrigatório pela URL final;
- até quatro tentativas para `429` e `5xx`, com backoff;
- navegador somente para página pública dependente de JavaScript;
- respeito a `robots.txt`, termos, autenticação, CAPTCHA e WAF;
- bloqueios viram pendência manual, sem tentativa de evasão.

Descoberta é particionada por família de fonte. Depois da redução, validação é
particionada por:

```text
sha256(candidate_id) mod 3
```

Validação deve ser executada por agente diferente daquele que descobriu o
candidato sempre que possível.

## Artefatos previstos

A issue #209 cria e valida:

- `source-inventory.jsonl`;
- `run-manifest.jsonl`;
- `candidates.jsonl`;
- `evidence.jsonl`;
- `identity-resolution.jsonl`;
- `coverage-matrix.jsonl`;
- `cvm-query-log.jsonl`;
- `review-sample.jsonl`;
- `audit-report.json`.

Cada linha JSONL é um objeto UTF-8 independente. IDs são estáveis. Referências
órfãs, IDs duplicados, decisões nulas no freeze e ownership concorrente são
erros de validação.

## Revisão independente e falsos negativos

A revisão cobre:

- 100% dos elegíveis;
- 100% dos encaminhados e híbridos;
- 100% dos candidatos com consulta CVM;
- amostra determinística de pelo menos 20% das exclusões.

Se uma exclusão amostrada estiver errada, revisar 100% do estrato de decisão ou
da família de fonte afetada.

O auditor de falsos negativos recebe o contrato e as fontes proibidas, mas não
recebe a lista consolidada antes da busca cega. Deve usar vocabulário diferente
e pelo menos duas famílias não usadas pelos workers. Novo elegível retorna para
identidade e validação antes do freeze.

## Freeze e publicação

O freeze exige:

- fontes planejadas em `complete` ou `gap_justified`;
- todos os candidatos decididos ou com pendência explícita;
- zero duplicata ou cluster de identidade sem destino;
- achados da revisão reconciliados;
- manifesto final com SHA-256, data de corte e totais por decisão;
- zero inconsistência crítica ou alta sem decisão.

Somente depois do freeze a publicação cria exatamente
`ceil(elegíveis_novos / 10)` lotes. Cada candidato congelado aparece uma vez.
Preparação de perfis pode ocorrer em worktrees paralelos, mas índices,
traduções, exports, geração e merges possuem integrador único.

## Métricas de fechamento

Relatar:

- fontes planejadas e estados terminais;
- candidatos e elegíveis por família;
- rendimento marginal por onda;
- sobreposição entre famílias;
- candidatos encontrados por uma única família;
- proporção encontrada por duas ou mais famílias;
- curva acumulada de descoberta;
- consultas CVM e `cvm_query_rate`;
- novos elegíveis encontrados pela busca cega;
- exclusões revisadas por estrato;
- correspondência entre manifesto e publicação.

Condição de saturação:

1. pelo menos cinco famílias novas concluídas;
2. duas passagens independentes finais com no máximo um novo elegível cada;
3. nenhum candidato de alta prioridade pendente;
4. busca cega reconciliada;
5. zero inconsistência crítica ou alta aberta.

Essa condição sustenta cobertura auditada. Ela não transforma uma amostra de
fontes públicas em prova de totalidade.
