# Plano congelado da revisão independente de aceleradoras

Issue de revisão: #77. Contrato: #68. Consolidação revisada: #76. Data de
corte: 27 de julho de 2026.

Este plano e o manifesto foram congelados antes da revisão das evidências e
decisões individuais. A revisão não cria perfis nem altera índices publicados.

## Populações obrigatórias

A consolidação contém 78 candidatos canônicos. A revisão cobre:

- 100% dos 25 candidatos marcados como `elegível`;
- 100% dos 16 encaminhamentos, sendo 13 para outra epic e 3 para `funds/`;
- 100% das 30 resoluções entre categorias;
- 100% das 22 resoluções de programas, operadoras e veículos de investimento;
- uma amostra determinística de 4 dos 17 excluídos, equivalente a 23,53%.

As sobreposições entre grupos são preservadas. A união congelada contém 52
candidatos distintos.

## Amostra de exclusões

Para cada candidato excluído, calcula-se:

```text
SHA-256("<candidate_id>|issue-77|2026-07-27")
```

Os 17 resultados são ordenados pelo hash em ordem ascendente. A amostra contém
os quatro primeiros IDs, pois `ceil(17 × 0,20) = 4`:

1. `accel-and-liquid`
2. `accel-dasa-pulsa`
3. `accel-and-impact-hub-caracas`
4. `accel-mxcac-honduras-digital`

## Procedimento

1. Conferir os hashes normalizados em LF dos seis artefatos da consolidação.
2. Para cada item obrigatório, reler candidato, evidência e fonte consolidada.
3. Para elegíveis, exigir fonte oficial para categoria, atividade nos últimos
   24 meses e acesso explícito a startups da América Latina.
4. Para encaminhamentos e híbridos, separar operadora, programa e veículo.
5. Comparar destinos com `funds/` e com os artefatos das epics #63, #64 e #65.
6. Não converter silêncio ou ausência de cadastro em conclusão.
7. Reabrir toda decisão que não tenha evidência suficiente e registrar
   divergência, resolução, responsável e próxima ação.
8. Congelar o relatório final e seus hashes somente após o verificador provar
   cobertura integral dos grupos obrigatórios e da amostra.

## Gates

- 25 de 25 elegíveis revisados;
- 16 de 16 encaminhados revisados;
- 30 de 30 resoluções entre categorias revisadas;
- 22 de 22 resoluções de veículos revisadas;
- pelo menos 4 de 17 excluídos, escolhidos pelo algoritmo congelado;
- 52 candidatos distintos com uma resolução final de revisão;
- nenhuma evidência oficial ausente tratada como confirmada;
- nenhuma duplicação silenciosa com `funds/` ou epics #63, #64 e #65;
- zero perfis criados;
- hashes SHA-256, UTF-8, ausência de mojibake e validação central aprovados.
