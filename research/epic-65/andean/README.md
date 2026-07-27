# Auditoria de programas públicos nos países andinos

Este diretório executa a
[#100](https://github.com/djairofilho/awesome-latam-vc/issues/100) sob o
contrato da [epic 65](../README.md). A data de corte é 2026-07-27.

## Plano congelado antes da coleta

O inventário cobre Bolívia, Colômbia, Equador, Peru e Venezuela. Para cada país,
foram declaradas cinco frentes independentes antes de qualquer coleta:

1. agência de inovação;
2. ministério responsável;
3. banco público de desenvolvimento;
4. portal oficial de chamadas;
5. fonte subnacional oficial.

Os 25 pares país × tipo de fonte têm `task_id`, `worker_id` e `shard_path`
exclusivos no manifesto. A matriz registra o ponto de entrada oficial, o escopo
planejado e a pendência inicial de cada frente.

O seed BDP Fondo Startup será revalidado sem presumir elegibilidade. A coleta
separará agência, programa e chamada; exigirá evidência oficial tanto do
benefício financeiro direto quanto da rota geográfica; e não publicará perfis.

## Resultado

A auditoria consolidou 8 agências, 8 programas, 4 chamadas temporárias e 21
evidências oficiais. Quatro rotas atendem ao contrato:

- Bolívia: BDP Fondo Startup, com capital de risco para startups bolivianas
  inovadoras ligadas a exportações ou substituição de importações;
- Colômbia: Fondo Emprender do SENA, com capital semente condonável para criação
  de empresas por meio de chamadas recorrentes;
- Equador: FonQuito, com capital semente recorrente para empreendimentos
  dinâmicos domiciliados no Distrito Metropolitano de Quito;
- Peru: StartUp Perú, com cofinanciamento de capital semente para startups
  inovadoras e de alto impacto.

As chamadas foram avaliadas separadamente. As inscrições de Fondo Emprender
2026, FonQuito 2026, StartUp Perú 13G e Medellín Next 2026 estavam encerradas na
data de corte. FonQuito seguia em avaliação e seleção, sem reabrir a candidatura.
Nenhuma chamada recebe perfil.

Bancóldex Impacto Inclusivo foi excluído por não criar rota específica para
startups. Medellín Next foi excluído por não comprovar benefício financeiro
direto. O antigo Fondo de Capital de Riesgo - Semilla Innovación do Equador foi
classificado como inativo porque sua execução terminou em janeiro de 2022. O
Financiamiento LOCTI do FONACIT ficou com evidência insuficiente: há finalidade
financeira, mas não chamada, fluxo de submissão nem recorte startup publicados.

## Cobertura e lacunas

Dos 25 pares país × tipo de fonte, 13 foram concluídos, 8 ficaram parciais e 4
indisponíveis. As lacunas têm responsável e próxima ação na matriz:

- Bolívia: agência, ministério, portal de chamadas e fonte municipal não
  comprovaram rota financeira específica além do BDP;
- Colômbia: as cinco frentes foram concluídas, com uma rota nacional elegível e
  negativas explícitas para os candidatos materiais restantes;
- Equador: faltam confirmação atual da CFN e uma chamada nacional material; o
  fundo ministerial histórico está inativo e FonQuito cobre apenas Quito;
- Peru: faltou comprovar uma rota direta da COFIDE; as demais frentes foram
  concluídas e a operação nacional ficou consolidada no ProInnóvate;
- Venezuela: somente o FONACIT respondeu, ainda sem especificidade suficiente.
  Mincyt, BANDES, rota de chamadas e portal de Miranda ficaram indisponíveis.

Essas lacunas não provam inexistência de iniciativas fora dos portais
inventariados. Elas delimitam o que as fontes oficiais permitiram afirmar em
2026-07-27.

## Consolidação e qualidade

Cada worker gravou somente em `shards/<worker-id>/records.jsonl`, inclusive
quando sua frente terminou sem candidato material. O
[`consolidate.py`](consolidate.py) percorre os 25 shards em ordem
lexicográfica, rejeita IDs duplicados, separa os tipos e ordena cada arquivo
canônico pelo ID. Reexecutá-lo produz os mesmos quatro arquivos consolidados.

O [`link_audit.py`](link_audit.py) verifica HTTPS, domínios oficiais e,
opcionalmente, respostas HTTP. Matriz e manifesto completam os seis artefatos
do bundle. Todos os registros permanecem com `canonical_profile: null`; nenhum
perfil foi publicado.
