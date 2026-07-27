# Plano da auditoria de programas públicos no Brasil

Este diretório executa a
[#98](https://github.com/djairofilho/awesome-latam-vc/issues/98) sob o contrato
da [epic 65](../README.md). A data de corte é 2026-07-27.

## Cobertura planejada

Antes da coleta, a matriz e o manifesto congelam cinco frentes independentes:

1. Finep como agência de inovação, incluindo os seeds Finep e Programa Inovar;
2. MCTI como ministério responsável;
3. BNDES como banco público de desenvolvimento, incluindo a Chamada de Clima;
4. Sebrae como portal oficial de chamadas e editais;
5. FAPESP PIPE como fonte subnacional material.

Cada frente possui um `worker_id` e um `shard_path` exclusivos. Nenhuma decisão
de elegibilidade é presumida a partir dos seeds da epic 16.

## Ordem de execução

1. congelar matriz e manifesto;
2. consultar somente fontes oficiais;
3. registrar resultados nos shards atribuídos;
4. consolidar os seis arquivos canônicos;
5. validar referências, evidências, datas, cobertura e decisões.

Nenhum perfil será publicado por esta issue.
