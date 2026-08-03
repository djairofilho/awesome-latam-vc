# Contrato de validação oficial

As issues #334, #335 e #336 consomem exclusivamente os candidatos congelados
pela consolidação com `status = ready_for_validation`. Cada worker escreve apenas
em `shards/validation-N/`, onde `N` é a partição
`int(sha256(candidate_id), 16) mod 3`.

## Artefatos de cada shard

- `candidates.jsonl`: entrada congelada produzida pelo reducer;
- `decisions.jsonl`: um `validation-record` por candidato de entrada;
- `official-evidence.jsonl`: novas evidências oficiais usadas na validação;
- `summary.json`: contagens e hashes verificados pelo reconciliador.

O reconciliador também lê `consolidation/candidates.jsonl`,
`consolidation/evidence.jsonl` e `consolidation/exceptions.jsonl`. Ele nunca gera
ou corrige esses artefatos.

## Evidência e findings

O schema de evidência compartilhado permanece compatível com a triagem. Nos
registros novos de validação, o `value` de cada claim segue este formato:

```json
{"finding": "confirmed", "value": true}
```

`finding` aceita `confirmed`, `contradictory` e `not_disclosed`. Um gate
`blocked` não cria claim: registra `blocking_outcome` e `attempted_url` no
registro de decisão.

Os campos aceitos por gate são:

- `direct_investment`: `direct_startup_investment`;
- `recurrence`: `recurrence`;
- `recent_activity`: `activity_date`;
- `latam_access`: `base_geography` ou `market_access`;
- `identity`: `identity`.

Cada evidência referenciada deve existir, pertencer ao mesmo `candidate_id` e
conter um claim do gate com o mesmo finding. `not_disclosed` registra ausência
de divulgação em material oficial acessível. Não equivale a `false` nem a
inatividade.

## Gates e decisões

A janela de atividade é inclusiva: da data de corte menos 24 meses-calendário
até a própria data de corte. Data futura é inválida.

- `eligible`: todos os cinco gates estão `confirmed`;
- `inactive`: identidade, investimento direto, recorrência e acesso LatAm estão
  confirmados, e a atividade oficial mais recente é anterior à janela;
- `excluded`: investimento direto, recorrência ou acesso LatAm está
  `contradictory`;
- `insufficient_evidence`: há `not_disclosed` ou `blocked`, sem condição mais
  forte de exclusão ou inatividade;
- `duplicate` e `routed_*`: exigem identidade confirmada e destino coerente.

Elegíveis e encaminhados seguem para `independent_review`. Duplicatas, inativos
e excluídos seguem para `deterministic_exclusion_sampling`. Evidência
insuficiente exige owner e ação de acompanhamento ou revisão manual de
identidade.

## Verificação read-only

```text
python research/epic-327/validation/reconcile.py --check
python -m unittest discover -s research/epic-327/tests -p "test_validation*.py" -v
```

`--check` apenas lê arquivos. Se o freeze da #333 ainda não existir, encerra
com erro claro. A reconciliação exige união exata dos três shards, partição e
worker corretos, ausência de sobreposição com exceções, referências válidas,
JSONL canônico e summaries idênticos às contagens e hashes calculados.
