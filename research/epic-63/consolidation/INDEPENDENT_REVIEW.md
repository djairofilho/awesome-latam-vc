# Revisão independente da fila de redes-anjo

## Autoria e escopo

- Revisor: `independent-reviewer-issue-86`.
- Consolidador: `consolidator-issue-86`.
- Data: 2026-07-27.
- Registros revisados: 42.
- Divergências críticas ou altas pendentes: 0.

O revisor leu a fila consolidada e as evidências já coletadas. Não executou
scraping novo e não criou perfis.

## Cobertura

- 100% dos 12 elegíveis;
- 100% dos 12 encaminhados;
- 100% dos casos com evidência insuficiente, duplicados e híbridos;
- amostra determinística de 1 entre
  3 decisões restantes.

A amostra usa `sha256(network_id), ordem crescente, ceil(20%)`. Registro selecionado: `ang-venecapital-org`.

## Resultado

As 42 decisões revisadas foram confirmadas. Todos os elegíveis mantêm
evidência oficial de categoria, atividade e acesso externo. As duas
duplicidades apontam diretamente para destino canônico. As 12 transferências
possuem categoria, ID-alvo e caminho de destino. Os casos híbridos preservam
rede, operador e veículo como unidades separadas quando a evidência permite.

### Decisões revisadas

- `duplicado`: 2
- `elegível`: 12
- `encaminhado-para-aceleradoras`: 2
- `encaminhado-para-funds`: 4
- `encaminhado-para-plataformas`: 5
- `encaminhado-para-programas-públicos`: 1
- `evidência-insuficiente`: 15
- `excluído`: 1

### Grupos de revisão

- `boundary`: 16
- `deterministic-sample`: 1
- `eligible`: 11
- `hybrid`: 2
- `transfer`: 12
