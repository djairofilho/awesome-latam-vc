# Auditoria de plataformas na região Andina

Esta pasta contém a execução da issue
[#92](https://github.com/djairofilho/awesome-latam-vc/issues/92), com data de
corte em 27 de julho de 2026. A coleta seguiu o contrato da issue #89 e não
criou perfis nem alterou índices de publicação.

## Resultado

Foram inventariadas 37 fontes em 21 shards exclusivos: vinte workers das
células país por categoria e um coordenador. O manifesto encerra nove tarefas
como concluídas e onze como bloqueadas. Fontes alternativas oficiais ou
institucionais fecharam seis células cujas fontes iniciais falharam.

| Decisão | Quantidade |
| --- | ---: |
| `eligible` | 1 |
| `inactive` | 1 |
| `insufficient_evidence` | 8 |
| `excluded` | 1 |
| `other_category` | 2 |

A a2censo possui operadora, rota de captação para empresa colombiana em
crescimento, atividade atual e situação regulatória documentadas por BVC e
SFC. Prospera possui rota para empreendedores, mas a fonte oficial não permite
confirmar a operadora legal e a situação regulatória individual.

Mesfix, Terrenta, Inversiones.io, Prestópolis, Securite e Prestamype mantêm
rotas empresariais, porém não publicam todos os elementos necessários para
confirmar uma rota atual e inequívoca para startups. HazVaca permanece sem
fonte oficial vigente. Bloom está inativa para esta auditoria após a tomada de
posse determinada pela SFC.

Fondea foi excluída porque sua modalidade principal é doação e recompensa.
Sambil Emprende e Pitch Day foram encaminhados, respectivamente, às trilhas de
programas e aceleradoras, sem serem convertidos em plataformas.

## Cobertura

Cada país possui quatro células: regulador, dívida ou recebíveis, plataforma
oficial e descoberta de crowdfunding ou equity.

| País | Completas | Lacunas justificadas |
| --- | ---: | ---: |
| Bolívia | 3 | 1 |
| Colômbia | 4 | 0 |
| Equador | 3 | 1 |
| Peru | 4 | 0 |
| Venezuela | 1 | 3 |
| **Total** | **15** | **5** |

Uma lacuna indica somente que nenhuma fonte vigente e verificável da categoria
foi localizada após a trilha planejada e suas alternativas. Ela não afirma
inexistência de plataformas no país.

## Artefatos congelados

| Arquivo | SHA-256 |
| --- | --- |
| `candidates.jsonl` | `d0dd0f7c5de8f115ffd149007c330d8b974f00a68aa16a30ac518a4068a0e964` |
| `coverage-matrix.jsonl` | `7aa66ecb1de36a984548d06a47a55dba79972c7e0d136e17e4f2186701a5c6cd` |
| `evidence.jsonl` | `7a45c98a973aec6bdc06108ac52af257ea31f3fad7ef243c39d25f27b56a3e9e` |
| `source-inventory.jsonl` | `9f8196cc16d8525206e101a74485a2371036f93390fca696ed16f2d3e4223f70` |

Os hashes usam conteúdo UTF-8 com finais de linha normalizados em LF. O
`run-manifest.jsonl` fica fora do conjunto para evitar referência circular.
