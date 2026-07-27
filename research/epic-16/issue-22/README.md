# Issue 22: consolidação brasileira

Data de corte e congelamento: 2026-07-27.

Este diretório é a fonte canônica de consolidação das issues #18, #19, #20 e
#21. A execução reuniu 314 registros de entrada e resolveu
colisões de domínio, aliases, razão social, gestor e veículo em
297 candidatos canônicos.

As fontes de descoberta foram preservadas, mas não foram usadas para comprovar
elegibilidade. O arquivo local de startups não foi usado para descoberta,
priorização, comprovação ou decisão.

## Método

1. Namespaciar todas as fontes e evidências pela issue de origem.
2. Unir IDs repetidos, aliases exatos e registros que apontam para o mesmo
   perfil já publicado.
3. Resolver manualmente Fundepar/Fundep Participações e RV/RVC.
4. Manter gestor, veículo e programa corporativo como entidades diferentes.
5. Dar precedência a perfil já publicado e, na ausência dele, à decisão oficial
   mais forte e recente.
6. Exigir motivo, responsável e próxima ação para toda
   `evidência insuficiente`.

## Totais canônicos

| Decisão | Total |
|---|---:|
| `elegível` | 22 |
| `duplicado` | 24 |
| `ecossistema` | 9 |
| `inativo` | 1 |
| `evidência insuficiente` | 148 |
| `excluído` | 93 |
| **Total** | **297** |

Todos os candidatos estão com status `decidido` e decisão não nula. Os
148 casos de evidência insuficiente possuem responsável e
próxima ação.

## Lista brasileira elegível congelada

Esta é a entrada canônica para a issue #23. A inclusão nesta lista não publica
perfis.

| ID canônico | Nome | Tipo | Domínio | Relação |
|---|---|---|---|---|
| `cand-acolab-ventures` | Açolab Ventures | veículo | `arcelormittal.com.br` | entidade canônica independente |
| `cand-ahead-ventures-gestao-de-recursos-e-consultoria-ltda` | Ahead Ventures Gestão De Recursos E Consultoria Ltda. | gestor | `aheadventures.com.br` | entidade canônica independente |
| `cand-amaz` | AMAZ Aceleradora de Impacto | organização | `amaz.org.br` | entidade canônica independente |
| `cand-arapy-fundepar` | Arapy | veículo | `fundep.ufmg.br` | gerido por `cand-fundepar-gestao-de-investimentos-ltda` |
| `cand-edp-ventures` | EDP Ventures | programa corporativo | `edp.com` | entidade canônica independente |
| `cand-eurofarma-ventures` | Eurofarma Ventures | veículo | `eurofarma.com` | entidade canônica independente |
| `cand-fip-nordeste-capital-semente` | FIP Nordeste Capital Semente | veículo | `fipnordeste.com` | gerido por `cand-triaxis-capital` |
| `cand-fundepar-gestao-de-investimentos-ltda` | Fundepar | gestor | `fundepar.com.br` | entidade canônica independente |
| `cand-fundo-inovabra-i` | Fundo inovabra I | veículo | `inovabra.com.br` | entidade canônica independente |
| `cand-gerdau-next-ventures` | Gerdau Next Ventures | programa corporativo | `gerdau.com.br` | entidade canônica independente |
| `cand-in3` | IN3 | gestor | `intr3s.com.br` | entidade canônica independente |
| `cand-invest-tech-participacoes-e-investimentos-s-a` | Invest Tech Participações E Investimentos S.A. | gestor | `investtech.com.br` | entidade canônica independente |
| `cand-msw-capital-gestao-de-recursos-ltda` | Msw Capital Gestao De Recursos Ltda. | gestor | `mswcapital.com.br` | entidade canônica independente |
| `cand-panvel-ventures` | Panvel Ventures | programa corporativo | `grupopanvel.com.br` | entidade canônica independente |
| `cand-raio-capital-consultoria-e-investimentos-ltda` | Raio Capital Consultoria E Investimentos Ltda. | gestor | `raio.vc` | entidade canônica independente |
| `cand-rv-randoncorp` | Randon Ventures (RV) | organização | `randon.ventures` | entidade canônica independente |
| `cand-rd-saude-ventures` | RD Saúde Ventures | programa corporativo | `rdsaude.com.br` | entidade canônica independente |
| `cand-rx-ventures` | RX Ventures | veículo | `lojasrennersa.com.br` | entidade canônica independente |
| `cand-sinergia-investimentos` | Sinergia Investimentos | programa corporativo | `sinergiainvestimentos.jornadaamazonia.org.br` | entidade canônica independente |
| `cand-slc-ventures` | SLC Ventures | programa corporativo | `slcagricola.com.br` | entidade canônica independente |
| `cand-triaxis-capital` | Triaxis Capital | gestor | `triaxiscapital.com` | entidade canônica independente |
| `cand-vivo-ventures` | Vivo Ventures | veículo | `telefonica.com.br` | gerido por `cand-wayra` |


