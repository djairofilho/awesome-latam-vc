# Auditoria de fundos da Colômbia

Este diretório registra a execução das issues #264 a #268 da epic #250, com
data de corte em 2026-07-30. A cobertura é auditada sobre as fontes
explicitamente percorridas e não representa uma afirmação de totalidade absoluta
do mercado colombiano.

## Resultado congelado

- 13 candidatos canônicos avaliados;
- 2 elegíveis: Marathon Ventures e Simma Capital;
- 5 com evidência insuficiente;
- 3 encaminhados para outro tipo de entidade;
- 3 duplicatas do catálogo;
- 100% das origens de descoberta não regulatórias;
- 1 consulta regulatória pontual, equivalente a 7,7% dos candidatos, usada
  apenas para resolver a identidade do H20 Capital Innovation.

Entrypoint e Flourish Ventures foram deduplicados contra os perfis incorporados
ao baseline pelo commit `5b3a4e0`. O arquivo local de startups não foi usado
para descoberta, priorização, comprovação ou decisão.

## Reproduzir

```powershell
python research/epic-250/colombia/build.py
python -m unittest research.epic-250.tests.test_colombia_audit
python tools/seo_geo/validate_profiles.py --catalog
python tools/seo_geo/generate_entities.py --check
```

O gerador produz baseline e delta histórico com SHA-256, inventário de fontes,
candidatos, evidências, curva de rendimento marginal, revisão cega, manifesto
de congelamento, lote de publicação e auditoria final.
