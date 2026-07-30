# Auditoria final dos fundos com acesso ao Brasil

Esta auditoria encerra a epic #207 na data de corte de 2026-07-30. O resultado
representa cobertura auditada nas fontes e no recorte registrados; não prova
totalidade do universo brasileiro.

## Resultado

- 172 fontes em estado terminal: 163 `complete` e 9 `gap_justified`;
- 76 linhas de candidatos e 63 identidades canônicas;
- 27 elegíveis publicados exatamente uma vez em três lotes;
- 27 perfis canônicos e 54 traduções, totalizando 81 arquivos;
- 126 de 126 referências de descoberta provenientes de fontes não-CVM;
- duas consultas CVM entre 63 candidatos canônicos, ou 3,17%;
- 10 de 11 tarefas de pesquisa/adjudicação não-CVM, ou 90,91%;
- 70 revisões resolvidas, sem inconsistência crítica ou alta aberta;
- zero omissão, sobreposição, duplicata publicada ou página órfã.

As duas tarefas `not_applicable` de revisão e freeze ficam fora do denominador
de 11 tarefas de pesquisa/adjudicação. Os rendimentos por família se sobrepõem
e não devem ser somados como universos independentes.

## Curva de descoberta e saturação

A curva inicial de candidatos/elegíveis acumulados foi
`7/1 → 19/5 → 25/8 → 40/9 → 48/11 → 51/14`. A revisão cega acrescentou
25 linhas e 13 elegíveis, encerrando em `76/27`.

Duas passagens finais não produziram candidato, e a última passagem encontrou
quatro candidatos e um elegível. A conclusão correta é rendimento marginal
baixo no recorte auditado, não saturação absoluta.

## Uso da CVM

As 126 referências que originaram os 76 candidatos são não-CVM. A CVM foi
consultada somente para resolver identidade em Vinci Partners e Jatobá Impacto
Amazônia. Os dois logs estão completos, os quatro documentos CVM do inventário
possuem `discovery_allowed: false`, e nenhuma consulta sustentou descoberta ou
elegibilidade.

## Encaminhamentos

Os itens abaixo foram registrados nas epics receptoras para nova validação sob
seus próprios contratos. O encaminhamento não concede elegibilidade automática.

- #62, aceleradoras: IPÊ Investe, StartVC e FOKS;
- #63, redes-anjo: AgroVen, UniAngels, Insper Angels e ITA Angels;
- #64, plataformas: 3C Invest.

## Reprodução

```text
python research/epic-207/brazil/final-audit/build_audit.py --check
python -m unittest discover -s research/epic-207/tests -p "test_*.py"
python research/epic-207/validate.py research/epic-207/brazil
python research/epic-207/brazil/publication/build_report.py --check
python tools/seo_geo/validate_profiles.py --catalog
python tools/seo_geo/validate_i18n.py
python tools/research/generate_indexes.py --check
python tools/seo_geo/generate_entities.py --check
```
