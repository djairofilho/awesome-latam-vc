# Contrato de pesquisa de redes-anjo

Este diretório é o artefato canônico da
[#80](https://github.com/djairofilho/awesome-latam-vc/issues/80). Ele define
como as issues #81 a #88 descobrem, validam, decidem e publicam redes-anjo,
clubes, alumni networks, capítulos e syndicates da epic
[#63](https://github.com/djairofilho/awesome-latam-vc/issues/63).

## Estrutura

```text
research/epic-63/
├── examples/       # conjunto completo que passa pelo validador
├── schemas/        # JSON Schema Draft 2020-12, um schema por linha JSONL
├── templates/      # ponto de partida válido para novas auditorias
├── tests/          # testes do contrato e das invariantes relacionais
├── requirements.txt
└── validate.py
```

Os arquivos usam UTF-8, uma linha JSON por registro e datas `YYYY-MM-DD`.
`schema_version` permite evoluir o contrato sem reinterpretar coletas antigas.

## Unidade canônica e ID

O registro canônico representa a organização que mantém o processo recorrente.

| Tipo | Unidade | Regra de ID |
|---|---|---|
| Rede ou clube independente | Organização no domínio oficial | `ang-` + domínio normalizado |
| Alumni network independente | Organização no domínio oficial | `ang-` + domínio normalizado |
| Syndicate com site próprio | Organização no domínio oficial | `ang-` + domínio normalizado |
| Syndicate hospedado | Operador + slug oficial do syndicate | `ang-` + domínio + `--` + slug |
| Capítulo autônomo | Rede matriz + slug estável do capítulo | ID da matriz + `--` + slug |
| Capítulo não autônomo | Alias da rede matriz | não recebe registro publicável |

Normalize o domínio removendo protocolo, `www.`, porta, caminho, parâmetros,
fragmento e ponto final. Converta para minúsculas e substitua pontos por hífens
no ID. `https://www.Exemplo.org.br/rede` vira
`ang-exemplo-org-br`.

Redes com o mesmo domínio não são automaticamente duplicadas. Preserve
operador legal, marca, redirects, equipe, endereço, rota de apresentação e
relações entre matriz e capítulos. Compartilhar membros, universidade ou
plataforma também não basta para mesclar registros.

### Capítulos e aliases

`chapter_identity: "standalone"` exige evidência oficial para quatro autonomias:

1. processo de seleção próprio;
2. autoridade de decisão própria;
3. geografia operacional própria;
4. atividade recente própria.

As quatro flags de `chapter_autonomy` precisam ser `true` e
`parent_network_id` precisa apontar para a matriz. Se algum ponto não for
comprovado, use `chapter_identity: "alias"` e
`canonical_network_id` com o ID da matriz. Um alias pode permanecer em pesquisa,
mas só pode ser decidido como `duplicado`. O destino canônico precisa ser um
registro que não seja alias; cadeias e ciclos de aliases são inválidos.

As evidências de autonomia usam quatro afirmações atômicas:
`autonomia de seleção`, `autonomia de decisão`, `autonomia geográfica` e
`autonomia de atividade recente`. Uma afirmação genérica de autonomia não
substitui nenhuma delas.

Aliases de nome, marca anterior e capítulo ficam em `aliases`. O nome canônico é
o nome usado atualmente pela organização em fonte oficial.

## Fronteiras de categoria

- Rede ou clube que organiza investidores membros: epic #63.
- Alumni network com processo recorrente de seleção e investimento: epic #63.
- Syndicate recorrente com seleção própria: epic #63.
- Plataforma neutra que hospeda ofertas ou conecta participantes: epic #64.
- Aceleradora com programa estruturado: epic #62.
- Agência ou programa público: epic #65.
- Gestor que decide e aporta capital agrupado de forma recorrente: `funds/`.
- Comunidade ou mentoria sem processo de investimento: `excluído`.
- Investidor individual: `excluído`.

Casos encaminhados não são descartados. Use a decisão correspondente e informe
`canonical_profile` quando o destino já existir.

## Seleção, decisão e capital

Os campos abaixo são independentes e nunca podem ser combinados em uma descrição
genérica de “investidor”:

- `selection_actors`: quem recebe, filtra ou apresenta oportunidades;
- `decision_actors`: quem decide participar de uma oportunidade;
- `capital_actors`: quem efetivamente aporta o capital.

Cada ator declara nome e tipo. Informação não publicada usa o ator
`{"name": "não divulgado", "actor_type": "não divulgado"}`. Não deduza autoridade
de decisão ou fonte do capital a partir de nomes de membros, portfólio ou
terceiros.

## Status e decisão

Status operacional e decisão editorial são dimensões separadas.

Status:

1. `descoberto`: ainda não houve validação oficial suficiente;
2. `em pesquisa`: validação em andamento;
3. `decidido`: decisão revisada;
4. `publicado`: perfil incorporado ao catálogo.

Decisões:

- `elegível`;
- `duplicado`;
- `encaminhado-para-funds`;
- `encaminhado-para-aceleradoras`;
- `encaminhado-para-plataformas`;
- `encaminhado-para-programas-públicos`;
- `inativo`;
- `evidência-insuficiente`;
- `excluído`.

`descoberto` e `em pesquisa` exigem `decision: null`. `decidido` e `publicado`
exigem decisão. Toda decisão diferente de `elegível` exige `reason`.

Qualquer registro pendente precisa de `owner` e `next_action`. Isso inclui
status ainda não decidido, `evidência-insuficiente`, fonte parcial ou
indisponível, tarefa ainda não concluída e célula de cobertura parcial ou
pendente.

## Elegibilidade e evidência

Um candidato `elegível` precisa ter:

- tipo `rede`, `clube`, `alumni network`, `capítulo` ou `syndicate`;
- site oficial;
- processo recorrente de seleção;
- fonte oficial que confirme a categoria;
- fonte oficial de atividade recente;
- fonte oficial de acesso externo ou explícito à América Latina;
- atores de seleção, decisão e capital separados;
- `activity_status` igual a `confirmada-recente` ou
  `entre-ciclos-recorrente`;
- `external_access` igual a `aberto` ou `explícito-américa-latina`;
- rota de candidatura ou contato quando publicamente disponível.

Atividade recente exige uma fonte oficial publicada ou atualizada no intervalo
de 24 meses anterior à `cutoff_date`. Pode ser chamada, turma, seleção,
investimento, evento de pitches ou resultado operacional. Um formulário fechado
entre ciclos não prova inatividade. Se houver recorrência oficial recente, use
`entre-ciclos-recorrente`.

`external_access: "aberto"` significa que founders externos podem apresentar uma
startup. `explícito-américa-latina` confirma também o recorte regional.
Processo apenas por indicação ou só para membros não é tratado como acesso
externo. Ausência pública vira `não confirmado`, nunca uma inferência positiva.

Cheque, instrumento, termos, liderança e frequência não divulgados permanecem
desconhecidos.

## Artefatos

### Inventário de fontes

[source-inventory.jsonl](templates/source-inventory.jsonl) registra o recorte
antes da coleta. Diretórios e notícias servem para descoberta. Categoria,
atividade e acesso de um elegível exigem evidência oficial.

### Candidatos

[candidates.jsonl](templates/candidates.jsonl) é a fila canônica. IDs de fontes e
evidências ligam os artefatos sem copiar trechos. Cada candidato aparece uma
única vez após a redução dos shards.

### Evidências

[evidence.jsonl](templates/evidence.jsonl) registra afirmações atômicas. `summary`
é factual e parafraseado. `locator` identifica a seção relevante sem armazenar
texto extenso.

### Matriz de cobertura

[coverage-matrix.jsonl](templates/coverage-matrix.jsonl) possui uma célula por
combinação de país ou região e categoria de fonte. O inventário vinculado prova
o que foi percorrido. Cobertura não pode ser declarada além desse inventário.

### Manifesto

[run-manifest.jsonl](templates/run-manifest.jsonl) começa com um registro `run` e
segue com tarefas. Cada worker grava apenas seu shard em:

```text
research/epic-63/<frente>/shards/<worker-id>/
```

Não há append concorrente em arquivos compartilhados. O consolidador é o único
escritor dos artefatos canônicos. Tarefas são idempotentes, recebem lease e podem
ser repetidas sem duplicar registros.

## Regras de scraping

- no máximo 8 requisições HTTP globais e 2 por domínio;
- no máximo 2 navegadores simultâneos;
- timeout de 20 segundos;
- até 3 tentativas para `429` e `5xx`, com backoff e jitter;
- cache pela URL final após redirects;
- browser apenas para conteúdo oficial dependente de JavaScript;
- respeitar `robots.txt`, termos, autenticação, CAPTCHA e WAF;
- registrar bloqueios como pendência manual, sem evasão.

## Validação

Instale a dependência e valide o exemplo:

```bash
python -m pip install -r research/epic-63/requirements.txt
python research/epic-63/validate.py research/epic-63/examples
python -m unittest discover -s research/epic-63/tests -v
```

O validador verifica schemas e invariantes entre arquivos:

- IDs únicos e referências existentes;
- status e decisão compatíveis;
- pendências com responsável e próxima ação;
- elegível com evidências oficiais de categoria, atividade e acesso;
- atividade oficial dentro da janela de 24 meses;
- capítulo autônomo com quatro autonomias comprovadas;
- alias e duplicado com destino canônico;
- datas de publicação anteriores ou iguais ao acesso;
- manifesto com `task_count` correto e tarefas da mesma execução;
- matriz sem células duplicadas e com fontes existentes.

O diretório [examples](examples) contém uma rede fictícia baseada em
`example.org`. Ele demonstra o formato sem afirmar uma pesquisa real.

## Gate para as auditorias

As issues #81 a #85 só começam depois que este contrato estiver integrado. Cada
auditoria publica inventário, matriz e manifesto antes do scraping. O fechamento
informa data de corte, recorte percorrido, totais por status e decisão, lacunas,
responsáveis e próximas ações.
