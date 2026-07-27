# Plano de auditoria de redes-anjo no Brasil

Este plano congela a execução da issue
[#82](https://github.com/djairofilho/awesome-latam-vc/issues/82) antes da
coleta, com data de corte em 27 de julho de 2026.

## Recorte

A auditoria revalida Gávea Angels como semente histórica e procura redes,
clubes, alumni networks e syndicates sem repetir AngelHub, Anjos do Brasil, BR
Angels, GVAngels e Urca Angels, já tratados na issue #81.

O inventário inicial percorre Gávea Angels, Curitiba Angels, Floripa Angels,
Poli Angels, MIT Alumni Angels Brazil, Sororitê, WIM Angels, Mulheres
Investidoras Anjo, PUC Angels e Bossa Invest. Anjos do Brasil e seu relatório
nacional entram apenas como descoberta e controle de cobertura.

## Particionamento

Há 12 workers independentes. Cada um escreve somente em
`research/epic-63/issue-82/shards/<worker-id>/`. O coordenador reduz os shards
em ordem estável de ID e é o único escritor dos arquivos canônicos.

As frentes de cobertura são associação nacional, Sudeste, Sul, alumni networks,
redes de mulheres, diretório nacional e fronteira com fundos. Uma organização
com fundo e rede precisa manter seleção, decisão e capital separados.

## Gates

1. plano, matriz e manifesto versionados antes do scraping;
2. cada fonte concluída, parcial ou indisponível;
3. cada candidato decidido, inclusive duplicados e inelegíveis;
4. evidência oficial de categoria, atividade e acesso para elegíveis;
5. shards exclusivos e redução idempotente;
6. nenhum perfil publicado;
7. relatório final com cobertura, lacunas, owners e próximas ações.
