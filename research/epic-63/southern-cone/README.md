# Auditoria de redes-anjo no Cone Sul

Resultado da issue
[#85](https://github.com/djairofilho/awesome-latam-vc/issues/85), conforme o
contrato da epic #63 e com data de corte em 27 de julho de 2026. A auditoria
cobre Argentina, Chile, Paraguai e Uruguai. Nenhum perfil foi criado.

## Resultado

Dezesseis fontes oficiais foram percorridas e 11 candidatos receberam decisão:

| Decisão | Quantidade |
| --- | ---: |
| `elegível` | 2 |
| `evidência-insuficiente` | 5 |
| `duplicado` | 1 |
| `encaminhado-para-plataformas` | 2 |
| `encaminhado-para-programas-públicos` | 1 |

O Business Angels Club EmprendeIAE e a Red Ángeles do Centro de Innovación UC
são elegíveis. As fontes oficiais separam seleção, decisão e capital, confirmam
processo recorrente, abrem candidatura externa e registram atividade em data
civil dentro da janela de 24 meses.

O capítulo Mar del Plata aponta diretamente para o BAC canônico. A organização
o chama de primeiro capítulo regional, mas não publica autonomia própria de
seleção, decisão, capital e atividade; por isso, ele permanece como alias e
duplicado, não como rede independente.

Red Chilena de Inversiones e Red Uruguaya de Inversiones são marketplaces e
seguem para a epic #64. A Red de Inversores APEP tem governança
intergovernamental e seleção executada por instituições públicas; ela segue para
a epic #65. Os diretórios nacionais de ARCAP, ACVC e URUCAP foram usados como
controle da fronteira com `funds/`, sem converter gestores em redes-anjo. Nenhum
candidato desta coleta exigiu encaminhamento à epic #62.

## Cobertura e lacunas

- Argentina: BAC concluído e elegível; Mar del Plata resolvido como alias; o
  Club de Inversores Ángeles CREA ainda precisa de processo decisório e
  atividade datada.
- Chile: Red Ángeles UC concluída e elegível; Austral Angels e ChileGlobal
  Angels têm processo e acesso conhecidos, mas não atividade oficial com data
  civil exata; o marketplace foi encaminhado.
- Paraguai: RIAP tem identidade e sinais atuais confirmados, mas faltam
  regulamento completo, rota externa inequívoca e atividade de investimento com
  data civil exata.
- Uruguai: Piso 40 tem identidade institucional, mas faltam processo, atores,
  acesso e atividade recente datada; APEP e o marketplace foram encaminhados.

Ausência de data precisa foi tratada como evidência insuficiente, não como
inatividade. Cada lacuna preserva responsável e próxima ação para a consolidação
da issue #86.

## Evidências principais

- [Business Angels Club — para fundadores](https://businessangelsclub.org/para-fundadores.html):
  triagem, pitch, decisão individual, veículo único e candidatura latino-americana.
- [Red Ángeles UC — convocatória de 18 de fevereiro de 2026](https://centrodeinnovacion.uc.cl/noticias/red-angeles-del-centro-de-innovacion-uc-abre-convocatoria-para-inversionistas-y-startups/):
  nova chamada para startups e investidores.
- [RIAP — perfil institucional](https://py.linkedin.com/company/redangelpy/):
  identidade e operação atual da rede paraguaia.
- [Uruguay XXI — Red de Inversores APEP](https://www.uruguayxxi.gub.uy/es/eventos/articulo/suma-tu-startup-a-la-red-de-inversores-apep/):
  governança, avaliadores públicos e convocatória.

## Controles de execução

- plano, matriz, inventário e manifest congelados antes da coleta;
- quatro shards nacionais exclusivos e um shard consolidador;
- redução canônica limitada a `southern-cone`, executada duas vezes com hashes
  SHA-256 idênticos;
- 17 URLs oficiais únicas e 16 arquivos `robots.txt` verificados, todos com
  resposta HTTP 200;
- 28 testes do contrato aprovados, incluindo seis testes próprios da issue #85;
- validação contratual e validação central aprovadas;
- varredura UTF-8 sem mojibake;
- zero perfis publicados.

## Artefatos

- `build_audit.py`: materialização e redução determinísticas;
- `source-inventory.jsonl`: fontes e escopo percorrido;
- `candidates.jsonl`: decisões, atores, aliases e destinos;
- `evidence.jsonl`: evidência oficial por afirmação;
- `coverage-matrix.jsonl`: cobertura e lacunas por país;
- `run-manifest.jsonl`: tarefas, ownership e estado final;
- `link-audit.json` e `robots-audit.json`: auditoria HTTP;
- `sha256sums.txt`: hashes dos cinco JSONLs canônicos;
- `shards/`: saídas exclusivas preservadas.

| Artefato | SHA-256 |
| --- | --- |
| `candidates.jsonl` | `73ebe1913f14dffab5f4968922da44721d53d363cf8380cb8cc254174ed483ec` |
| `coverage-matrix.jsonl` | `a000af9852551df88f2699145d5fb23577edaa47ab9dbb7f175f0a01a2e092aa` |
| `evidence.jsonl` | `5d8c3574d8ee3277806b552842cf407f186e1347f79da01a0a796bc558e7a2bb` |
| `run-manifest.jsonl` | `abd061dea7770dae19a5da722d79dd77774aff2016eff89e19e230a9fdd9b458` |
| `source-inventory.jsonl` | `f3b393b8e3b7c2cb1b4e6ccc92f7159bdd2669cbbeb6c17db11fa1d0040b4454` |
