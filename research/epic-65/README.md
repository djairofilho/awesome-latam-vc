# Contrato de pesquisa da epic 65

Este diretório é o artefato canônico da issue
[#97](https://github.com/djairofilho/awesome-latam-vc/issues/97). Ele define
como as issues #98 a #104 registram agências públicas, programas financeiros e
chamadas temporárias.

## Regra central

O contrato mede acesso estruturado a capital ou financiamento público para
startups. Ele não exige investimento direto e não reutiliza a regra de
elegibilidade de `funds/`.

Uma entidade só pode receber a decisão `elegível` quando fontes oficiais
confirmam:

- benefício financeiro, como subvenção, cofinanciamento, crédito, garantia,
  capital ou instrumento conversível;
- rota oficial para startups;
- intake permanente, chamada aberta ou recorrência oficial nos 24 meses
  anteriores à data de avaliação.

Diretórios, notícias e bases de terceiros podem descobrir rotas. Somente portais
e documentos oficiais comprovam elegibilidade, atividade, valores,
contrapartidas e condições.

## Três entidades, três IDs

| Entidade | ID | O que representa | Pode receber perfil |
| --- | --- | --- | --- |
| Agência | `agency_id` | Organização pública estável que opera ou encaminha vários instrumentos | Sim, quando é a rota estável |
| Programa | `program_id` | Instrumento permanente ou recorrente com benefício e rota próprios | Sim |
| Chamada | `call_id` | Janela, edição ou processo seletivo temporário de um programa | Nunca |

Os vínculos são explícitos:

```text
agency_id
    └── program_id
            └── call_id
```

O mesmo órgão pode ter vários programas. O mesmo programa pode ter várias
chamadas ao longo do tempo. Marcas, siglas e traduções ficam em `aliases`; elas
não geram novos IDs. Duplicatas apontam para `canonical_agency_id` ou
`canonical_program_id` existente no mesmo bundle. Autorreferências, ciclos e
caminhos de perfil com segmentos `.` ou `..` são inválidos.

## Status separados

`research_status` descreve o andamento da pesquisa. `decision` registra a
decisão editorial.

O campo `program_status` aceita:

- `ativo`;
- `fechado agora, recorrente`;
- `inativo`;
- `não confirmado`.

O campo `call_status` aceita:

- `aberta`;
- `fechada`;
- `prevista`;
- `não confirmada`.

Esses status não são intercambiáveis. Um programa pode estar
`fechado agora, recorrente` enquanto sua chamada mais recente está `fechada`.
Isso não autoriza dizer que inscrições estão abertas.

## Atividade em 24 meses

Um programa elegível usa exatamente uma base de atividade:

- `intake permanente`;
- `chamada aberta`;
- `recorrência oficial em 24 meses`.

`latest_official_signal_on` registra a data do sinal e `assessed_on` registra a
data de avaliação. A evidência correspondente registra a data do evento ou da
observação em `observed_on`; o validador exige que ela coincida com o sinal. Para
`intake permanente`, o intake precisa ser observado na data da avaliação. Para
recorrência, a mesma data deve possuir afirmação oficial confirmada de
recorrência. O validador rejeita sinal posterior à avaliação ou anterior à
janela de 24 meses.

O status de uma chamada é um retrato em `captured_on`. Uma chamada `aberta` não
pode ter sido capturada antes de `opened_on` nem depois de `closes_on`, quando
essas datas são conhecidas. De forma análoga, uma chamada `fechada` não pode ser
capturada antes de sua abertura ou de seu fechamento, e uma chamada `prevista`
não pode conservar esse status na data ou depois de `opened_on`.

Uma página antiga sem intake atual, chamada aberta ou recorrência confirmada não
comprova atividade. `Fechado agora, recorrente` exige evidência oficial de
recorrência, não apenas uma chamada encerrada.

## Unidade de publicação

Uma agência recebe perfil quando sua página institucional é a rota estável para
múltiplos instrumentos e há ao menos um programa elegível vinculado. Um programa
recebe perfil quando possui benefício, rota e identidade duráveis.

Uma chamada nunca recebe perfil. Seus valores, contrapartida, datas e
elegibilidade ficam em `calls.jsonl` e só valem para aquela `call_id`. O schema
fixa `profile_eligible: false` e `canonical_profile: null`.

## Exclusões

Registrar como `excluído`, `inativo` ou `evidência insuficiente`, conforme o
caso:

- política pública sem programa operacional;
- prêmio isolado;
- contratação pública;
- incentivo fiscal sem rota de capital ou financiamento;
- notícia ou anúncio sem operação comprovada;
- chamada encerrada sem evidência de recorrência;
- capacitação, mentoria ou aceleração sem benefício financeiro;
- veículo privado apresentado apenas em parceria com governo.

Toda decisão negativa exige `reason`. Pendências devem indicar `owner` e
`next_action`.

## Matriz país por fonte

Cada auditoria começa por
[`coverage-matrix.jsonl`](templates/coverage-matrix.jsonl). Uma linha representa
uma fonte oficial efetivamente percorrida em um país. Os tipos são:

1. agência de inovação;
2. ministério responsável;
3. banco público de desenvolvimento;
4. portal oficial de chamadas;
5. fonte subnacional oficial, quando material.

As frentes devem cobrir os países declarados nas issues:

- Brasil;
- México, América Central e Caribe;
- Bolívia, Colômbia, Equador, Peru e Venezuela;
- Argentina, Chile, Paraguai e Uruguai.

Cada frente detalha os países efetivamente incluídos antes da coleta. Uma lacuna
usa `parcial` ou `indisponível` com motivo, responsável e próxima ação. A matriz
comprova o recorte percorrido, não a inexistência de outras fontes.

## Arquivos

Cada bundle contém:

| Arquivo | Responsabilidade |
| --- | --- |
| `agencies.jsonl` | Agências, rotas institucionais e programas vinculados |
| `programs.jsonl` | Benefício, rota, atividade e decisão dos programas |
| `calls.jsonl` | Estado e condições restritas a cada chamada |
| `evidence.jsonl` | Evidências oficiais e afirmações que elas sustentam |
| `coverage-matrix.jsonl` | Cobertura país por fonte |
| `run-manifest.jsonl` | Execução, tarefas, workers e shards exclusivos |

Os schemas JSON Schema Draft 2020-12 ficam em [schemas](schemas). Os modelos
iniciais ficam em [templates](templates). O bundle [examples](examples) mostra a
separação entre CORFO, Start-Up Chile e sua rota atual de candidatura.

O exemplo reaproveita o baseline CORFO já publicado. Ele demonstra o contrato,
não substitui a revalidação da issue #101 e não afirma que uma chamada esteja
aberta. Por isso, a chamada de exemplo usa `call_status: "não confirmada"` e
não registra valores.

## Evidência e proveniência

Cada evidência pertence a uma única entidade por `subject_type` e `subject_id`.
Os registros elegíveis precisam de evidências vinculadas à mesma entidade.
`published_on` registra a publicação, quando conhecida; `observed_on` registra
a data do evento ou da observação oficial; `accessed_on` registra a consulta.

Para um programa elegível, evidências oficiais devem confirmar:

- `benefício financeiro`;
- `rota para startups`;
- `atividade do programa`.

Valores e contrapartidas só podem ser preenchidos quando a fonte da chamada os
confirma. `não divulgado` significa que a fonte consultada não informou o dado;
não significa zero.

## Execução paralela

O coordenador cria o manifesto antes da coleta. Cada tarefa combina país e tipo
de fonte, tem um `worker_id` e grava apenas no `shard_path` atribuído:

```text
research/epic-65/<região>/shards/<worker-id>/
```

Workers não fazem append em arquivos compartilhados. A consolidação posterior
reduz os shards de forma determinística, resolve IDs e verifica referências. O
`task_count` do manifesto deve coincidir com a quantidade de tarefas. Uma tarefa
`bloqueada` exige motivo e próxima ação. Cada `shard_path` pertence a uma única
tarefa e a um único `worker_id`; caminhos repetidos no manifesto são inválidos.
Segmentos `.` e `..` são proibidos. Cada par país × tipo de fonte aparece uma
única vez na matriz e em uma tarefa correspondente. Uma execução `concluída`
não pode manter tarefas `todo` ou `em execução`.

## Fronteiras com outros catálogos

- [`funds/`](../../funds/README.md) contém investidores diretos recorrentes.
  Benefício público não transforma uma agência em fundo.
- [Aceleradoras](../../ecosystem/accelerators/README.md) pertencem à epic #62.
  Um programa público de aceleração só entra nesta epic quando também oferece
  benefício financeiro estruturado.
- [Redes-anjo](../../ecosystem/angel-networks/README.md) pertencem à epic #63.
  Uma rede apoiada pelo governo continua sendo rede-anjo.
- [Plataformas de captação](../../ecosystem/funding-platforms/README.md)
  pertencem à epic #64. Uma plataforma pública sem instrumento financeiro
  próprio é encaminhada para essa categoria.

Casos híbridos preservam uma entidade canônica e registram o motivo do
encaminhamento. Não duplicar o mesmo perfil entre categorias.

## Validação

O validador requer Python 3.9 ou superior e `jsonschema`:

```powershell
python research/epic-65/validate.py
python -m unittest discover -s research/epic-65/tests -v
python tools/research/validate.py --base-ref origin/main
git diff --check origin/main...HEAD
```

Sem argumentos, `validate.py` valida `templates` e `examples`. Para validar um
ou mais bundles de coleta:

```powershell
python research/epic-65/validate.py `
  research/epic-65/brazil `
  research/epic-65/andean
```

Além dos schemas, o validador verifica:

- IDs únicos;
- referências e vínculos bidirecionais;
- evidência pertencente à entidade que a cita;
- benefício, rota e atividade comprovados em programas elegíveis;
- janela de atividade de 24 meses;
- datas de publicação, acesso, abertura e fechamento;
- chamada impossibilitada de receber perfil;
- contagem e `run_id` das tarefas do manifesto.

Nenhuma auditoria deve começar antes do merge deste contrato.
