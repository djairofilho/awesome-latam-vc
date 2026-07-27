# Baseline de descoberta SEO/GEO

Este bundle registra o estado anterior ao site da epic #107. A data de corte é
**2026-07-27**. Ele separa três conceitos que não podem ser usados como
sinônimos:

1. **Baseline**: observação datada do estado atual.
2. **Meta interna**: condição técnica que o projeto pretende satisfazer.
3. **Resultado real**: dado externo observado depois da publicação.

Uma meta de cobertura, uma nota de prontidão ou um teste aprovado não representa
tráfego, posição ou probabilidade de citação.

## Estado inicial

Na data de corte, o repositório era público e sua superfície encontrável era o
próprio GitHub, com READMEs em inglês, português e espanhol. Não havia:

- homepage configurada no repositório;
- site no GitHub Pages;
- `package.json` ou configuração do Astro;
- workflow de publicação no GitHub Pages.

A consulta à API do GitHub Pages retornou HTTP 404. O snapshot completo e o
commit observado estão em `repository-state.json`.

## Matriz de consultas

`queries.jsonl` contém 30 consultas fixas:

| Idioma | Consultas |
| --- | ---: |
| Inglês | 10 |
| Português do Brasil | 10 |
| Espanhol | 10 |

A matriz cobre descoberta ampla, país, estágio, setor, tipo de organização e
nome do projeto. Cada linha registra:

- texto e idioma;
- intenção e dimensões aplicáveis;
- mecanismo e provedor;
- localização, quando disponível;
- data;
- estado do resultado;
- URL observada;
- limitações.

Nenhuma URL do projeto apareceu na amostra retornada. Isso não prova ausência
total do índice: o mecanismo retorna uma amostra variável, sem posição
controlada ou localização exposta.

## Método de repetição

Para uma nova medição:

1. copie a matriz sem alterar consultas, locales ou intenções;
2. execute todas as linhas no mecanismo declarado;
3. registre provedor, localização efetiva quando disponível e data UTC;
4. registre se uma URL canônica do projeto apareceu;
5. quando houver resultados sem o projeto, guarde uma URL representativa;
6. acrescente uma execução versionada, preservando o baseline;
7. execute o validador.

```text
python research/seo-geo/baseline/validate.py
python -m unittest discover -s research/seo-geo/baseline/tests -p "test_*.py"
```

O manifesto também contém essas instruções em formato legível por máquina.

## KPIs

`kpis.jsonl` define a fonte, frequência e unidade de cada indicador.

### Indicadores técnicos

- URLs válidas;
- páginas indexáveis;
- cobertura do sitemap;
- cobertura de canonicals;
- completude de traduções;
- cobertura de dados estruturados.

Esses indicadores medem a implementação publicada. No baseline, contagens do
site são zero ou não aplicáveis porque o site ainda não existe.

### Indicadores observados

- páginas indexadas;
- consultas distintas;
- impressões;
- cliques;
- presença em respostas generativas;
- citações de URLs canônicas em respostas generativas.

Search Console e Bing Webmaster Tools ainda não estavam conectados. Portanto,
os indicadores externos são `null`, não zero. Presença e citação generativas
devem ser registradas como amostras não determinísticas, sempre com mecanismo,
idioma, localização e data.

## Limitações

- O resultado retornado não representa o índice completo.
- Ausência em uma consulta não prova ausência total do índice.
- Ordem e disponibilidade variam por provedor, data, idioma, conta e local.
- A localização não estava disponível no mecanismo desta execução.
- Esta rodada mediu busca web, não respostas generativas.
- Nenhuma meta interna é previsão de tráfego, ranking ou citação.
