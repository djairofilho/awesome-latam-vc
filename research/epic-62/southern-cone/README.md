# Auditoria de aceleradoras no Cone Sul

Auditoria executada para a issue #74, conforme o contrato da issue #68, com data
de corte em 27 de julho de 2026. O recorte cobre Argentina, Chile, Paraguai e
Uruguai.

## Resultado

Foram percorridas 12 fontes oficiais e decididos 12 candidatos:

| Decisão | Quantidade |
| --- | ---: |
| `elegível` | 2 |
| `encaminhado-para-outra-epic` | 4 |
| `excluído` | 3 |
| `evidência-insuficiente` | 2 |
| `encaminhado-para-funds` | 1 |

GRIDX Transform e Magical Accelerator cumpriram os requisitos de programa
estruturado, acesso externo e latino-americano, atividade e rota oficial.
Nenhum perfil foi criado. Os dois elegíveis seguem para revisão independente na
issue #77.

## Cobertura e lacunas

| País | Fontes concluídas | Resultado e lacuna |
| --- | ---: | --- |
| Argentina | 3/3 | Um programa elegível; CITES foi encaminhado a `funds/` e IncuBAte à Epic 65. A busca setorial cobriu deep tech, biotecnologia e política pública. |
| Chile | 3/3 | Um programa elegível e um público encaminhado. Platanus permanece pendente de sinal oficial datado e regra geográfica. |
| Paraguai | 3/3 | Nenhum elegível. A fonte privada atual descreve consultoria, a universitária oferece incubação e o programa nacional foi encaminhado à Epic 65. Falta prova oficial de uma aceleradora privada ativa com seleção própria. |
| Uruguai | 3/3 | Nenhum elegível. ThalesLab publica percurso e contato, mas não atividade datada recente; Ingenio é incubadora e SprintUy é programa público de imersão. |

As lacunas não foram convertidas em fatos negativos. Capital, instrumento,
equity, duração e estágio ausentes permanecem como
`not_publicly_disclosed`.

## Controles de execução

- 12 tarefas concluídas em 12 shards exclusivos;
- redução limitada à partição `southern-cone`, sem incorporar shards regionais
  de outras auditorias;
- segunda redução com hashes SHA-256 idênticos nos quatro artefatos reduzidos;
- 12 URLs oficiais responderam HTTP 200 na auditoria de links;
- validador contratual e suíte de testes executados sem erro;
- zero perfis publicados.

## Artefatos

- `source-inventory.jsonl`: inventário e estado das 12 fontes;
- `candidates.jsonl`: decisões editoriais e campos canônicos;
- `evidence.jsonl`: evidência oficial por afirmação;
- `coverage-matrix.jsonl`: cobertura por país;
- `run-manifest.jsonl`: execução, ownership e estado das tarefas;
- `shards/`: saídas exclusivas dos workers preservadas para auditoria.
