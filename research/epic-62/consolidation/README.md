# Registro provisório consolidado de aceleradoras

Este bundle materializa a issue #76 na data de corte 2026-07-27. Ele não
publica perfis.

## Resultado

- Ocorrências de entrada: 80.
- Candidatos canônicos: 78.
- Ocorrências duplicadas fundidas: 2.
- Decisões: {"elegível": 25, "encaminhado-para-funds": 3, "encaminhado-para-outra-epic": 13, "evidência-insuficiente": 19, "excluído": 17, "inativo": 1}.
- Resoluções entre categorias: 30.
- Veículos separados de seus programas: 22.
- Encaminhamentos em fila canônica com responsável e próxima ação:
  12.

As duas duplicatas eram `accel-oxigenio` e `accel-kruger-labs`, coletadas no
piloto e revalidadas regionalmente. A versão regional prevalece, e as listas de
fontes e evidências das duas ocorrências são preservadas.

## Conflitos resolvidos

- Google for Startups Accelerator: Brazil passou de encaminhamento interno
  para `elegível`, apoiado pela evidência oficial completa da auditoria
  brasileira.
- Rockstart LATAM e SparkLabs Mexico passaram de encaminhamentos internos sem
  destino para `evidência-insuficiente`, cada um com responsável e próxima
  ação.
- Os 13 programas públicos receberam IDs ou caminhos canônicos da epic #65.
- Os três encaminhamentos para fundos receberam caminho publicado ou namespace
  canônico de backlog.
- Programas híbridos e seus veículos permanecem unidades distintas; o mesmo
  capital não é contado como prova de duas categorias.

## Lacunas acionáveis

Os 19 registros com `evidência-insuficiente` têm `owner` e `next_action`. Os
encaminhamentos ainda não materializados fora desta epic também têm responsável
e próxima ação. Uma fila canônica não significa que o perfil de destino já foi
publicado.

## Artefatos

- `candidates.jsonl`: registro canônico completo e compatível com o contrato.
- `evidence.jsonl` e `source-inventory.jsonl`: proveniência combinada.
- `registry-index.json`: execução escolhida, ocorrências e mudança de decisão.
- `category-resolutions.json`: encaminhamentos, híbridos e veículos.
- `consolidation-manifest.json`: contagens e hashes das entradas e saídas.

## Reprodução

```text
python research/epic-62/consolidation/build_registry.py
python research/epic-62/consolidation/build_registry.py --check
python -m unittest discover -s research/epic-62/consolidation/tests -p "test_*.py"
python tools/research/validate.py --base-ref origin/main
```
