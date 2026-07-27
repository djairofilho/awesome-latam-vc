# Auditoria de programas públicos no Cone Sul

Este diretório executa a
[#101](https://github.com/djairofilho/awesome-latam-vc/issues/101) sob o
contrato da [epic 65](../README.md). A data de corte é 2026-07-27.

## Plano congelado antes da coleta

O inventário cobre Argentina, Chile, Paraguai e Uruguai. Para cada país, foram
declaradas cinco frentes independentes antes de qualquer coleta:

1. agência de inovação;
2. ministério responsável;
3. banco público de desenvolvimento;
4. portal oficial de chamadas;
5. fonte subnacional oficial.

Os 20 pares país × tipo de fonte têm `task_id`, `worker_id` e `shard_path`
exclusivos. A matriz registra o ponto de entrada oficial, o escopo planejado e a
pendência inicial de cada frente.

A CORFO será revalidada a partir da migração da
[#61](https://github.com/djairofilho/awesome-latam-vc/issues/61), sem presumir
elegibilidade e sem fundir agência, programa e chamada. A coleta exigirá prova
oficial do benefício financeiro, do público startup, da geografia e da
atividade; chamadas temporárias não serão publicadas como perfis.

## Saídas previstas

Cada worker gravará apenas em `shards/<worker-id>/records.jsonl`. Um redutor
idempotente consolidará `agencies.jsonl`, `programs.jsonl`, `calls.jsonl` e
`evidence.jsonl`. Cobertura, bloqueios, lacunas e auditoria de links serão
documentados ao concluir a execução.
