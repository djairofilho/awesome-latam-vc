# Auditoria de redes-anjo no Brasil

Resultado da issue
[#82](https://github.com/djairofilho/awesome-latam-vc/issues/82), conforme o
contrato da issue #80 e com data de corte em 27 de julho de 2026. Esta etapa
decide candidatos e lacunas; nenhum perfil foi publicado.

## Resultado

Foram percorridas 12 fontes planejadas, 11 concluídas e uma indisponível. Dez
candidatos receberam decisão:

| Decisão | Quantidade |
| --- | ---: |
| `elegível` | 2 |
| `evidência-insuficiente` | 5 |
| `inativo` | 1 |
| `duplicado` | 1 |
| `encaminhado-para-funds` | 1 |

Curitiba Angels e PUC angels são elegíveis. Ambas comprovam processo recorrente,
acesso externo, atores separados e atividade oficial datada dentro da janela de
24 meses. Elas seguem para consolidação na issue #86; nenhum perfil foi criado.

Gávea Angels, Poli Angels, Rede Sororitê e WIM Angels publicam sinais atuais de
identidade ou operação, mas não uma atividade de investimento com data oficial
precisa dentro da janela exigida. Floripa Angels ficou com evidência insuficiente
porque o domínio não resolveu no DNS. Esses cinco casos preservam responsável e
próxima ação, sem converter ausência de prova em inatividade.

MIT Alumni Angels Brazil foi classificada como inativa porque o último evento
datado na fonte oficial ocorreu em 26 de abril de 2023. O MIA foi marcado como
duplicado da Anjos do Brasil, conforme declaração da própria organização. Bossa
Invest foi encaminhada ao perfil canônico em `funds/`, pois se apresenta como
venture capital com tese e processo de análise próprios.

## Cobertura e lacunas

- Sudeste: Gávea Angels foi percorrida como rede regional; Poli Angels e PUC
  angels entraram na frente de alumni networks.
- Sul: Curitiba Angels foi concluída; Floripa Angels permanece como lacuna
  técnica por falha de DNS.
- Redes de mulheres: Sororitê, WIM Angels e MIA foram decididas
  individualmente, separando rede, alias e fundo.
- Associação e diretório nacional: Anjos do Brasil e o relatório nacional foram
  usados apenas para descoberta e controle, sem repetir o baseline da issue
  #81.
- Fronteira editorial: Bossa Invest foi mantida como candidato decidido e
  encaminhada ao catálogo de fundos.

A auditoria não encontrou diretório oficial nacional completo e atualizado que
permita afirmar cobertura exaustiva por estado. Essa limitação permanece como
lacuna acionável para a consolidação.

## Controles de execução

- 12 fontes gravadas em 12 shards exclusivos, mais um shard do coordenador;
- 13 tarefas finais: 12 concluídas e uma bloqueada com owner e próxima ação;
- reducer limitado à partição `issue-82`;
- segunda redução com hashes SHA-256 idênticos nos cinco artefatos;
- 17 URLs oficiais únicas verificadas: 16 responderam HTTP 200 e Floripa Angels
  permaneceu como a falha de DNS já registrada;
- validação contratual e validação central aprovadas;
- zero perfis publicados.

## Artefatos

- `source-inventory.jsonl`: inventário e estado de cada fonte;
- `candidates.jsonl`: decisões e destinos editoriais;
- `evidence.jsonl`: evidência oficial por afirmação;
- `coverage-matrix.jsonl`: cobertura por geografia e categoria;
- `run-manifest.jsonl`: execução, ownership e bloqueios;
- `shards/`: saídas exclusivas preservadas para auditoria;
- `build_audit.py`: materialização determinística dos shards.

| Artefato | SHA-256 |
| --- | --- |
| `candidates.jsonl` | `e576f195b5fc1c8e572dd6a260db89fb16199066dd8e4207fd0e5bfb87fe709b` |
| `coverage-matrix.jsonl` | `c019a3b8cea22868402496edb0ba3447e2585c2b0ccf1798d03f76e47f987bdd` |
| `evidence.jsonl` | `c967b2c5f81659eab9ca1a0597571fbddeac6e20d7f8d73fcb323fcd1b88b0cd` |
| `run-manifest.jsonl` | `b1b7ed7a21eabadaa354b405e69d29154e606b79697deb6b96d3cb26b7f1d962` |
| `source-inventory.jsonl` | `2d1756e925fb47f809ad50c7d928bbc03788e0da2908b33dfe6bcf36b8c09af9` |
