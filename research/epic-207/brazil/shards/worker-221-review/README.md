# Revisão final da auditoria brasileira

Este shard registra a revisão independente da issue #221 sobre o bundle
adjudicado da issue #220. Ele reúne os achados cegos e das passagens finais,
sem usar a CVM nem o baseline como origem de descoberta.

O arquivo `records.py` é a fonte determinística dos novos registros de
`source-inventory.jsonl`, `candidates.jsonl`, `evidence.jsonl` e
`identity-resolution.jsonl`. O builder canônico aplica esses registros sobre a
saída em memória de `build_adjudicated.py`, corrige os pontos encontrados na
revisão e gera a amostra e o relatório final.
