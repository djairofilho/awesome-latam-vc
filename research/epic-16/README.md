# Contrato de pesquisa da epic 16

Este diretório é o artefato canônico da issue
[#17](https://github.com/djairofilho/awesome-latam-vc/issues/17). Ele define
como as issues #18 a #29 registram descoberta, triagem, evidência e decisão.

## Princípios

- Use o domínio oficial normalizado como identificador principal.
- Preserve aliases, marcas anteriores, veículos e todas as fontes de descoberta.
- Trate diretórios, notícias e bases de terceiros apenas como descoberta.
- Exija site e evidência oficiais de investimento direto para `elegível`.
- Prefira sinais de atividade publicados nos 24 meses anteriores à data de corte.
- Classifique ausência pública como `evidência insuficiente`, sem inferir exclusão.
- Não use o arquivo local de startups para descoberta, priorização, comprovação
  ou decisão.
- Registre datas como `YYYY-MM-DD` e URLs absolutas.
- Grave cada registro JSONL em uma única linha UTF-8.

## Estrutura

```text
research/epic-16/
├── examples/       # exemplo completo e revisado
├── manifests/      # execuções planejadas ou realizadas
├── schemas/        # contrato JSON Schema Draft 2020-12
└── templates/      # modelos válidos para iniciar novas coletas
```

Os schemas validam cada linha individual de seu arquivo JSONL. O campo
`schema_version` permite evoluir o contrato sem reinterpretar dados antigos.

## Identidade e deduplicação

Normalize o domínio removendo protocolo, `www.`, porta, caminho, parâmetros,
fragmento e ponto final. Converta o resultado para minúsculas. Por exemplo,
`https://www.Exemplo.com.br/fundos?id=1` vira `exemplo.com.br`.

Use `candidate_id` como identificador imutável do registro. Se duas descobertas
apontarem para a mesma organização, mescle suas fontes no mesmo candidato. Um
alias ou veículo que precise permanecer separado deve preencher
`canonical_candidate_id`. Toda decisão `duplicado` deve apontar para
`canonical_profile` ou `canonical_candidate_id`.

Não una automaticamente veículos distintos administrados pelo mesmo gestor.
Use `entity_type` para distinguir gestor, veículo, programa corporativo e
organização.

## Fluxo de trabalho

Os únicos status são:

1. `descoberto`: identificado, ainda sem pesquisa oficial suficiente;
2. `em pesquisa`: validação oficial em andamento;
3. `decidido`: decisão registrada e revisada;
4. `publicado`: perfil incorporado ao repositório.

As únicas decisões são:

- `elegível`;
- `duplicado`;
- `ecossistema`;
- `inativo`;
- `evidência insuficiente`;
- `excluído`.

Status e decisão são dimensões diferentes. `descoberto` e `em pesquisa` usam
`decision: null`. `decidido` e `publicado` exigem uma decisão. Toda decisão
diferente de `elegível` exige `reason`.

## Arquivos de dados

### Inventário de fontes

Use [source-inventory.jsonl](templates/source-inventory.jsonl) antes da coleta.
Cada linha descreve a fonte, o recorte percorrido e o resultado. `parcial` e
`indisponível` exigem `reason`, `next_action` e `owner`.

### Candidatos

Use [candidates.jsonl](templates/candidates.jsonl) para a fila canônica. Os
campos `discovery_source_ids` e `official_evidence_ids` ligam o candidato aos
outros artefatos sem copiar a evidência.

Para `elegível`, são obrigatórios:

- `official_site`;
- `direct_investment: true`;
- ao menos um `official_evidence_id`;
- `evidence_date`.

Além do schema, o revisor deve confirmar que ao menos uma evidência vinculada
tem `source_type: "oficial"`, `finding: "confirmado"` e sustenta
`investimento direto`.

### Evidências

Use [evidence.jsonl](templates/evidence.jsonl) para registrar o que uma página
comprova. `summary` deve ser factual e parafraseado. `locator` identifica a
seção, título ou trecho relevante sem armazenar cópias extensas.

Uma página de portfólio isolada não comprova o modelo operacional atual. Não
infira tese, cheque, estágio ou preferência de liderança a partir de terceiros
ou da composição do portfólio.

### Manifesto de execução

Use [run-manifest.jsonl](templates/run-manifest.jsonl). A primeira linha é
`record_type: "run"`; as seguintes são tarefas da mesma `run_id`. `task_count`
deve coincidir com a quantidade de tarefas. Uma execução planejada usa
`status: "planejada"` e tarefas `todo`.

O [piloto de dez URLs](manifests/pilot-10-urls.jsonl) apenas declara a primeira
execução. `scraping_performed: false` confirma que nenhuma página foi coletada.

## Invariantes entre arquivos

JSON Schema valida linhas, mas o fechamento de cada issue também deve verificar:

- todos os IDs são únicos dentro de seu tipo;
- todas as referências apontam para registros existentes;
- `task_count` coincide com as tarefas do manifesto;
- toda decisão `elegível` possui a evidência oficial descrita acima;
- toda decisão `duplicado` possui destino canônico;
- toda pendência possui `owner` ou `next_action`;
- a data de evidência não é posterior à data de acesso;
- nenhuma fonte ou nota registra uso do arquivo local de startups.

## Exemplo revisado

O diretório [examples](examples) representa uma descoberta do perfil já
publicado da ACE Ventures. Ele demonstra:

- inventário concluído;
- evidência oficial de investimento direto;
- candidato com status `decidido` e decisão `duplicado`;
- referência ao perfil canônico;
- manifesto concluído com uma tarefa.

O exemplo documenta o formato e não constitui nova pesquisa da epic.

## Encerramento de uma issue

O comentário final deve apontar para os artefatos versionados e informar:

- data de corte e recorte efetivamente percorrido;
- total de fontes por resultado;
- total de candidatos por status e decisão;
- lacunas, responsáveis e próximas ações;
- manifesto da execução;
- confirmação de que o arquivo local de startups não foi usado.

Não declare cobertura além do inventário registrado.
