# Freeze canônico dos fundos brasileiros

Este diretório é a saída determinística congelada pela issue #222. O builder
parte, em memória, da revisão independente da issue #221, reconcilia os estados
terminais e produz o manifesto imutável que delimita a publicação.

## Geração e validação

```powershell
python research/epic-207/brazil/build_frozen.py
python research/epic-207/brazil/build_frozen.py --check
python research/epic-207/validate.py research/epic-207/brazil
python -m unittest discover -s research/epic-207/tests -v
```

Os sete JSONL centrais são ordenados deterministicamente e recebem hashes
SHA-256 no manifesto de execução e em `freeze-manifest.json`. O relatório de
auditoria registra `status: frozen`, enquanto o manifesto fixa a lista dos 27
elegíveis, seus destinos planejados e os lotes de publicação.

## Resultado

O bundle final contém 76 linhas de candidato e 63 identidades canônicas:

| Decisão | Total |
| --- | ---: |
| `eligible` | 27 |
| `duplicate` | 13 |
| `routed_accelerators` | 3 |
| `routed_angel_networks` | 4 |
| `routed_funding_platforms` | 1 |
| `insufficient_evidence` | 28 |

A amostra de revisão cobre todos os 27 elegíveis, todos os oito roteados, os
dois candidatos consultados na CVM, seis insuficientes escolhidos pelos
menores hashes SHA-256 e os achados das buscas cegas e passagens finais.

As 172 fontes possuem estado terminal: 163 estão `complete` e nove bloqueios ou
enumerações incompletas estão `gap_justified`, com motivo, responsável e
próxima ação preservados. Todos os 76 candidatos possuem decisão. As 48
resoluções de identidade estão encerradas, sem cluster ou duplicata sem destino.

## Manifesto de publicação

Os 27 elegíveis foram distribuídos deterministicamente em três lotes de nove,
abaixo do limite de dez perfis por lote. Cada candidato aparece exatamente uma
vez e possui um destino único em `funds/brazil/` ou `funds/multi-country/`.

O freeze não publica perfis, índices, traduções ou exports. Esses arquivos só
podem ser criados a partir de `freeze-manifest.json` na issue #223.

## CVM e origem

A CVM permanece restrita às duas consultas herdadas sobre Vinci e Jatobá.
Nenhuma nova descoberta usa CVM ou baseline como origem. As consultas não
comprovam tese, recorrência, atividade, acesso ao Brasil ou elegibilidade.

## Correções antes do congelamento

- Vinci Partners não agrega duas gestoras distintas como aliases e não recebe
  um `manager_id` genérico.
- DNA Capital, Jatobá Gestora e Mundi Ventures mantêm nomes de veículos somente
  em `vehicle_ids`.
- Quatro evidências sem `observed_on` tiveram o claim de atividade rebaixado
  para `inconclusive`.
- A evidência da AgroVen passa a refletir que os aportes são realizados pelos
  membros do clube.

O relatório auxiliar também explicita os 17 casos originais com uma única
fonte, a sobreposição entre famílias de descoberta, a curva cumulativa e as
passagens finais de saturação.
