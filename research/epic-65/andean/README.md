# Auditoria de programas públicos nos países andinos

Este diretório executa a
[#100](https://github.com/djairofilho/awesome-latam-vc/issues/100) sob o
contrato da [epic 65](../README.md). A data de corte é 2026-07-27.

## Plano congelado antes da coleta

O inventário cobre Bolívia, Colômbia, Equador, Peru e Venezuela. Para cada país,
foram declaradas cinco frentes independentes antes de qualquer coleta:

1. agência de inovação;
2. ministério responsável;
3. banco público de desenvolvimento;
4. portal oficial de chamadas;
5. fonte subnacional oficial.

Os 25 pares país × tipo de fonte têm `task_id`, `worker_id` e `shard_path`
exclusivos no manifesto. A matriz registra o ponto de entrada oficial, o escopo
planejado e a pendência inicial de cada frente.

O seed BDP Fondo Startup será revalidado sem presumir elegibilidade. A coleta
separará agência, programa e chamada; exigirá evidência oficial tanto do
benefício financeiro direto quanto da rota geográfica; e não publicará perfis.

## Saídas previstas

Cada worker gravará apenas em seu próprio
`shards/<worker-id>/records.jsonl`. Um redutor idempotente consolidará os
registros em `agencies.jsonl`, `programs.jsonl`, `calls.jsonl` e
`evidence.jsonl`. Cobertura, decisões, lacunas, auditoria de links e validações
serão documentadas ao concluir a execução.
