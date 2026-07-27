# Medição pós-lançamento de SEO e GEO

Este diretório define como verificar a propriedade pública, submeter o sitemap
e acompanhar resultados sem adicionar analytics, pixels, cookies ou qualquer
identificador de visitante ao site.

O estado anterior ao lançamento permanece imutável em
[`../baseline/`](../baseline/). Cada medição posterior deve ser salva em um
novo diretório `runs/YYYY-MM-DD-dNN/`, onde `NN` é `30`, `60` ou `90`. Nunca
sobrescreva uma execução anterior.

## Estado público confirmado

- Propriedade de prefixo de URL: `https://djairofilho.github.io/awesome-latam-vc/`
- Sitemap: `https://djairofilho.github.io/awesome-latam-vc/sitemap.xml`
- `robots.txt`: `https://djairofilho.github.io/awesome-latam-vc/robots.txt`
- Em 2026-07-27, os três endereços responderam HTTP `200`.
- Não havia conector específico do Google Search Console nem do Bing Webmaster
  Tools disponível nesta execução.
- Uma sessão Google estava autenticada, mas o Search Console exibia somente a
  criação inicial de propriedade. Nenhuma propriedade foi adicionada porque a
  conta proprietária precisa ser confirmada pelo responsável.
- O Bing Webmaster Tools exibia **Sign In**, sem sessão autenticada.
- Nenhuma credencial, propriedade ou submissão foi presumida.

O estado detalhado e os próximos passos ficam em
[`provider-status.json`](provider-status.json).

## Verificação de propriedade

As duas verificações usam metatags na página inicial pública:

- Google: variável pública do repositório `GOOGLE_SITE_VERIFICATION`;
- Bing: variável pública do repositório `BING_SITE_VERIFICATION`.

O workflow de Pages repassa essas variáveis como
`PUBLIC_GOOGLE_SITE_VERIFICATION` e `PUBLIC_BING_SITE_VERIFICATION`. Se uma
variável estiver vazia, nenhuma tag é publicada. Os valores devem ser copiados
exatamente da conta autenticada do respectivo provedor. Não use placeholders.

Procedimento do responsável:

1. Entre na conta que deve ser proprietária.
2. Adicione a propriedade de prefixo de URL acima.
3. Escolha a verificação por tag HTML e copie somente o valor de `content`.
4. Crie ou atualize a variável pública correspondente em
   **Settings → Secrets and variables → Actions → Variables**.
5. Execute novamente o workflow `Deploy static site to GitHub Pages`.
6. Abra o código-fonte da página inicial e confirme a tag esperada.
7. Volte ao provedor e conclua **Verificar**.
8. Registre data UTC, conta responsável sem e-mail pessoal, método e evidência
   em uma cópia de [`run-template.json`](run-template.json).

Esses valores aparecem publicamente no HTML por definição. Eles não são
segredos de API e não concedem acesso à conta. Tokens OAuth, chaves de API,
cookies de sessão, e-mails e outros dados pessoais não devem ser salvos no
repositório.

Documentação oficial:

- [Verificação por tag HTML no Google Search Console](https://support.google.com/webmasters/answer/9008080?hl=pt-BR)
- [Bing Webmaster Tools](https://www.bing.com/webmasters/about)

## Submissão do sitemap

Após a propriedade estar verificada:

1. No Google Search Console, abra **Sitemaps**, informe `sitemap.xml` e envie.
   Alternativamente, a API aceita a URL completa, mas exige OAuth com o escopo
   `webmasters`.
2. No Bing Webmaster Tools, abra **Sitemaps**, envie a URL completa e aguarde o
   estado aceito/processado.
3. Registre o estado retornado, a data UTC e uma referência de evidência. Não
   registre tokens ou conteúdo de sessão.
4. Consulte novamente após o processamento. “Enviado” não equivale a
   “processado” nem a “indexado”.

Não existe submissão anônima confiável para substituir essas etapas. A API do
Google exige autorização e a API do Bing exige uma conta/chave autorizada:

- [API de submissão de sitemap do Google](https://developers.google.com/webmaster-tools/v1/sitemaps/submit)
- [API do Bing Webmaster](https://learn.microsoft.com/en-us/bingwebmaster/)

## Execução aos 30, 60 e 90 dias

Defina `launch_date` como a data UTC da primeira implantação pública estável.
As datas dos três checkpoints são calculadas a partir dela, conforme
[`cadence.json`](cadence.json).

Para cada checkpoint:

1. Copie `run-template.json` para `runs/YYYY-MM-DD-dNN/run.json`.
2. Preencha o intervalo medido e os estados de verificação e sitemap.
3. Exporte, para cada provedor, páginas indexadas, consultas, impressões,
   cliques, países e dispositivos. Preserve o arquivo bruto fora do Git se ele
   contiver dados pessoais; registre apenas uma referência agregada.
4. Repita as 30 consultas de `../baseline/queries.jsonl` sem alterar texto,
   idioma ou intenção. Salve as observações em `query-results.jsonl` usando
   `../baseline/measurement.schema.json`; atualize mecanismo, provedor,
   localização, data, resultado e limitações reais.
5. Registre amostras de respostas generativas em `generative-samples.jsonl`,
   sempre com data, idioma, mecanismo, localização disponível, presença,
   citação observada e limitações. Uma ausência amostrada não prova ausência
   geral.
6. Execute:

   ```powershell
   python research/seo-geo/measurement/validate.py
   python research/seo-geo/baseline/validate.py
   npm run verify
   ```

## Leitura responsável

Resultados técnicos internos e resultados externos observados são categorias
distintas. Páginas válidas, sitemap disponível ou metadados corretos não
garantem indexação, ranking, tráfego nem citação. As amostras de busca e de
respostas generativas variam por data, idioma, localidade, conta e provedor.
