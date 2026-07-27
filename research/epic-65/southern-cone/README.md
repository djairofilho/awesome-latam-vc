# Auditoria de programas públicos no Cone Sul

Este diretório executa a
[#101](https://github.com/djairofilho/awesome-latam-vc/issues/101) conforme o
contrato da [epic 65](../README.md). A data de corte é 2026-07-27.

## Cobertura

Antes da coleta, a matriz e o manifesto congelaram 20 pares exclusivos:
Argentina, Chile, Paraguai e Uruguai × agência de inovação, ministério
responsável, banco público de desenvolvimento, portal oficial de chamadas e
fonte subnacional oficial.

Cada par possui `task_id`, `worker_id` e `shard_path` próprios. As 20 tarefas
foram concluídas, inclusive quando o resultado foi parcial ou indisponível. A
matriz conserva motivo, responsável e próxima ação para cada lacuna.

## Resultado

Foram consolidadas 9 agências, 12 programas, 7 chamadas e 28 evidências
oficiais. Sete programas cumprem o contrato:

- CORFO: Semilla Inicia para Empresas Lideradas por Mujeres e Start-Up Chile;
- SERCOTEC: Capital Pioneras Emprende;
- ANII: Apoyo a Emprendimientos Innovadores, Validación de Ideas de Negocios e
  Coinversión en Startups;
- ANDE: Semilla ANDE 2026.

A CORFO foi revalidada a partir de fontes atuais, sem herdar a decisão da
[#61](https://github.com/djairofilho/awesome-latam-vc/issues/61). Agência,
programas e chamadas possuem registros e evidências separados.

Na Argentina, Startup 2025 confirmou benefício financeiro direto e público
startup, mas a janela encerrou e não há prova oficial suficiente de recorrência.
Emprendimiento Argentino 2026 estava aberto na data de corte, porém oferece
reconhecimento e mentoria, não capital.

No Paraguai, o CONACYT documenta instrumentos históricos do PROINNOVA para
validação e arranque de empreendimentos tecnológicos, sem intake atual
confirmado. O MIC anunciou Capital Semilla Emprende 2026 em Hohenau, mas não
publicou valor, calendário ou formulário. A decisão ficou como evidência
insuficiente, com responsável e próxima ação.

No Uruguai, o Fondo Sectorial de Energía do MIEM estava aberto e possui
benefício financeiro, mas aceita empresas em geral e não confirma uma rota
específica para startups. Ele foi excluído sem extrapolar `empresa`,
`MIPYME` ou `inovação` para a categoria editorial de startup.

## Consolidação e links

Cada worker grava somente em `shards/<worker-id>/records.jsonl`.
[`consolidate.py`](consolidate.py) percorre os shards em ordem, rejeita IDs
duplicados e gera `agencies.jsonl`, `programs.jsonl`, `calls.jsonl` e
`evidence.jsonl` com ordenação determinística.

[`link_audit.py`](link_audit.py) valida HTTPS e domínios oficiais. Com `--live`,
respostas 401, 403, 405 e 429 são bloqueios alcançáveis; 404 e outros erros HTTP
quebram o gate; timeout, DNS e cadeia TLS inválida ficam como não verificáveis,
pois não demonstram sozinhos que o conteúdo deixou de existir.

Na auditoria ao vivo, 36 dos 39 links responderam HTTP 200. O portal argentino
de chamadas expirou por timeout e os dois links do MIEM não puderam ser
verificados pela cadeia TLS local. Não houve link HTTP quebrado.

Esta issue não cria nem publica perfis. Todos os campos `canonical_profile`
permanecem nulos.

## Lacunas e limites

- BICE, BancoEstado, AFD e BROU não confirmaram rota própria para startups no
  escopo percorrido.
- Fontes subnacionais foram tratadas como sondagem material, não como prova de
  inexistência em todas as províncias, regiões, departamentos ou municípios.
- O catálogo geral da CORFO estava inconsistente; fichas específicas e a rota
  Start-Up Chile sustentam as decisões registradas.
- O portal de convocatórias do CONACYT não forneceu inventário atual
  verificável de apoio a startups.
- Chamadas e formulários são uma fotografia de 2026-07-27 e precisam ser
  recapturados antes de qualquer publicação.
