# Revisão independente da fila pública

Revisor: `independent-reviewer-issue-102`. Data: 2026-07-27. A revisão foi executada depois da
redução mecânica e não reutilizou a decisão do consolidador como evidência.

## Cobertura

- 12 agências originalmente elegíveis: 12.
- 15 programas originalmente elegíveis: 15.
- 5 agências originalmente insuficientes: 5.
- 5 programas originalmente insuficientes: 5.
- 5 fronteiras de saída: 5.
- 13 transferências recebidas: 13.
- 3 agências derivadas ou corrigidas por transferências: 3.

Cada linha de `independent-review.jsonl` registra sujeito, evidências consultadas,
checagens do contrato, conclusão, divergência e resolução. Todas as divergências
altas estão resolvidas.

## Decisões corrigidas ou materializadas

| Item | Antes | Depois | Resolução |
| --- | --- | --- | --- |
| `agency-brde` | `None` | `elegível` | A agência foi criada somente para preservar o vínculo institucional do programa transferido. |
| `agency-finep` | `excluída` | `elegível` | A agência passou a elegível porque a transferência revelou uma rota financeira recorrente para startups. |
| `agency-prefeitura-divinopolis` | `None` | `evidência insuficiente` | A agência foi criada somente para preservar o vínculo institucional do programa transferido. |
| `agency-sena` | `elegível` | `evidência insuficiente` | A decisão foi rebaixada porque empreendedorismo geral não comprova rota específica para startups. |
| `agency-sercotec` | `elegível` | `evidência insuficiente` | A decisão foi rebaixada porque empreendedorismo geral não comprova rota específica para startups. |
| `program-sena-fondo-emprender` | `elegível` | `evidência insuficiente` | A decisão foi rebaixada porque empreendedorismo geral não comprova rota específica para startups. |
| `program-sercotec-capital-pioneras` | `elegível` | `evidência insuficiente` | A decisão foi rebaixada porque empreendedorismo geral não comprova rota específica para startups. |

Fondo Emprender e Capital Pioneras foram rebaixados porque as fontes confirmam
empreendedorismo geral, não uma rota específica para startups. A Finep passou a
elegível após a materialização do Programa Mulheres Inovadoras. Valores,
recorrência e disponibilidade permanecem restritos às fontes que os afirmam.

## Transferências da epic #62

| Origem | Resolução | Destino canônico | Fundamento |
| --- | --- | --- | --- |
| `accel-acelera-divinopolis` | `materialized-after-independent-review` | `research/epic-65/consolidation/programs.jsonl#program-acelera-divinopolis` | A fonte confirma cinco edições e rota para startups, mas não esclarece se a bolsa é benefício financeiro; as premiações descritas são capacitações. |
| `accel-acre-for-startups` | `materialized-after-independent-review` | `research/epic-65/consolidation/programs.jsonl#program-acre-for-startups` | A bolsa financeira e a rota para startups são explícitas, mas a única edição localizada está encerrada e não há recorrência oficial. |
| `accel-and-agroinnovatec` | `materialized-after-independent-review` | `research/epic-65/consolidation/programs.jsonl#program-agroinnovatec` | As edições 2025 e 2026, a rota para propostas e o acesso a capital semente satisfazem o contrato público. |
| `accel-and-emprendimiento-digital` | `rejected-by-public-contract` | `research/epic-62/consolidation/candidates.jsonl#accel-and-emprendimiento-digital` | A fonte oferece acompanhamento técnico, recursos e conexões, mas não confirma capital ou financiamento para os empreendimentos. |
| `accel-and-startup-peru` | `matched-existing-program` | `research/epic-65/andean/programs.jsonl#program-proinnovate-startup-peru` | A transferência coincide com programa regional já validado pelo contrato público. |
| `accel-bndes-garagem` | `materialized-after-independent-review` | `research/epic-65/consolidation/programs.jsonl#program-bndes-garagem` | A rota anual até 2028 e a premiação em dinheiro comprovam benefício, startups e recorrência. |
| `accel-brde-labs-rs` | `materialized-after-independent-review` | `research/epic-65/consolidation/programs.jsonl#program-brde-labs-rs` | A sétima edição oficial confirma rota recorrente para startups e R$ 261 mil em prêmios. |
| `accel-finep-mulheres-inovadoras` | `materialized-after-independent-review` | `research/epic-65/consolidation/programs.jsonl#program-finep-mulheres-inovadoras` | A sétima edição e o histórico das seis anteriores confirmam rota recorrente e prêmios em dinheiro para startups. |
| `accel-mxcac-cenpromype` | `rejected-by-public-contract` | `out-of-scope:regional-public-operator-without-specific-program` | A transferência identifica apenas um organismo regional; não há programa, benefício, rota ou atividade adjudicáveis. |
| `accel-sc-anii-sprintuy` | `rejected-by-public-contract` | `out-of-scope:soft-landing-without-capital` | Passagens e hospedagem para uma imersão não constituem os instrumentos financeiros enumerados pelo contrato. |
| `accel-sc-incubate` | `rejected-by-public-contract` | `research/epic-62/consolidation/candidates.jsonl#accel-sc-incubate` | A incubação e mentoria são estruturadas, mas a fonte não oferece benefício financeiro. |
| `accel-sc-mic-reinventa` | `rejected-by-public-contract` | `research/epic-62/consolidation/candidates.jsonl#accel-sc-mic-reinventa` | A assistência técnica é pública e atual, mas a fonte não confirma capital ou financiamento. |
| `accel-sc-startup-chile` | `matched-existing-program` | `research/epic-65/southern-cone/programs.jsonl#program-start-up-chile` | A transferência coincide com programa regional já validado pelo contrato público. |

As cinco transferências rejeitadas não ficaram em limbo: três retornam à fila de
aceleradoras para decisão sob o contrato próprio e duas recebem destinos
fora de escopo específicos. Nenhuma foi convertida em programa público por
inferência.
