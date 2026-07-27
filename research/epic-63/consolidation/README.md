# Consolidação das redes-anjo da América Latina

Resultado da issue
[#86](https://github.com/djairofilho/awesome-latam-vc/issues/86), conforme o
contrato da epic #63 e com data de corte em 27 de julho de 2026. Esta etapa
congelou a fila, mas não criou perfis.

## Before/after

| Artefato | Antes | Depois |
| --- | ---: | ---: |
| Ocorrências de candidatos | 44 | 44 |
| IDs únicos de candidatos | 44 | 44 |
| Evidências | 57 | 57 |
| Fontes | 61 | 61 |
| Células de cobertura | 42 | 42 |
| Elegíveis na fila publicável | 12 | 12 |

Não houve ocorrência duplicada entre as cinco auditorias. Os 44 candidatos
permanecem no registro canônico para preservar decisões negativas, lacunas e
transferências.

## Decisões congeladas

| Decisão | Quantidade |
| --- | ---: |
| `elegível` | 12 |
| `evidência-insuficiente` | 15 |
| `encaminhado-para-plataformas` | 5 |
| `encaminhado-para-funds` | 4 |
| `duplicado` | 2 |
| `encaminhado-para-aceleradoras` | 2 |
| `inativo` | 2 |
| `encaminhado-para-programas-públicos` | 1 |
| `excluído` | 1 |

Cinco elegíveis já possuem perfil baseline: AngelHub, Anjos do Brasil, BR
Angels, GVAngels e Urca Angels.

Sete seguem para publicação posterior:

- Curitiba Angels;
- PUC angels;
- Enlaces;
- FirstAngels Caribbean;
- PAD, Red de Inversionistas Ángeles;
- Business Angels Club EmprendeIAE;
- Red Ángeles do Centro de Innovación UC.

`publication-queue.jsonl` fixa os 12 IDs, rotas canônicas e o estado
`already-published` ou `pending-publication`.

## Identidades, aliases e veículos

- Mulheres Investidoras Anjo aponta diretamente para Anjos do Brasil.
- BAC Mar del Plata aponta diretamente para o Business Angels Club.
- FirstAngels Jamaica permanece como marca anterior de FirstAngels Caribbean.
- Os três produtos nacionais da Angel Investment Network mantêm registros
  distintos e destinos próprios na epic #64.
- ParqueTec e Costa Rica Angels permanecem como operador acelerador e rede
  hospedada, respectivamente.
- O veículo da BR Angels permanece ator de capital, não substituto da rede.
- The Board continua como híbrido com evidência insuficiente, sem fusão
  inferida entre rede e fundo.

As sete resoluções estão em `identity-resolutions.json`. Não há cadeia ou ciclo
de aliases.

## Transferências de categoria

As 12 saídas possuem categoria, ID-alvo e destino:

- quatro para `funds/`;
- duas para a epic #62;
- cinco para a epic #64;
- uma para a epic #65.

`category-resolutions.json` também registra os cinco perfis baseline recebidos
do catálogo. Não houve transferência nova recebida de outra epic.

## Revisão independente

O consolidador usa a identidade `consolidator-issue-86`. A revisão separada usa
`independent-reviewer-issue-86` e está documentada em
`independent-review.jsonl` e `INDEPENDENT_REVIEW.md`.

A revisão cobriu 42 registros:

- 100% dos elegíveis;
- 100% dos encaminhados;
- 100% dos casos insuficientes, duplicados e híbridos;
- amostra determinística mínima de 20% dos demais.

A amostra ordenou os IDs pelo SHA-256 e selecionou `ang-venecapital-org`.
Nenhuma divergência crítica ou alta ficou aberta.

## Reprodutibilidade

- `input-inventory.json` fixa 25 entradas e seus hashes;
- `build_registry.py` aborta quando uma entrada diverge;
- `provenance.jsonl` liga cada candidato à auditoria de origem;
- `consolidation-manifest.json` registra before/after, decisões e hashes;
- `sha256sums.txt` congela os artefatos finais;
- duas execuções consecutivas do consolidador e do revisor geram hashes
  idênticos;
- testes verificam referências, destinos, duplicidades, revisão, drift e UTF-8;
- zero perfis foram criados.
