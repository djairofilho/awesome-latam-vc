# Plano de publicação das aceleradoras

## Gate de entrada

- Issue: #78.
- Epic: #62.
- Contrato: #68.
- Consolidação: #76.
- Revisão independente: #77.
- Data de corte: 2026-07-27.
- Manifesto congelado:
  `research/epic-62/independent-review/publishable-manifest.json`.
- SHA-256 dos bytes de entrada:
  `52da16cfc931aa3c1a1304dbee575a7b805e0db03ca2f96a75e5f4c79604adc2`.
- IDs publicáveis: 26.

Nenhum candidato fora desse manifesto pode ser publicado. Decisões
`excluído`, `evidência-insuficiente`, `encaminhado-para-funds`,
`encaminhado-para-outra-epic` ou `inativo` permanecem fora do catálogo.

## Lotes

Os IDs são ordenados pelo `candidate_id` e divididos em fatias consecutivas de
até 10 registros:

| Lote | Perfis | Owner | Branch |
| --- | ---: | --- | --- |
| `batch-01` | 10 | `djairofilho` | `agent/issue-78-accelerators-publication` |
| `batch-02` | 10 | `djairofilho` | `agent/issue-78-accelerators-publication` |
| `batch-03` | 6 | `djairofilho` | `agent/issue-78-accelerators-publication` |

Cada arquivo em `batches/` é também o corpo UTF-8 do sub-issue correspondente.
O manifesto final registra número, URL e hash de cada sub-issue.

## Conteúdo dos perfis

Cada perfil deriva somente do candidato consolidado, das evidências oficiais e
da resolução independente:

- identidade, aliases, operador e programa;
- site e rota de candidatura;
- formato, duração, estágio e geografia;
- atividade e acesso externo;
- capital, instrumento e equity sem inferência;
- relação explícita entre programa e veículo;
- fontes oficiais e data de verificação.

Campos não divulgados permanecem `Not publicly disclosed`. Programa e veículo
financeiro nunca são fundidos.

## Índices

`ecosystem/accelerators/README.md` será o índice canônico dos 26 perfis. Os
índices raiz em inglês e espanhol já apontam para a categoria e serão
verificados por testes de links internos. Não há índice raiz em português neste
repositório.

## Gates

- exatamente 26 perfis e três lotes não vazios;
- nenhum lote com mais de 10 perfis;
- cobertura exata e sem sobreposição;
- cada ID ligado a um único caminho;
- nenhum candidato fora do manifesto;
- todos os caminhos indexados uma vez;
- fontes oficiais, atividade, acesso, aliases e veículos preservados;
- zero links internos órfãos;
- gerador e hashes determinísticos;
- testes da publicação, consolidação, revisão e 46 testes centrais aprovados;
- validadores, drift, UTF-8, mojibake e `git diff --check` aprovados.
