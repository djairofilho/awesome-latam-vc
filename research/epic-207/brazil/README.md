# Consolidação canônica da descoberta brasileira

Este diretório é a saída determinística da issue #216. O builder reúne os
shards #210–#215 sem consultar a CVM, decidir elegibilidade ou publicar perfis.

## Geração

```powershell
python research/epic-207/brazil/build_consolidated.py
python research/epic-207/brazil/build_consolidated.py --check
python research/epic-207/validate.py research/epic-207/brazil
```

O builder ordena todos os JSONL por ID, preserva as fontes e evidências dos
workers e gera hashes SHA-256. A saída bruta consolidada contém 82 fontes, 51
linhas de candidato, 69 evidências e 22 registros de cobertura reduzidos a 10
células únicas por família e geografia.

## Identidade

Canary dos shards #210/#213 e Sororitê Ventures dos shards #212/#213 são as
duas duplicatas exatas. Os IDs de redescoberta apontam aos candidatos
canônicos, mas todas as 51 linhas permanecem disponíveis para a revisão.

`identity-resolution.jsonl` também registra as relações ou ambiguidades de DNA
Capital/VC II, Vinci Partners, Primus/FIP Sul Ventures, Nido/Platypus,
Jatobá/Impacto Amazônia, LH Invest/LH Tech Ventures, Accion/Venture Lab e
Prosus/Naspers. Veículos distintos não são unidos automaticamente.

Os perfis Entrypoint e Flourish Ventures surgiram no catálogo depois do
baseline. `consolidation-summary.json` registra esse delta como guarda:
nenhum candidato é criado e nenhum dos dois entra nos shards de validação.

## Validação paralela

As filas em `validation-shards/` aplicam:

```text
int(sha256(candidate_id), 16) % 3
```

| Issue | Resto | Candidatos |
| --- | ---: | ---: |
| #217 | 0 | 17 |
| #218 | 1 | 19 |
| #219 | 2 | 15 |

Todos os candidatos continuam com `decision: null`. Elegibilidade, categoria e
atividade serão decididas pelos workers #217–#219.

## Limitações preservadas

- Não houve consulta à CVM.
- O vínculo entre `evidence.jsonl` e `source-inventory.jsonl` é inferido por
  URL, título e publicador, pois o schema de evidência não possui `source_id`.
- As 27 evidências de terceiros permanecem no artefato, mas não são promovidas
  para `official_evidence_ids`.
- Fontes parciais ou indisponíveis continuam visíveis no inventário e tornam a
  respectiva célula de cobertura `gap_justified`.
