---
{
  "schema_version": "1.0",
  "id": "editorial:methodology:pt-BR",
  "slug": "methodology",
  "locale": "pt-BR",
  "translation_of": "editorial:methodology:en",
  "translation_status": "complete",
  "title": "Metodologia",
  "summary": "Como o Awesome LatAm VC transforma perfis Markdown baseados em fontes em um diretório estruturado e auditável.",
  "last_reviewed": "2026-07-27",
  "references": [
    {
      "title": "Canonical metadata and translation contract",
      "url": "https://github.com/djairofilho/awesome-latam-vc/blob/main/research/seo-geo/contract/README.md"
    }
  ]
}
---
# Metodologia

O Awesome LatAm VC publica visualizações estruturadas dos perfis Markdown
canônicos do repositório. A compilação lê cada perfil no local original, usa
seu front matter validado para os fatos normalizados e mantém o texto com
citações como registro editorial. O site não cria fatos ausentes desses
arquivos.

## Como o diretório é construído

Cada entidade tem identificador e slug estáveis. Os metadados registram tipo de
entidade, geografia, estágios, focos, URLs, fontes e data de verificação. O
corpo em Markdown fornece o contexto factual desses campos. O histórico do Git
preserva alterações que podem ser revisadas.

## O que os dados significam

Os valores normalizados facilitam a navegação e a comparação, mas não
substituem a linguagem da própria entidade. Uma tese declarada permanece
separada das observações de portfólio ou atividade. Um valor explícito de
ausência significa que a informação não foi divulgada publicamente nas
evidências registradas, e não que o projeto a estimou.

## Controles de qualidade

Os esquemas rejeitam identidades e enumerações inválidas. As verificações das
coleções rejeitam perfis duplicados, relações de tradução quebradas e
divergências em campos protegidos. As verificações de compilação garantem que
todo perfil canônico descoberto seja renderizado.

## Referências

- [Canonical metadata and translation contract](https://github.com/djairofilho/awesome-latam-vc/blob/main/research/seo-geo/contract/README.md)
