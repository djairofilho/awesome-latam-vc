# Worker 213 — listas públicas de eventos

Este shard audita listas públicas de investidores, jurados, palestrantes e participantes de eventos realizados ou anunciados entre 2024 e 2026. A data de corte é **2026-07-30**. Participação em evento é tratada somente como descoberta: todos os candidatos permanecem em `discovered` ou `researching`, com `decision: null`, e nenhum registro de evento foi incluído em `official_evidence_ids`.

## Estratégia auditável

Foram executadas duas passagens independentes:

1. **Listas gerais e agendas:** `investors`, `speakers`, `palestrantes`, `participants`, `attendees`, `lineup` e `programação`, cobrindo South Summit Brazil, Web Summit Rio, Startup Summit, CASE e Gramado Summit.
2. **Função no processo de investimento:** `LP forum`, `family office`, `pitch jury`, `judge`, `investment manager`, `general partner`, `manager selection` e `processo de investimento`, incluindo o Startup Investment Summit como evento setorial.

As páginas de evento são fontes terceiras em relação ao candidato. Mesmo quando controladas pelo organizador, elas não substituem site, tese, portfólio ou anúncio oficial da gestora.

## Classificação de papéis

- **Função de investimento:** GP, partner de VC, investment manager, head of investment ou organização apresentada nominalmente na lista de investidores gera candidato para validação.
- **Palestrante:** falar no evento, sem função institucional de investimento, não gera candidato.
- **Patrocinador ou parceiro:** logo em página de parceiros ou categoria de patrocínio não gera candidato.
- **Prestador:** escritório, consultoria, plataforma, empresa de tecnologia ou moderador sem mandato de investimento não gera candidato.
- **Outros tipos:** BR Angels, Poli Angels, Anjos do Brasil e GVAngels foram reconhecidas como redes de anjos; WOW como aceleradora; CVCs foram separados de gestores independentes. Esses nomes não foram convertidos em candidatos a fundo neste shard.

## Deduplicação

O cruzamento usou `catalog-baseline.jsonl`, `identity-index.jsonl`, `prior-candidates.jsonl` e os shards integrados #210–#212.

- **Perfis existentes:** Primus Ventures, Caravela Capital, Triaxis Capital, Canary e Astella.
- **Shard #212:** Sororitê Ventures, reconciliada por nome, domínio e `Sororitê Fund 1`.
- **Memória insuficiente anterior:** AMZ Venture Capital, Quartzo Capital e Vinci Partners.
- **Leads sem correspondência:** 30N Ventures, Maromar Investimentos, Santa Maria Investment Group, FHE Ventures, Seedstars e Lean VC.

Aliases de evento foram preservados, mas nenhuma colisão foi decidida nesta etapa.

## Cobertura e lacunas

- 12 superfícies inventariadas: 9 completas, 2 parciais e 1 indisponível.
- 15 candidatos: 6 sem correspondência, 3 com memória insuficiente, 5 perfis existentes e 1 candidato do shard #212.
- 18 evidências de descoberta, todas classificadas como `third_party` e `event`.
- O Startup Summit não expôs programação no conteúdo acessado.
- A página do CASE retornou HTTP 403; apenas o trecho indexado foi auditável.
- O arquivo nominal completo do Gramado Summit 2025/2026 não permaneceu disponível na superfície oficial vigente.
- A agenda do Startup Investment Summit é futura em relação ao corte; anúncio não comprova presença efetiva.
- South Summit Brazil publicou totais de fundos e investidores sem lista nominal completa; os totais não foram transformados em candidatos.

Não houve consulta à CVM nem leitura do arquivo local de startups.

## Validação

Cada linha deve validar contra seu schema em `research/epic-207/schemas/`. A validação local também deve verificar unicidade de IDs, referências entre os quatro JSONL, `decision: null`, ausência de evidência oficial derivada apenas de evento, UTF-8 e mojibake. O validador agregado da epic exige artefatos de consolidação fora do escopo deste worker.
