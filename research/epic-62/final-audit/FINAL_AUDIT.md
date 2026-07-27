# Auditoria final de aceleradoras

Issue: #79. Epic: #62. Data de corte: 2026-07-27.

## Resultado

**Aprovada.** A auditoria reconciliou 80 ocorrências
de entrada em 78 candidatos canônicos. Todos têm
uma decisão, a fila revisada contém 26
publicáveis e os 26 perfis foram publicados exatamente uma
vez. Não há inconsistência crítica ou alta aberta.

## Métricas

| Métrica | Resultado |
| --- | ---: |
| Ocorrências de entrada | 80 |
| Candidatos canônicos | 78 |
| Ocorrências duplicadas consolidadas | 2 |
| Registros de cobertura | 37 |
| Países na matriz | 25 |
| Tarefas fechadas | 80/80 |
| Candidatos revisados independentemente | 52 |
| Divergências resolvidas | 3 |
| Relações entre catálogos verificadas | 55 |
| Perfis publicados | 26 |
| Lotes | 3 (10, 10, 6) |

Decisões consolidadas: 25 elegível, 3 encaminhado-para-funds, 13 encaminhado-para-outra-epic, 19 evidência-insuficiente, 17 excluído, 1 inativo.
A revisão independente reabriu Ventiur com evidência oficial adicional, levando
a fila final de 25 para 26 publicáveis.

## Qualidade

- cada candidato aparece uma vez e tem decisão;
- todos os casos obrigatórios da revisão independente foram cobertos;
- três divergências, incluindo uma alta, foram resolvidas;
- 26 IDs, perfis, caminhos, lotes e índice reconciliam exatamente;
- aliases, veículos separados e evidências oficiais foram preservados;
- hashes congelados, links internos, UTF-8 e mojibake foram verificados;
- zero duplicata silenciosa entre catálogos.

## Limitações

- A auditoria comprova o snapshot de 2026-07-27; mudanças externas posteriores exigem nova coleta.
- Oito registros de cobertura permanecem parciais, todos com motivo, responsável e próxima ação.
- Seis tarefas permanecem bloqueadas por indisponibilidade de fonte oficial, sem impedir uma decisão explícita para cada candidato.
- Destinos de backlog em outros catálogos são rotas registradas, não perfis materializados por esta epic.
