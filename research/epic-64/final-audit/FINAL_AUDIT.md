# Auditoria final de plataformas de funding

Issue: #96. Epic: #64. Data de corte: 2026-07-27.

## Resultado

**Aprovada.** A reconciliação encontrou 39 candidatos em
20 países, 80 células de cobertura e
93 tarefas concluídas. Não há achado crítico, alto, médio ou baixo
aberto no snapshot.

## Reconciliação

| Métrica | Resultado |
| --- | ---: |
| Candidatos com decisão | 39/39 |
| Elegíveis publicados exatamente uma vez | 9/9 |
| Não elegíveis mantidos fora do catálogo | 30/30 |
| Perfis publicados | 9 |
| Índices verificados | 5 |
| Evidências oficiais resolvidas | 63/63 |
| Transferências recebidas adjudicadas | 3/3 |
| Transferências enviadas resolvidas | 6/6 |
| Registros da revisão independente | 29 |

Decisões: 9 elegíveis, 4 excluídos,
2 inativos, 18 com
evidência insuficiente e 6 roteados para outra
categoria.

## Verificações de qualidade

- Cobertura fechada: true.
- Tarefas fechadas: true (58 concluídas e 35 bloqueadas com motivo, responsável e próxima ação).
- Hashes congelados íntegros: true.
- Duplicidades e divergências altas abertas: zero.
- Links internos, evidências, ordenação e índices: íntegros.
- Schemas e testes: validados pela suíte da epic e pelo validador central.
- UTF-8 e mojibake: limpos.

## Caso limítrofe: Captable

Captable foi revalidada como plataforma elegível: existe rota estruturada para
captação, registro regulatório e evidência oficial da CVM. O perfil aparece uma
única vez no lote, está indexado e seu hash permanece congelado.

## Limitações

- A auditoria comprova a consistência do snapshot congelado em 2026-07-27; alterações externas posteriores exigem nova coleta.
- Células sem fonte vigente permanecem fechadas apenas quando o artefato registra gap justificado, owner e próxima ação.
- Dezoito candidatos seguem como insufficient_evidence e não foram publicados; isso é uma decisão explícita, não ausência de destino.
