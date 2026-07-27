# Contrato de pesquisa de aceleradoras

Este diretório é o artefato canônico da issue
[#68](https://github.com/djairofilho/awesome-latam-vc/issues/68) e da epic
[#62](https://github.com/djairofilho/awesome-latam-vc/issues/62). Ele define
identidade, elegibilidade, evidência, atividade e decisões para todas as
auditorias de aceleradoras.

O contrato da [epic #16](../epic-16/README.md) pode orientar proveniência,
inventários e execução, mas não pode ser copiado como regra de elegibilidade.
Aceleradoras podem ser elegíveis sem investimento direto recorrente.

## Objetivo e data de corte

O objetivo é identificar programas estruturados de aceleração que aceitem
founders externos e tenham acesso verificável para startups da América Latina.

Cada execução registra uma data de corte no formato `YYYY-MM-DD`. Atividade,
rotas de aplicação, termos e geografia são avaliados nessa data. Nenhum registro
pode converter ausência de divulgação em fato negativo.

## Unidade canônica

Há três unidades distintas:

1. `operator`: organização que opera um ou mais programas;
2. `program`: experiência estruturada de aceleração oferecida pela operadora;
3. `investment_vehicle`: veículo que eventualmente aporta capital.

Uma organização independente usa o domínio oficial normalizado como
`operator_id`. Um programa usa:

```text
<domínio-normalizado-da-operadora>#<slug-estável-do-programa>
```

Exemplo:

```text
example.org#climate-accelerator
```

O slug identifica o programa, não a turma, edição ou chamada. Edições anuais e
formulários temporários permanecem vinculados ao mesmo programa.

Aliases, nomes anteriores e URLs redirecionadas apontam para o ID canônico. Dois
programas no mesmo domínio não são deduplicados automaticamente. Um programa
corporativo e o veículo de investimento da mesma empresa também não são a mesma
entidade.

## Programa estruturado

Um candidato só pode ser `elegível` quando fontes oficiais comprovarem:

- operadora e programa identificáveis;
- proposta de aceleração com começo, fim ou percurso definido;
- seleção ou avaliação de startups externas;
- acesso explícito para ao menos um país latino-americano ou para a região;
- atividade atual conforme a regra deste contrato;
- rota oficial de candidatura, contato ou acompanhamento de chamadas;
- ausência de duplicidade com um perfil canônico já publicado.

Mentoria, conteúdo, benefícios, comunidade ou conexão com parceiros podem fazer
parte do programa, mas não bastam isoladamente.

## Atividade

Um programa é `ativo` quando existe pelo menos um destes sinais oficiais nos
24 meses anteriores à data de corte:

- chamada ou formulário atual;
- anúncio de turma, seleção ou participantes;
- execução documentada de uma turma;
- resultados ou encerramento de uma edição;
- calendário ou declaração oficial de recorrência futura.

Um formulário fechado entre turmas não torna o programa inativo. Nesse caso,
registre `application_status: closed_between_cycles` e mantenha
`activity_status: active` somente quando houver evidência de recorrência.

Uma página institucional sem sinal datado não prova atividade. Se não houver
evidência suficiente, use `activity_status: unknown` e a decisão
`evidência-insuficiente`.

Os estados de atividade são:

- `active`;
- `paused`;
- `inactive`;
- `unknown`.

O estado de candidatura é separado:

- `open`;
- `closed`;
- `closed_between_cycles`;
- `invite_only`;
- `not_publicly_disclosed`;
- `not_applicable`.

## Decisões

Status operacional e decisão editorial são dimensões diferentes.

Os status da pesquisa são:

1. `descoberto`;
2. `em-pesquisa`;
3. `decidido`;
4. `publicado`.

As decisões permitidas são:

- `elegível`;
- `duplicado`;
- `encaminhado-para-funds`;
- `encaminhado-para-outra-epic`;
- `inativo`;
- `evidência-insuficiente`;
- `excluído`.

`descoberto` e `em-pesquisa` exigem `decision: null`. `decidido` e `publicado`
exigem uma decisão. Toda decisão diferente de `elegível` exige justificativa.

`duplicado` exige um ID ou perfil canônico. `encaminhado-para-funds` e
`encaminhado-para-outra-epic` exigem destino. Toda pendência exige responsável
e próxima ação.

## Fronteiras editoriais

Use estas regras antes de decidir:

| Caso | Destino |
| --- | --- |
| Programa estruturado, seleção externa e aceleração verificável | Epic #62 |
| Veículo que decide e investe capital próprio ou comprometido recorrentemente | `funds/` |
| Rede ou clube em que membros decidem e aportam | Epic #63 |
| Plataforma neutra de ofertas, syndicates ou matchmaking | Epic #64 |
| Programa público com rota estruturada de capital | Epic #65 |
| Incubação sem programa de aceleração verificável | Excluído |
| Desafio pontual ou campanha de inovação aberta | Excluído |
| Consultoria, venture builder contratado ou CVC as a service | Excluído |
| Coworking, comunidade, evento ou diretório | Excluído |

Um programa híbrido pode ter perfil de aceleradora e referência separada a um
veículo publicado em `funds/`, desde que programa e veículo sejam descritos
como unidades distintas. O mesmo aporte não pode ser contado duas vezes.

## Acesso externo e geografia

`open_to_external_founders` só pode ser `true` quando uma fonte oficial descreve
seleção, candidatura, indicação aceita ou processo equivalente para startups
que não pertençam à operadora.

`latam_access` só pode ser `confirmed` quando a fonte oficial:

- cita América Latina;
- lista ao menos um país latino-americano elegível;
- apresenta regras globais sem restrição incompatível e uma rota utilizável a
  partir da região.

Portfólio, nacionalidade de alumni ou presença de equipe na região não comprovam
acesso. Quando a conclusão depender de regras globais, registre a regra e a
ausência de restrição como evidências separadas.

## Evidência por afirmação

Fontes de terceiros podem descobrir candidatos, mas não comprovam elegibilidade.
Cada afirmação publicável registra:

- URL oficial;
- data de acesso;
- tipo da fonte;
- localização da afirmação na página ou documento;
- resumo factual e parafraseado;
- entidade e campo sustentados;
- resultado `confirmado`, `contraditório` ou `inconclusivo`.

Exigem evidência oficial própria:

- identidade da operadora e do programa;
- estrutura e formato;
- atividade;
- acesso externo;
- geografia;
- rota de candidatura;
- capital, instrumento e equity, quando divulgados;
- duração e estágio, quando divulgados.

Capital, cheque, instrumento, equity, duração e estágio ausentes devem ser
registrados como `not_publicly_disclosed`. Nunca os inferir de portfólio,
notícias, bases de terceiros ou termos de outra edição.

## Campos canônicos

O tooling da issue #69 deve materializar, no mínimo:

- `schema_version`;
- `candidate_id`;
- `operator_id`;
- `program_id`;
- `investment_vehicle_id`;
- `canonical_candidate_id`;
- `name`;
- `aliases`;
- `entity_type`;
- `official_site`;
- `base_country`;
- `accepted_geography`;
- `program_format`;
- `duration`;
- `stage`;
- `capital_offered`;
- `instrument`;
- `equity`;
- `open_to_external_founders`;
- `latam_access`;
- `activity_status`;
- `application_status`;
- `application_url`;
- `status`;
- `decision`;
- `reason`;
- `destination`;
- `discovery_source_ids`;
- `official_evidence_ids`;
- `evidence_date`;
- `owner`;
- `next_action`.

Campos não aplicáveis usam `null`. Campos factuais não divulgados usam o
vocabulário explícito definido pelo schema, em vez de valores inventados.

## Artefatos executáveis

O contrato é materializado em:

- [schemas](schemas), em JSON Schema Draft 2020-12;
- [templates](templates), para iniciar inventários e coletas;
- [examples](examples), com um conjunto sintético completo e validado.

Cada diretório de execução usa os mesmos nomes:

```text
candidates.jsonl
coverage-matrix.jsonl
evidence.jsonl
run-manifest.jsonl
source-inventory.jsonl
```

O validador verifica schemas, cada linha JSONL e invariantes entre arquivos:
IDs únicos, referências existentes, manifesto consistente, cobertura coerente
e evidência oficial mínima para elegíveis.

Workers gravam shards isolados com:

```text
python tools/research/shards.py write \
  research/epic-62 brazil worker-1 candidates input.jsonl
```

O coordenador produz o arquivo canônico em ordem determinística:

```text
python tools/research/shards.py reduce \
  research/epic-62 candidates research/epic-62/candidates.jsonl
```

Uma divergência entre registros com o mesmo ID interrompe a redução. Registros
idênticos são idempotentes.

## Fluxo e ownership

1. O coordenador aprova matriz de cobertura, inventário e manifesto.
2. Workers de descoberta percorrem apenas fontes declaradas.
3. Um resolver normaliza URLs, operadoras, programas e aliases.
4. Workers de validação pesquisam candidatos canônicos em fontes oficiais.
5. Um consolidador reduz shards em ordem determinística.
6. Um revisor independente avalia todos os elegíveis, encaminhados e híbridos,
   além de uma amostra determinística das exclusões.
7. O manifesto é congelado com data e hash.
8. Publishers recebem somente IDs congelados.

Cada worker escreve em shard próprio. Nenhum worker altera diretamente arquivos
consolidados, índices ou perfis. O mesmo agente não aprova sozinho um caso
híbrido que tenha pesquisado.

## Exemplos de decisão

Os exemplos são ilustrativos e não constituem pesquisa real.

### Elegível

Uma operadora mantém um programa de 12 semanas, publica seleção para startups
externas, aceita explicitamente empresas do Brasil e do México e documenta uma
turma realizada há seis meses.

Decisão: `elegível`.

Motivo: programa estruturado, acesso externo, geografia latino-americana e
atividade recente são comprovados oficialmente. Capital não divulgado permanece
`not_publicly_disclosed`.

### Encaminhado

Uma organização se apresenta como fundo, decide os aportes de um veículo
recorrente e não oferece percurso estruturado de aceleração.

Decisão: `encaminhado-para-funds`.

Destino: perfil ou candidato canônico em `funds/`.

### Excluído

Uma consultoria anuncia um desafio corporativo único com workshops, sem seleção
recorrente, percurso de aceleração ou acesso público para founders.

Decisão: `excluído`.

Motivo: desafio pontual e prestação de serviço não satisfazem o contrato de
aceleradora.

## Gates de qualidade

Antes de uma auditoria regional:

- o contrato e os schemas estão versionados;
- o exemplo completo valida;
- a matriz de cobertura e o manifesto foram aprovados.

Antes da consolidação:

- toda fonte e tarefa possui estado;
- todo candidato possui decisão ou pendência acionável;
- todas as referências apontam para IDs existentes.

Antes da publicação:

- não existem IDs órfãos, decisões nulas ou duplicados sem destino;
- todos os elegíveis têm fonte oficial para programa, atividade e acesso;
- a revisão independente foi concluída;
- o manifesto foi congelado com data e hash.

Antes do fechamento:

- cada elegível foi publicado exatamente uma vez ou possui exceção documentada;
- links, UTF-8, mojibake, ordenação, schemas, testes e índices passam;
- não existe inconsistência crítica ou alta aberta.

## Encerramento de uma sub-issue

O comentário final deve informar:

- data de corte e recorte efetivamente percorrido;
- fontes por estado;
- candidatos por status e decisão;
- lacunas, responsáveis e próximas ações;
- caminhos dos artefatos e manifesto;
- validações executadas;
- confirmação de que nenhum termo foi inferido.

Cobertura declarada nunca pode exceder a matriz e o inventário registrados.
