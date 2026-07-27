# Auditoria final multilíngue de SEO/GEO

Data de corte: 27 de julho de 2026.

Commit auditado: `fce004897b76d8e28dff9c7879a042970f109032`.

Produção:
[`https://djairofilho.github.io/awesome-latam-vc/`](https://djairofilho.github.io/awesome-latam-vc/).

## Conclusão

O diretório multilíngue está publicado e passou os gates técnicos da epic #107.
Não foram encontradas inconsistências críticas ou altas.

A conexão com Google Search Console e Bing Webmaster Tools foi adiada por
decisão de escopo em 27 de julho de 2026. Essa decisão não equivale a
propriedade verificada nem a sitemap aceito pelos provedores. Os artefatos e o
procedimento para executar essa etapa depois permanecem versionados em
[`../measurement/`](../measurement/).

## Fatos medidos

| Área | Resultado |
|---|---|
| Inventário canônico | 227 perfis |
| Cobertura por idioma | EN 227, PT-BR 227, ES 227 |
| Páginas editoriais | 7 por idioma |
| Validação i18n | Aprovada, zero avisos |
| Testes Python | 55/55 |
| Testes Node | 40/40 |
| Build estático | 771 páginas |
| Pagefind | 681 páginas, 3 idiomas e 12 filtros |
| Acessibilidade estrutural | Aprovada |
| Links externos | 569 únicos, zero quebrados |
| Smoke de produção | 14/14 endpoints HTTP 200 |
| Página 404 personalizada | HTTP 404 |

O auditor de links classificou 558 URLs como acessíveis, 7 como restritas e 4
como não verificadas automaticamente. As quatro não verificadas pertencem ao
FirstAngels Caribbean, ao Banco Central do Uruguai e à CNBV. A revisão
independente confirmou HTTP 200 nos dois reguladores. O domínio do FirstAngels
permaneceu como limitação transitória por responder com Cloudflare 522, embora o
conteúdo oficial continue indexado.

Três referências realmente indisponíveis foram corrigidas antes desta
auditoria: Capital Invent, Primus Ventures e The Ark Fund. Os exports JSON e CSV
foram regenerados depois das correções.

## Lighthouse

Foram auditadas home, país, perfil e catálogo em EN, PT-BR e ES, totalizando 12
rotas.

| Categoria | Meta | Resultado observado |
|---|---:|---:|
| Performance | ≥ 0,90 | 0,98 a 1,00 |
| Acessibilidade | ≥ 0,95 | 1,00 |
| Boas práticas | ≥ 0,95 | 0,96 |
| SEO | ≥ 0,95 | 1,00 |

A primeira execução foi descartada porque um preview antigo ocupava a porta
`4321`. A repetição válida usou o servidor do worktree auditado, produziu 12
relatórios e terminou sem saída de erro.

## Produção

O deploy do GitHub Pages passou no commit auditado. O smoke test confirmou:

- homes, catálogos e perfis nos três idiomas;
- `sitemap.xml` e `robots.txt`;
- exports `entities.json` e `entities.csv`;
- resposta 404 correta para rota inexistente.

Kaszek, metodologia e catálogo em espanhol responderam HTTP 200, com canonical
próprio e sem `noindex`.

## Metas e limitações

As metas Lighthouse são limites de qualidade técnica. Elas não representam
ganho de tráfego, indexação, impressões, cliques ou citações.

Search Console e Bing continuam com o estado
`pending_authenticated_owner`. Os sitemaps não foram submetidos nesses
provedores. Essa etapa pode ser retomada sem alterar o site quando houver
autorização e autenticação do proprietário.

O baseline de descoberta preserva a matriz de 30 consultas e a cadência D30,
D60 e D90. Nenhuma métrica pós-lançamento foi inventada para substituir dados
ainda indisponíveis.

## Comandos reproduzíveis

```powershell
npm ci
npm run verify
npm run audit:lighthouse
npm run audit:external-links
npm run smoke:production
python tools/seo_geo/validate_i18n.py --release-locale es
python tools/seo_geo/validate_editorial.py --release-locale es
python translations/es/validate_quality.py
```

`npm run audit:release` continua rejeitando corretamente o estado atual porque
os dois provedores não estão verificados. Para este encerramento, essa falha é
uma limitação aceita por decisão explícita de escopo, não um resultado aprovado.
