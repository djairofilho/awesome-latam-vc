# Contrato de pesquisa da epic 64

Este diretório é o artefato canônico da issue
[#89](https://github.com/djairofilho/awesome-latam-vc/issues/89). Ele define
como as issues #90 a #96 descobrem, auditam, consolidam e publicam plataformas
de captação para startups da América Latina.

## Princípio de elegibilidade

A unidade publicável é a **plataforma**, identificada por `platform_id`. Uma
plataforma é elegível quando:

1. oferece uma rota oficial e estruturada para founders captarem recursos;
2. a rota aceita startups de ao menos um país latino-americano;
3. está aberta ou possui ciclos recorrentes confirmados;
4. possui sinal oficial de atividade nos 24 meses anteriores à data de corte;
5. suas alegações de elegibilidade são sustentadas por fontes oficiais.

O contrato não exige nem registra investimento direto da própria plataforma.
Uma plataforma pode apenas intermediar a captação entre startups e terceiros.

`open` significa uma rota utilizável no momento da verificação.
`recurring_closed` significa que o ciclo atual está fechado, mas uma fonte
oficial confirma a recorrência. Os dois estados são diferentes e ambos podem
ser elegíveis.

## Taxonomia e identidade

Cada candidato separa seis entidades que não podem ser confundidas:

| Entidade | ID | Papel |
| --- | --- | --- |
| Operador legal | `operator_id` | Pessoa jurídica responsável pela operação |
| Marca | `brand_id` | Nome público e aliases |
| Plataforma | `platform_id` | Rota permanente e unidade publicável |
| Produto | `product_id` | Instrumento ou modalidade oferecida |
| Oferta | `offer_id` | Campanha ou rodada temporária |
| Registro regulatório | `regulatory_id` | Registro ou autorização em uma jurisdição |

O domínio oficial normalizado e a marca iniciam a primeira passagem de
deduplicação. A identidade legal e os registros regulatórios formam a segunda.
O `platform_id` é imutável. Uma duplicata aponta para
`canonical_platform_id` ou para um perfil já publicado.

Uma oferta sempre possui `profile_eligible: false`. Oferta aberta, encerrada ou
cancelada pode comprovar atividade ou ilustrar um produto, mas nunca vira perfil
permanente. A plataforma permanece a unidade canônica.

## Escopo e fronteiras

Inclua plataformas de equity crowdfunding, dívida, revenue share, instrumentos
conversíveis, syndicates, matching ou outro mecanismo estruturado de captação
para startups.

Exclua:

- doações e recompensas sem mecanismo de financiamento empresarial;
- ICOs e vendas de tokens;
- P2P genérico sem rota específica para startups;
- ofertas individuais encerradas sem plataforma recorrente;
- diretórios, marketplaces informativos ou formulários sem fluxo de captação;
- serviços destinados somente a investidores, sem rota para founders.

As fronteiras com as outras categorias são:

- `funds/`: gestores ou veículos que investem capital próprio diretamente;
- epic #62: programas de aceleração com seleção e suporte estruturado;
- epic #63: redes que organizam investidores-anjo;
- epic #65: programas públicos que concedem ou operam apoio estatal.

Uma organização pode exercer mais de um papel, mas cada perfil deve representar
uma categoria e uma rota distintas. Colisão conhecida deve ser registrada antes
da publicação.

## Estados e decisões

Os status são `discovered`, `researching`, `decided` e `published`.
`discovered` e `researching` usam `decision: null`.
`decided` e `published` exigem uma decisão:

- `eligible`;
- `duplicate`;
- `inactive`;
- `insufficient_evidence`;
- `excluded`;
- `other_category`.

Toda decisão diferente de `eligible` exige motivo. Evidência insuficiente exige
responsável e próxima ação. Nenhum candidato pode chegar ao freeze como
indeciso.

## Evidência

Terceiros servem para descoberta. As fontes oficiais permitidas para comprovar
rota, acesso geográfico e atividade são a plataforma, o operador, um regulador
ou um documento oficial.

Alegações de situação regulatória exigem `source_type` igual a
`official_regulator` ou `official_document`. O `subject_id` da evidência deve
ser o mesmo `regulatory_id` do registro. Comunicação da própria plataforma não
comprova autorização regulatória.

Cada evidência registra:

- sujeito e ID ao qual se aplica;
- URL, publicador e tipo de fonte;
- data de publicação, quando disponível, data observada do evento e data de acesso;
- alegações confirmadas, refutadas ou não divulgadas;
- localizador e resumo factual parafraseado.

Uma atividade somente é recente quando `observed_on` está entre a data de corte
e os 24 meses anteriores e coincide com `last_official_activity_on`. Não infira
atividade atual da publicação de uma página nem de uma oferta antiga.

## Matriz país por tipo de fonte

A [matriz inicial](coverage-matrix.jsonl) cobre os 20 países latino-americanos
do recorte e encaminha cada país à issue regional correspondente:

- #90: Brasil;
- #91: México, América Central e Caribe;
- #92: países andinos;
- #93: Cone Sul.

Cada país possui as quatro categorias obrigatórias:

1. regulador;
2. ecossistema público;
3. plataforma oficial;
4. descoberta.

Cada célula evolui de `planned` para `complete` ou `gap_justified`. Uma lacuna
justificada exige motivo, responsável e próxima ação. A matriz limita a alegação
de cobertura ao recorte efetivamente inventariado.

## Arquivos

```text
research/epic-64/
├── coverage-matrix.jsonl
├── examples/
├── schemas/
├── templates/
├── tests/
└── validate.py
```

Cada diretório de auditoria usa cinco arquivos:

- `candidates.jsonl`;
- `evidence.jsonl`;
- `source-inventory.jsonl`;
- `coverage-matrix.jsonl`;
- `run-manifest.jsonl`.

Cada linha JSONL é um objeto UTF-8 independente. Os
[templates](templates) são um ponto de partida válido. O
[exemplo](examples) é inteiramente fictício, valida uma plataforma elegível e
demonstra que uma oferta encerrada permanece subordinada à plataforma.

## Execução paralela

O coordenador cria uma execução e particiona tarefas por região, domínio e
worker. Cada tarefa declara `worker_id` e `shard_path`. Um worker possui um
único shard, e um shard não pode pertencer a workers diferentes. Cada worker
escreve somente no próprio diretório:

```text
research/epic-64/<região>/shards/<worker-id>/
```

Não há append concorrente em arquivos compartilhados. O reducer é o único
escritor dos artefatos regionais consolidados. Tarefas e reduções devem ser
idempotentes e reentrantes.

O destino regional define o escopo do reducer. Por exemplo:

```text
python tools/research/shards.py reduce \
  research/epic-64 evidence research/epic-64/mexico-cac/evidence.jsonl
```

Uma execução concluída pode congelar `hash_algorithm: sha256` e
`artifact_hashes` para os quatro artefatos não circulares: candidatos,
evidências, inventário de fontes e matriz de cobertura. O validador recalcula
os hashes com finais de linha normalizados em LF. O manifesto não inclui o
próprio hash.

O manifesto fixa estas regras:

- respeitar `robots.txt` e termos de uso;
- nunca contornar autenticação, CAPTCHA, WAF ou outro controle de acesso;
- no máximo duas requisições simultâneas por domínio;
- intervalo mínimo de 500 ms;
- cache obrigatório;
- no máximo quatro tentativas com backoff;
- navegador somente para páginas oficiais dependentes de JavaScript.

Uma tarefa bloqueada exige motivo, responsável e próxima ação. Conteúdo
inacessível vira pendência manual, não tentativa de evasão.
Tarefas `leased`, `extracted` e `verified` também exigem responsável e próxima
ação. Uma execução `complete` contém somente tarefas `done` ou `blocked`.

## Invariantes de fechamento

O validador verifica JSON Schema e também:

- IDs únicos e referências sem órfãos;
- correspondência entre oferta e produto;
- rota estruturada e acesso latino-americano comprovados oficialmente;
- atividade oficial dentro da janela de 24 meses;
- alegação regulatória ligada ao registro e à fonte oficial;
- oferta permanentemente inelegível como perfil;
- quatro tipos de fonte por país;
- fontes concluídas presentes no inventário;
- fontes concluídas com inventário também concluído;
- país e categoria das fontes concluídas iguais aos da célula de cobertura;
- `task_count`, `run_id` e IDs de tarefa consistentes;
- ownership exclusivo e caminhos seguros de shard;
- ausência do campo `direct_investment`.

Antes do freeze, o revisor também deve confirmar zero duplicatas conhecidas,
zero candidatos indecisos e zero colisões com categorias existentes.

## Validação

Instale a dependência isolada do validador e execute:

```powershell
python -m pip install -r research/epic-64/requirements.txt
python research/epic-64/validate.py
python -m unittest discover -s research/epic-64/tests -v
python tools/research/validate.py --base-ref origin/main
git diff --check origin/main...HEAD
```

Para validar um shard ou conjunto regional adicional:

```powershell
python research/epic-64/validate.py --dataset research/epic-64/<região>
```

O comando padrão valida os schemas, templates, o exemplo e a matriz inicial.
Uma auditoria regional só começa depois do merge deste contrato.
