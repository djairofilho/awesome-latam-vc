# Validação canônica — issue #217

Este shard valida integralmente os 17 candidatos atribuídos ao resíduo `hash mod 3 = 0`, com data de corte em 30 de julho de 2026.

## Resultado

| Decisão | Quantidade |
| --- | ---: |
| `eligible` | 8 |
| `duplicate` | 2 |
| `insufficient_evidence` | 7 |
| Pendentes | 0 |

Elegíveis: 17Sigma, DNA Capital, Barn Investimentos, Accion Ventures, Antler, L4 Venture Builder, Prosus Ventures e Upload Ventures.

Duplicatas: Astella, já publicada em `funds/brazil/astella.md`, e Caravela Capital, já publicada em `funds/regional/caravela-capital.md`.

## Método auditável

1. A fila de entrada foi preservada por `candidate_id`, fontes de descoberta, aliases e IDs de marca, gestora, veículo e programa.
2. Cada candidato foi confrontado com fontes oficiais atuais para os cinco gates: identidade, aporte direto, recorrência, atividade oficial na janela e relação explícita com o Brasil.
3. Evidências anteriores foram revalidadas quando úteis. Fontes novas receberam IDs da issue #217; fontes bloqueadas também foram inventariadas.
4. Data de acesso, candidatura aberta, publicação editorial, rodapé anual e datas relativas de redes sociais não foram usados como prova de atividade. Para Accion e Antler, o gate foi fechado respectivamente pelo anúncio oficial da rodada da BackChannel em 23 de março de 2026 e pelo anúncio oficial do BNDES sobre o Fundo Antler Brasil I em 16 de junho de 2026.
5. Notícias e listas públicas serviram somente à descoberta. Nenhuma fonte da CVM foi consultada ou usada.

## Lacunas explícitas

- Lean VC: a fonte oficial atual descreve software e serviços para investidores, sem veículo próprio comprovado.
- Maromar Investimentos: há investimento direto em startups e base brasileira, mas falta atividade oficial datada na janela.
- Santa Maria Investment Group: há venture capital latino-americano, mas não há acesso específico ao Brasil nem aporte recente datado.
- Vinci Partners: a plataforma institucional não fecha uma estratégia startup/VC canônica e separada.
- Rural Ventures: tese, portfólio e base brasileira estão confirmados, mas falta atividade oficial com data completa.
- Big Bets: identidade, recorrência e sede estão confirmadas; atualizações oficiais só exibiram datas relativas.
- Firestreak Ventures: atividade recente e recorrência estão confirmadas, mas o Brasil aparece apenas de forma incidental.

Os próximos passos de cada lacuna estão registrados no respectivo overlay em `candidates.jsonl`.
