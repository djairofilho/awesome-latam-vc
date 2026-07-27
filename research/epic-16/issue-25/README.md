# México, América Central e Caribe

Este diretório registra o fechamento da
[#25](https://github.com/djairofilho/awesome-latam-vc/issues/25), conforme o
contrato da #17. A pesquisa foi limitada, reproduzível e congelada em
2026-07-27 para alimentar a
[#28](https://github.com/djairofilho/awesome-latam-vc/issues/28).

Não há alegação de exaustividade. O trabalho priorizou associações, órgãos
institucionais e uma fila curta de candidatos com alto sinal. Diretórios e
fontes de descoberta não foram usados como prova de elegibilidade.

## Resultado final

- 12 países cobertos por fonte institucional, associação regional ou lacuna
  explícita.
- 24 fontes inventariadas.
- 10 candidatos classificados e sem pendência de decisão.
- 5 candidatos `elegível`.
- 1 candidato `duplicado`.
- 1 candidato `ecossistema`.
- 3 candidatos com `evidência insuficiente`.
- 0 candidatos publicados nesta issue.
- 0 uso do arquivo local de startups.

## Lista elegível congelada para a #28

Data de corte: **2026-07-27**.

| ID canônico | Nome | Base | Geografia comprovada | Sinal de atividade |
| --- | --- | --- | --- | --- |
| `cand-caricaco-ventures` | Caricaco Ventures | Costa Rica | América Central e República Dominicana | CV2 lançado em maio de 2026; 27 empresas apoiadas e nova alocação anunciada |
| `cand-innogen-capital-ventures` | Innogen Capital Ventures | El Salvador | El Salvador e América Central | equipe atual e portfólio Delta I mantidos no site oficial em 2026 |
| `cand-parallel18-ventures` | Parallel18 Ventures | Porto Rico | Porto Rico, América Latina e startups internacionais operando a partir da ilha | plataforma de investimento reestruturada em 2025, Matching Fund e VCAP atuais |
| `cand-morro-ventures` | Morro Ventures | Porto Rico | Caribe e América Latina | Fund I com portfólio ativo e estratégia atual do Caribbean Fund |
| `cand-lightrock-gestora-de-recursos-ltda` | Lightrock | Reino Unido, com escritório no México | México e América Latina | escritório mexicano aberto em fevereiro de 2026 e investimentos locais divulgados |

A #28 deve tratar essa lista como congelada. Mudanças exigem nova evidência
oficial, revisão explícita da decisão e atualização da data de corte.

## Cobertura por país

| País | Fonte principal | Resultado |
| --- | --- | --- |
| México | AMEXCAP e fontes oficiais dos gestores | Lightrock elegível; BASF Venture Capital, Qualcomm Ventures e StepStone Group permaneceram insuficientes para o recorte |
| Belize | BELTRAIDE | apoio público e subvenções encontrados; nenhum gestor privado elegível confirmado |
| Costa Rica | PROCOMER e CAPCA | Caricaco Ventures elegível; Carao Ventures deduplicada contra perfil existente |
| El Salvador | Ministério da Economia, CAPCA e Innogen | Innogen Capital Ventures elegível |
| Guatemala | PRONACOM e CAPCA | ecossistema e escassez de financiamento documentados; nenhum novo gestor local com prova oficial suficiente |
| Honduras | SENPRENDE e CAPCA | programas públicos e capital-semente encontrados; nenhum novo gestor local elegível confirmado |
| Nicarágua | MIFIC e CAPCA | apoio público a PMEs encontrado; nenhum gestor privado elegível confirmado |
| Panamá | PROPANAMA e CAPCA | estudo e atores de ecossistema encontrados; nenhum novo gestor local passou pela validação oficial |
| Cuba | Projeto NAE e instituições públicas participantes | incubadoras e espaços de inovação encontrados; nenhum gestor privado recorrente confirmado |
| Haiti | CFI — Invest Haïti | facilitação de investimento encontrada; nenhum diretório ou gestor de venture capital validado |
| Porto Rico | Parallel18 | Parallel18 Ventures e Morro Ventures elegíveis |
| República Dominicana | ProDominicana, CAPCA e fontes oficiais | Caricaco cobre o país; Boost foi classificada como ecossistema |

As ausências acima significam somente “não confirmado nesta execução”. Elas não
provam inexistência de investidores.

## Fila incorporada da #24

Os quatro candidatos roteados pela #24 foram preservados com seus IDs
canônicos:

| Candidato | Decisão na #25 | Motivo |
| --- | --- | --- |
| BASF Venture Capital | evidência insuficiente | atividade global e latino-americana confirmada, sem investimento direto atual concluído em país da #25 |
| Lightrock | elegível | estratégia, escritório, atividade e investimentos mexicanos confirmados em fonte oficial de 2026 |
| Qualcomm Ventures | evidência insuficiente | equipe e portfólio latino-americanos ativos, mas sem país da #25 individualizado na evidência oficial atual |
| StepStone Group | evidência insuficiente | investimentos diretos globais confirmados; presença mexicana identificada como relações com investidores |

## Deduplicação e fronteira do ecossistema

Domínio oficial normalizado, nome e aliases foram comparados com os perfis
existentes. Carao Ventures já está em
[`funds/multi-country/carao-ventures.md`](../../../funds/multi-country/carao-ventures.md)
e foi marcada como duplicata.

Boost Acceleration Camp foi mantida como entidade de ecossistema. Seu site
oficial confirma aceleração regional, mas não um veículo com investimento
direto recorrente. Programas públicos de subvenção, órgãos de promoção de
investimentos, associações, anjos e facilitadores também não foram convertidos
em fundos.

## Método e limites

1. O inventário inicial foi criado antes da coleta de candidatos.
2. AMEXCAP, CAPCA e fontes institucionais serviram somente para descoberta e
   cobertura.
3. Cada decisão de elegibilidade exigiu site oficial atual, investimento
   direto, atividade e geografia aderente.
4. Atividade recente foi verificada por anúncio atual, portfólio mantido,
   veículo em implantação ou operação explicitamente vigente.
5. A coleta percorreu páginas públicas; não houve login, envio de credenciais,
   quebra de bloqueios nem tentativa de contornar restrições.
6. A execução privilegiou profundidade em uma fila curta, não enumeração
   exaustiva de todos os gestores possíveis.

## Artefatos

- [source-inventory.jsonl](source-inventory.jsonl): inventário e lacunas por
  país.
- [candidates.jsonl](candidates.jsonl): decisões canônicas congeladas.
- [evidence.jsonl](evidence.jsonl): evidência oficial usada em cada decisão.
- [run-manifest.jsonl](run-manifest.jsonl): execução e partições auditáveis.
