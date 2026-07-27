# Auditoria de plataformas no México, América Central e Caribe

Esta pasta contém a execução da issue
[#91](https://github.com/djairofilho/awesome-latam-vc/issues/91), com data de
corte em 27 de julho de 2026. A coleta seguiu o contrato da issue #89 e não
criou perfis nem alterou índices de publicação.

## Resultado

Foram inventariadas 44 fontes em 41 shards exclusivos: quarenta workers das
células país por categoria e um coordenador. O manifesto encerra 19 tarefas
como concluídas e 21 como bloqueadas. Fontes alternativas oficiais ou
institucionais fecharam duas células inicialmente bloqueadas.

| Decisão | Quantidade |
| --- | ---: |
| `eligible` | 2 |
| `insufficient_evidence` | 4 |
| `excluded` | 1 |
| `other_category` | 1 |

Arkangeles e Play Business possuem rota oficial para empresas mexicanas,
atividade atual e registro na CNBV. Snowball permanece com evidência
insuficiente porque o documento de captação localizado não conduz a uma rota
atual para founders. A rota empresarial da Fortesza não explicita atendimento
a startups nem a intermediação coletiva da captação.

Jompéame foi excluída por operar doações para causas sociais. AUGE-UCR foi
encaminhada para outra categoria por operar incubação e aceleração. Hagámosla e
Zafèn permanecem com evidência insuficiente porque seus domínios oficiais não
responderam.

## Cobertura

Cada país possui quatro células: regulador, ecossistema público, plataforma
oficial e descoberta.

| País | Completas | Lacunas justificadas |
| --- | ---: | ---: |
| Costa Rica | 3 | 1 |
| Cuba | 2 | 2 |
| República Dominicana | 1 | 3 |
| Guatemala | 1 | 3 |
| Honduras | 3 | 1 |
| Haiti | 3 | 1 |
| México | 2 | 2 |
| Nicarágua | 1 | 3 |
| Panamá | 3 | 1 |
| El Salvador | 2 | 2 |
| **Total** | **21** | **19** |

Uma lacuna indica somente que a fonte planejada estava inacessível ou não
forneceu conteúdo verificável na data de corte. Ela não afirma inexistência de
plataformas no país.

## Artefatos congelados

| Arquivo | SHA-256 |
| --- | --- |
| `candidates.jsonl` | `778d7d13c940329038f84922b3850be147d0bc4733884bf540809bdb538e5f31` |
| `coverage-matrix.jsonl` | `527c0bd550d80ec72e06453de716153f251baa38860d46ddd6869a18a4e7a245` |
| `evidence.jsonl` | `7bbb2aa66466c398aee69f4d1c9380c89a64663cd03b52157891800f219acf0b` |
| `source-inventory.jsonl` | `f53039ce96b265cacf5b8f624639cf5c4b692ad3653f9b7ba162afb0f99f1913` |

Os hashes usam conteúdo UTF-8 com finais de linha normalizados em LF. O
`run-manifest.jsonl` fica fora do conjunto para evitar referência circular.
