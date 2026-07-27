# Auditoria de geografia dos perfis preexistentes

Auditoria executada em 2026-07-27 para a issue #59, conforme a regra de
localização definida em `contributing.md`:

- usar a pasta do país quando o investidor é sediado na América Latina e não
  possui mandato regional explícito;
- usar `funds/regional/` quando o investidor é sediado na América Latina e
  investe explicitamente em vários mercados da região;
- usar `funds/multi-country/` quando a sede principal está fora da América
  Latina e existe presença de investimento regional.

## Decisões

| Investidor | Base reconfirmada | Mandato reconfirmado | Decisão | Evidência principal |
| --- | --- | --- | --- | --- |
| Alaya Capital | Argentina | América Latina | mover para `regional/` | [Site oficial](https://alaya-capital.com/) |
| Canary | Brasil | América Latina | mover para `regional/` | [Site oficial](https://www.canary.com.br/) |
| DGF Investimentos | Brasil | Brasil e América Latina | mover para `regional/` | [Site oficial](https://www.dgf.com.br/) |
| Indicator Capital | Brasil | América Latina | mover para `regional/` | [Tese oficial](https://indicator.capital/thesis) |
| Itaú Ventures | Brasil | Brasil e América Latina | mover para `regional/` | [Página oficial](https://www.itau.com.br/ventures) |
| Monashees | Brasil | América Latina com expansão global | mover para `regional/` | [Site oficial](https://www.monashees.com/) |
| Spectra Investimentos | Brasil | Brasil e América Latina | mover para `regional/` | [Site oficial](https://spectrainvest.com/) |
| Fen Ventures | Chile | América Latina de língua espanhola | mover para `regional/` | [Site oficial](https://fenventures.com/) |
| Genesis Ventures | Chile | Chile e América Latina | mover para `regional/` | [Site oficial](https://genesisventures.vc/) |
| Manutara Ventures | Chile | Chile e América Latina | mover para `regional/` | [Site oficial](https://manutaraventures.com/) |
| Ventures EPM | Colômbia | Colômbia e América Latina | mover para `regional/` | [Programa oficial](https://www.epm.com.co/institucional/innovacion/programa-ventures-epm/) |
| Velum Ventures | Colômbia | Colômbia e América Latina | mover para `regional/` | [Página institucional](https://www.linkedin.com/company/velum-ventures/) |
| Veronorte | Colômbia | América Latina | mover para `regional/` | [Site oficial](https://veronorte.com/) |
| Dux Capital | Estados Unidos, com escritório no México | Estados Unidos e mercados transfronteiriços | mover para `multi-country/` | [Site e escritórios oficiais](https://duxcapital.vc/) |
| AVP Ventures | Peru | Peru e América Latina | mover para `regional/` | [Site oficial](https://avpventures.com/) |
| EMA Ventures | Peru | América Latina de língua espanhola | mover para `regional/` | [Tese oficial](https://ema.ventures/) |
| UTEC Ventures | Peru | Peru e América Latina | mover para `regional/` | [Site oficial](https://utecventures.com/) |
| Winnipeg Capital | Peru | América Latina | mover para `regional/` | [Site oficial](https://www.winnipegcapital.com/) |
| Grupo Boticário Ventures | Brasil | Brasil e oportunidades globais, sem mandato regional explícito | mover para `brazil/` | [Página oficial](https://ventures.grupoboticario.com.br/) |
| Carao Ventures | Costa Rica | América Central e América Latina | mover para `regional/` | [Site oficial](https://www.caraov.com/) |
| Krealo | Peru | América Latina | mover para `regional/` | [Site oficial](https://www.krealo.pe/) |
| New Ventures Capital | México | América Latina | mover para `regional/` | [Site oficial](https://nvcapital.vc/) |
| Valor Capital Group | Estados Unidos, com escritório no Brasil | Estados Unidos, Brasil e América Latina | manter em `multi-country/` | [Escritórios oficiais](https://www.valorcapitalgroup.com/contact) |

## Resultado

- 20 perfis foram movidos para `funds/regional/`.
- Grupo Boticário Ventures foi movido para `funds/brazil/`.
- Dux Capital foi movido para `funds/multi-country/`.
- Valor Capital Group permaneceu em `funds/multi-country/`.
- Os três índices continuam com 152 entradas equivalentes e ordenadas.
- Os perfis movidos receberam os campos obrigatórios que faltavam no padrão
  atual.

A revalidação corrigiu a hipótese inicial sobre Dux Capital: a sede principal
oficial é Austin, com escritório adicional na Cidade do México. Por isso, a
classificação correta é `multi-country/`, não `regional/`.

## Links

Foram verificadas 81 URLs únicas nos 23 perfis:

- 73 responderam com sucesso na primeira execução concorrente;
- 3 URLs da AVP Ventures responderam HTTP 200 na repetição individual;
- 4 URLs responderam 403 por proteção ou WAF, sem evidência de link quebrado;
- 1 arquivo da Credicorp manteve timeout e foi removido do perfil de Krealo,
  que permanece sustentado por duas páginas oficiais ativas.

## Validação

```powershell
python tools/research/validate.py --base-ref origin/main
python tools/research/generate_indexes.py --check
python -m unittest discover -s tools/research/tests -v
git diff --check origin/main...HEAD
```

Também foram conferidos UTF-8, mojibake, contagem de páginas, equivalência dos
três índices, existência de todos os caminhos e ausência de duplicidades.