## Colisões resolvidas

| Canônico | Registros de origem consolidados | Decisão |
|---|---|---|
| `cand-astella` — Astella | #18 `cand-astella`, #19 `cand-astella` | `duplicado` |
| `cand-canary` — Canary | #18 `cand-canary`, #19 `cand-canary` | `duplicado` |
| `cand-crescera-venture` — Crescera Venture Ltda. | #18 `cand-crescera-investimentos-ltda`, #19 `cand-crescera-venture` | `duplicado` |
| `cand-dna-capital` — DNA Capital | #18 `cand-dna-capital-consultoria-ltda`, #19 `cand-dna-capital` | `evidência insuficiente` |
| `cand-domo-invest-gestora-de-ativos-financeiros-e-valores-mobiliarios-ltda` — Domo Invest Gestora De Ativos Financeiros E Valores Mobiliarios Ltda. | #18 `cand-domo-invest`, #18 `cand-domo-invest-gestora-de-ativos-financeiros-e-valores-mobiliarios-ltda` | `duplicado` |
| `cand-edp-ventures` — EDP Ventures | #18 `cand-edp-ventures`, #20 `cand-edp-ventures` | `elegível` |
| `cand-ey` — EY | #18 `cand-ernst-young-assessoria-empresarial-ltda`, #18 `cand-ey` | `excluído` |
| `cand-finep` — Finep | #18 `cand-financiadora-de-estudos-e-projetos-finep`, #19 `cand-finep` | `ecossistema` |
| `cand-fip-nordeste-capital-semente` — FIP Nordeste Capital Semente | #19 `cand-fip-nordeste-capital-semente`, #21 `cand-fip-nordeste-capital-semente` | `elegível` |
| `cand-fundepar-gestao-de-investimentos-ltda` — Fundepar | #18 `cand-fundepar-gestao-de-investimentos-ltda`, #21 `cand-fundepar` | `elegível` |
| `cand-gef-brasil-investimentos` — GEF Brasil Investimentos Ltda. | #18 `cand-gef-brasil-investimentos-ltda`, #19 `cand-gef-brasil-investimentos` | `evidência insuficiente` |
| `cand-general-atlantic-representacoes-ltda` — General Atlantic Representacoes Ltda. | #18 `cand-general-atlantic`, #18 `cand-general-atlantic-representacoes-ltda` | `evidência insuficiente` |
| `cand-kptl` — KPTL | #18 `cand-kptl-investimentos-ltda`, #19 `cand-kptl` | `duplicado` |
| `cand-rv-randoncorp` — Randon Ventures (RV) | #18 `cand-rvc-venture-capital-participacoes-e-investimentos-ltda`, #20 `cand-rv-randoncorp` | `elegível` |
| `cand-triaxis-capital` — Triaxis Capital | #18 `cand-triaxis-capital-ltda`, #19 `cand-triaxis-capital`, #21 `cand-triaxis-capital` | `elegível` |
| `cand-wayra` — Wayra | #18 `cand-wayra-brasil-desenvolvedora-e-apoiadora-de-projetos-ltda`, #20 `cand-wayra` | `duplicado` |


Decisões estruturais:

- Fundepar, Fundep Participações e a razão social da gestora formam um único
  canônico. Arapy permanece como veículo separado e aponta para a gestora.
- Triaxis Capital e FIP Nordeste Capital Semente permanecem em perfis separados;
  o veículo aponta para a gestora.
- RVC é preservada como razão social/alias de Randon Ventures (RV).
- Vivo Ventures permanece separado da Wayra. A Wayra já possui perfil publicado
  e é tratada como plataforma/gestora relacionada, não como o mesmo veículo.
- Seed4Science permanece separado da Fundepar e continua com evidência
  insuficiente; portanto, não integra a lista congelada.

## Domínios compartilhados revisados

Domínio igual não foi usado isoladamente para unir entidades. Permanecem
separados:

- gestora, veículos e programas ligados a BNDES, Finep, Sebrae, Fundepar e
  Triaxis;
- Banco do Brasil e BB Gestão de Recursos;
- Banco BTG Pactual e BTG Pactual Asset Management;
- as pessoas jurídicas de Angra Partners, Mantiq e Matterhorn;
- as gestoras Vinci Capital e Vinci Gestora.

EY e sua razão social foram consolidadas em `cand-ey`. Finep e sua razão social
foram consolidadas em `cand-finep`. Os demais compartilhamentos de domínio
representam entidades jurídicas, programas ou veículos diferentes; nos casos
sem comprovação suficiente, a decisão e a próxima ação permanecem explícitas.

## Artefatos

- `source-inventory.jsonl`: 92 fontes e recortes
  preservados;
- `candidates.jsonl`: 297 candidatos canônicos;
- `evidence.jsonl`: 95 evidências preservadas e
  remapeadas;
- `run-manifest.jsonl`: uma execução concluída e cinco tarefas.

Não foram criados perfis em `funds/` ou `ecosystem/`.
