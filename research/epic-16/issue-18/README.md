# Auditoria pública da Endeavor e da ABVCAP

Este diretório registra o fechamento da
[#18](https://github.com/djairofilho/awesome-latam-vc/issues/18), conforme o
contrato da #17. A data de corte e de acesso é 2026-07-27.

## Resultado final

- 18 fontes ou recortes inventariados.
- 13 fontes concluídas.
- 4 fontes parciais.
- 1 área autenticada indisponível e fora do escopo autorizado.
- 248 ocorrências nas fontes de diretório: 29 da Endeavor, 205 do HTML da
  ABVCAP e 14 nomes adicionais no PDF após deduplicação.
- 242 candidatos canônicos.
- 5 candidatos `elegível`.
- 21 candidatos `duplicado`.
- 126 candidatos com `evidência insuficiente`.
- 90 candidatos `excluído`: 75 prestadores de serviços sem atuação investidora
  comprovada e 15 entidades estrangeiras fora do recorte Brasil.
- Nenhum candidato permaneceu sem decisão.

Os cinco elegíveis são Ahead Ventures, MSW Capital, Fundepar, Raio Capital e
Invest Tech. Honey Island Capital também teve investimento direto, atividade
recente e acesso externo confirmados, mas ficou como `duplicado` porque o perfil
já existe no baseline.

## Recorte percorrido

Na Endeavor, a coleta percorreu a página pública completa do Mapa de Acesso a
Capital. Foram registrados 2 patrocinadores e 28 colaboradores únicos. EY
aparece nas duas seções e foi deduplicada. O formulário de conteúdo exclusivo
não foi preenchido.

Na ABVCAP, a coleta percorreu os quatro blocos públicos de membros expostos pela
API WordPress: 104 gestores, 27 investidores, 65 prestadores de serviços e 9
gestores iniciantes. O catálogo, o corpo das 49 publicações e o corpo dos 53
eventos também foram percorridos. As páginas de eventos expuseram 20 links
externos não sociais: 17 responderam, 2 retornaram HTTP 404 e 1 entrou em loop
de redirecionamento. Os links acessíveis eram páginas de inscrição ou de
organização de eventos e não acrescentaram gestores.

O PDF oficial de membros, gerado em 17/07/2026, possui 8 páginas e 231
associações distribuídas entre apoiadores, gestores, gestores iniciantes,
investidores e prestadores. A comparação com o HTML identificou mudanças de
categoria, uma razão social alternativa da Valora e 14 nomes ausentes da fila
anterior. Os 12 novos prestadores foram excluídos do recorte de investidores.
BLUINVEST permaneceu com evidência insuficiente. Honey Island foi vinculada ao
perfil canônico existente.

## Decisões

Diretórios foram usados somente para descoberta e classificação do recorte.
Uma decisão `elegível` exigiu site controlado pelo candidato, investimento
direto, atividade recente e acesso externo para fundadores. Contato
institucional genérico não foi suficiente.

Prestadores identificados apenas nessa categoria foram marcados como
`excluído`. Entidades com país-base estrangeiro também foram excluídas do
recorte Brasil e preservadas em [foreign-candidates.jsonl](foreign-candidates.jsonl).
Os demais candidatos sem prova oficial suficiente receberam
`evidência insuficiente`, motivo explícito, responsável e próxima ação. Essa
decisão não afirma inatividade nem ausência de investimento.

## Deduplicação

O baseline foi importado pelo normalizador do repositório. A comparação usou
domínio oficial normalizado, aliases e perfil canônico. Organizações com o
mesmo domínio não foram unidas automaticamente quando representavam entidades
distintas. Mudanças de razão social claramente associadas ao mesmo domínio e à
mesma marca foram preservadas em `aliases`.

O PDF foi ligado como fonte de descoberta a todos os candidatos da ABVCAP que
ele confirmou. Os 231 vínculos de categoria correspondem a 218 candidatos
canônicos após a deduplicação entre categorias e razões sociais.

## Evidências e limitações

O arquivo [evidence.jsonl](evidence.jsonl) contém 16 registros oficiais para os
9 candidatos submetidos a validação individual. As ausências de prova oficial
nos demais registros não foram preenchidas com inferências.

As quatro fontes parciais são:

- ACE Outlier Capital, sem canal público inequívoco para fundadores.
- Eqwow Ventures, sem atividade recente datada ou canal de candidatura claro.
- Kortex Ventures, sem canal público inequívoco para fundadores.
- Eventos da ABVCAP, com dois links externos em HTTP 404 e um link em loop de
  redirecionamento.

A área autenticada da ABVCAP não foi acessada. Ela permanece indisponível até
existir autorização explícita e acesso legítimo.

O [source-inventory.jsonl](source-inventory.jsonl) registra URL, recorte,
resultado, hash quando disponível e limitações. O
[run-manifest.jsonl](run-manifest.jsonl) registra as tarefas e seu fechamento.
O arquivo local de startups não foi usado para descoberta, priorização,
comprovação ou decisão.
