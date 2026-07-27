# Revisão independente da fila de redes-anjo

## Autoria e escopo

- Revisor: `independent-reviewer-final-issue-86`.
- Consolidador: `consolidator-issue-86`.
- Data: 2026-07-27.
- Registros revisados: 42.
- Divergências altas encontradas: 1, resolvida.
- Divergências altas pendentes: 0.

O revisor conferiu os artefatos consolidados, as evidências oficiais e os
contratos das epics relacionadas. Não criou perfis.

## Cobertura

- 100% dos 12 originalmente elegíveis;
- 100% dos 12 encaminhados;
- 100% dos casos com evidência insuficiente, duplicados e híbridos;
- amostra determinística de 1 entre
  3 decisões restantes.

A amostra usa `sha256(network_id), ordem crescente, ceil(20%)`. Registro selecionado: `ang-venecapital-org`.

## Divergências e resolução

O PAD/UDEP foi alterado de `elegível` para `evidência-insuficiente`. A fonte
oficial confirma a rede, seleção e atividade recente, mas a rota registrada
recebe inscrições de participantes em um seminário e em seu fórum exclusivo.
Ela não comprova acesso externo de startups à seleção recorrente da rede.

O Honduras Digital Challenge continua transferido como fronteira de categoria.
A epic 62 o exclui como desafio pontual; a transferência preserva a
proveniência e não equivale a aceitação no destino.

## Resultado congelado

A fila final contém 11 redes elegíveis. Todas satisfazem categoria, atividade,
recorrência, acesso externo, atores e rota com evidência oficial. As duas
duplicidades e as sete resoluções de identidade têm destino explícito. As 12
transferências têm categoria, ID-alvo e destino; nenhuma fica órfã.

### Decisões revisadas

- `duplicado`: 2
- `elegível`: 11
- `encaminhado-para-aceleradoras`: 2
- `encaminhado-para-funds`: 4
- `encaminhado-para-plataformas`: 5
- `encaminhado-para-programas-públicos`: 1
- `evidência-insuficiente`: 16
- `excluído`: 1

### Grupos de revisão

- `boundary`: 16
- `deterministic-sample`: 1
- `eligible`: 11
- `hybrid`: 2
- `transfer`: 12
