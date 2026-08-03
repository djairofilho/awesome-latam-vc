# Planejamento determinístico da publicação

Este diretório prepara a coordenação da issue #338 sem publicar perfis, criar
issues, abrir pull requests ou alterar índices globais. A entrada padrão será o
manifesto congelado produzido pela #337 em
`research/epic-327/review/freeze-manifest.json`.

## Contrato de entrada

O manifesto segue
`schemas/publication-freeze-manifest.schema.json`. Ele contém somente o freeze
revisado: data de corte, hashes dos artefatos de decisão e revisão, contagem de
elegíveis e `eligible_records`. Cada registro elegível preserva a identidade, a
partição de validação, as evidências da decisão e o registro de revisão.

O planejador rejeita:

- manifesto que não esteja com `status: frozen`;
- contagem divergente;
- hashes ausentes ou malformados;
- `candidate_id` ou `review_record_id` duplicado;
- decisão diferente de `eligible` dentro de `eligible_records`;
- plano com candidato ausente, repetido ou inserido indevidamente;
- lote com mais de dez candidatos.

Os hashes de decisões e revisões são proveniência congelada pela #337. A #338
os copia sem alteração e acrescenta hashes do próprio manifesto e da lista
canônica de elegíveis. Assim, qualquer troca da entrada ou do conteúdo dos
lotes invalida o plano.

## Geração e verificação

Quando o freeze existir:

```text
python research/epic-327/publication/plan.py
python research/epic-327/publication/plan.py --check
```

Uma entrada alternativa pode ser fornecida sem mudar o código:

```text
python research/epic-327/publication/plan.py --manifest caminho/freeze-manifest.json --output caminho/publication-plan.json
```

Os elegíveis são ordenados por `candidate_id` e particionados sequencialmente
em lotes de até dez. A quantidade é sempre
`ceil(eligible_count / 10)`. O plano apenas reserva nomes determinísticos de
branch e worktree; ele não cria nenhum deles.

## Saída auditável

`publication-plan.json`, quando gerado, segue
`schemas/publication-plan.schema.json` e registra:

- hashes da entrada e da lista canônica de elegíveis;
- quantidade e limite dos lotes;
- cobertura exata dos candidatos;
- coordenadas futuras de branch e worktree por lote;
- hashes individuais dos registros congelados;
- invariantes de duplicidade, elegibilidade e cobertura.

Perfis multilíngues, índices, exports, issues e pull requests permanecem fora do
escopo deste planejador.
