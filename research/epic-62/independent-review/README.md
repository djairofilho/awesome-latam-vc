# Revisão independente da consolidação de aceleradoras

Esta pasta registra a execução da issue #77 sobre a consolidação da issue #76, conforme o contrato de elegibilidade da issue #68. A revisão foi feita sem criar perfis e com corte em **27 de julho de 2026**.

## Resultado

- 52 candidatos únicos revisados;
- 25 de 25 decisões elegíveis revisadas;
- 16 de 16 encaminhamentos revisados;
- 30 de 30 casos com fronteira de categoria revisados;
- 22 de 22 casos com programa e veículo financeiro revisados;
- 4 de 17 exclusões revisadas por amostra determinística, equivalentes a 23,53%;
- 48 decisões confirmadas sem ressalva;
- 1 decisão confirmada com evidência oficial adicional;
- 2 decisões confirmadas com resolução de fronteira;
- 1 decisão reaberta e alterada;
- 3 divergências registradas e resolvidas;
- 26 candidatos no manifesto final publicável;
- 0 perfis criados.

Cada caso obrigatório foi confrontado com evidência oficial de categoria, atividade e acesso externo compatível com a América Latina. Também foram verificadas as relações com `funds/` e com as epics #63, #64 e #65.

## Divergências resolvidas

### Ventiur Acelera Impacto

A consolidação classificava o candidato como `evidência-insuficiente` por suposta ausência de data. A página oficial publica o edital em 6 de março de 2025, inscrições de 6 a 27 de março e atividades entre abril e outubro de 2025. A decisão foi reaberta para `elegível`.

### Founder Institute

A elegibilidade do programa foi mantida. A revisão identificou, porém, o Founder Capital como veículo financeiro separado na fonte oficial. Foi criado o encaminhamento de backlog `funds/:fi.co#founder-capital`, sem duplicar o programa como fundo.

### Honduras Digital Challenge

A epic #63 encaminha o Startup Challenge para análise de aceleradoras, enquanto a consolidação da epic #62 o exclui. A exclusão foi mantida porque a fonte descreve um desafio por edição, e o contrato #68 exclui desafios pontuais. O registro da epic #63 foi tratado como descoberta de fronteira, não como decisão de elegibilidade.

## Evidência adicional

A página principal do InovAtiva Brasil estava em manutenção durante a revisão. A decisão foi sustentada por FAQ oficial do MDIC, atualizado em 17 de dezembro de 2024, que confirma ciclos recorrentes em fevereiro e julho e acesso nacional para startups.

## Amostra de exclusões

A população tinha 17 decisões `excluído`. O tamanho mínimo foi calculado com `ceil(17 × 0,20) = 4`. A seleção ordena de forma crescente:

```text
sha256(candidate_id + "|issue-77|2026-07-27")
```

Os quatro casos selecionados e seus hashes estão congelados em `review-manifest.json`. O verificador recalcula a amostra a partir da consolidação e falha se a população ou a seleção forem alteradas.

## Artefatos

- `review-manifest.json`: universo congelado, amostra, hashes de entrada e saída e contagens finais;
- `review-results.json`: resultado individual dos 52 casos e referências de evidência;
- `review-evidence.json`: evidências oficiais adicionadas pela revisão;
- `divergences.json`: divergências, severidade e resolução;
- `cross-catalog-checks.json`: comparação com `funds/` e epics #63, #64 e #65;
- `publishable-manifest.json`: conjunto final congelado de 26 IDs elegíveis;
- `verify_review.py`: verificador reproduzível de cobertura e invariantes;
- `tests/test_review.py`: testes positivos e testes de adulteração.

## Reprodução

Na raiz do repositório:

```bash
python research/epic-62/independent-review/build_review.py
python research/epic-62/independent-review/verify_review.py
python -m unittest discover -s research/epic-62/independent-review/tests -v
```

O primeiro comando reconstrói os artefatos a partir do manifesto congelado. O segundo confirma cobertura integral dos grupos obrigatórios, amostra mínima, evidência oficial para cada decisão elegível, resolução de divergências, comparação entre catálogos e integridade dos hashes.
