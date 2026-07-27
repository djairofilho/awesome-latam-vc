# Plano congelado — redes-anjo do México, América Central e Caribe

## Gate pré-coleta

- Issue de execução: #83.
- Contrato: #80.
- Data de corte: 2026-07-27.
- Recência elegível: evidência oficial publicada ou atualizada entre 2024-07-27 e 2026-07-27.
- Escopo: México, Belize, Costa Rica, El Salvador, Guatemala, Honduras, Nicarágua, Panamá e Caribe.
- Subcoberturas caribenhas explícitas: República Dominicana, Jamaica e fontes regionais do Caribe.
- Baseline: AngelHub (`ang-angelhub-mx`) já foi validada na #81. Não há fonte, tarefa, evidência, candidato ou perfil duplicado nesta execução.
- Perfis novos permitidos: zero. A execução produz pesquisa e decisões, não novos arquivos em `ecosystem/angel-networks/`.

Este plano, o inventário de fontes, a matriz de cobertura e o manifesto foram gravados antes de qualquer coleta ou decisão.

## Hipóteses e fronteiras

As sementes Costa Rica Angels/ParqueTec, Trigen Ventures, Barrilete Ventures, Enlaces RD, FirstAngels Jamaica e Venture Club Latam são hipóteses, não conclusões. Cada descoberta receberá uma decisão explícita.

- Rede, clube, alumni network, capítulo autônomo ou syndicate recorrente podem permanecer na epic 63.
- Gestora com capital recorrente será encaminhada para `funds/`.
- Plataforma neutra será encaminhada para a epic 64.
- Aceleradora será encaminhada para a epic 62.
- Programa público será encaminhado para a epic 65.
- Comunidade sem decisão e investimento dos membros será excluída.
- Capítulo sem autonomia comprovada nos quatro critérios do contrato será alias do ator canônico e só poderá receber `duplicado`.

## Partições exclusivas

| Partição | Shard exclusivo | Fontes planejadas |
| --- | --- | --- |
| México | `shards/worker-mexico/` | Venture Club Latam, Trigen Ventures, Barrilete Ventures |
| Belize | `shards/worker-belize/` | BELTRAIDE |
| Costa Rica | `shards/worker-costa-rica/` | Costa Rica Angels, ParqueTec |
| El Salvador | `shards/worker-el-salvador/` | Secretaría de Innovación |
| Guatemala | `shards/worker-guatemala/` | Win.gt |
| Honduras | `shards/worker-honduras/` | Honduras Digital Challenge |
| Nicarágua | `shards/worker-nicaragua/` | CCSN |
| Panamá | `shards/worker-panama/` | Ciudad del Saber |
| Caribe | `shards/worker-caribbean/` | Enlaces RD, FirstAngels Jamaica, Caribbean Export |
| Consolidação | `shards/worker-consolidator/` | Matriz e manifesto |

Nenhuma partição pode escrever no shard de outra. O redutor canônico lê os shards em ordem estável, rejeita chaves conflitantes e deve gerar o mesmo hash em duas execuções consecutivas.

## Protocolo de coleta e decisão

1. Verificar URL, identidade e categoria em fonte oficial.
2. Registrar redirecionamentos, indisponibilidade, bloqueio e lacunas sem inferir datas.
3. Para uma entidade potencialmente elegível, separar atores de seleção, decisão e capital.
4. Exigir acesso externo e atividade oficial datada dentro da janela de 24 meses.
5. Respeitar `robots.txt`, termos, autenticação, CAPTCHA e WAF.
6. Limitar a execução a oito requisições simultâneas, duas por domínio, timeout de 20 segundos, até três tentativas para 429/5xx e no máximo dois navegadores.
7. Auditar links e `robots.txt`; registrar hashes SHA-256 dos artefatos canônicos.

## Critério de fechamento

A execução só pode fechar quando as onze linhas de cobertura, incluindo República Dominicana, Jamaica e Caribe regional, tiverem status final, toda descoberta tiver decisão, pendências tiverem motivo/responsável/próxima ação, o redutor for idempotente, os schemas e testes passarem e não houver perfil novo.
