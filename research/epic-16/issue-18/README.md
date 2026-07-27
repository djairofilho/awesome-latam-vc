# Auditoria pública da Endeavor e da ABVCAP

Este diretório registra a primeira onda da
[#18](https://github.com/djairofilho/awesome-latam-vc/issues/18), conforme o
contrato da #17. A data de corte e de acesso é 2026-07-27.

## Resultado

- 9 fontes ou recortes inventariados.
- 5 recortes concluídos.
- 3 recortes parciais.
- 1 área autenticada indisponível para esta coleta.
- 234 ocorrências de organizações no recorte concluído.
- 228 candidatos canônicos após deduplicação entre as fontes.
- 16 candidatos já possuem perfil no baseline.
- 212 candidatos permanecem como `descoberto`, sem decisão de elegibilidade.
- 15 candidatos estrangeiros ausentes foram roteados para a fila da #24.

As 234 ocorrências vieram de:

| Recorte | Ocorrências |
| --- | ---: |
| Endeavor, patrocinadores e colaboradores | 29 |
| ABVCAP, gestores | 104 |
| ABVCAP, investidores | 27 |
| ABVCAP, prestadores de serviço | 65 |
| ABVCAP, gestores iniciantes | 9 |

O arquivo [candidates.jsonl](candidates.jsonl) contém a fila canônica. O arquivo
[foreign-candidates.jsonl](foreign-candidates.jsonl) é uma visão derivada para
a #24. Ele inclui apenas entidades estrangeiras identificadas de forma
conservadora pelo nome e domínio presentes no diretório. O país-base e a
estratégia para a América Latina ainda precisam de confirmação oficial.

## Recorte executado

Na Endeavor, a coleta percorreu a página pública completa do Mapa de Acesso a
Capital. Foram registrados 2 patrocinadores e 28 colaboradores únicos. EY
aparece nas duas seções e foi deduplicada. O formulário de conteúdo exclusivo
não foi preenchido.

Na ABVCAP, a coleta percorreu os quatro blocos completos da página pública
`Nossos Membros`, expostos pela API pública do WordPress. As 205 entradas e
seus links foram registradas. Organizações com o mesmo domínio não foram
unidas automaticamente. Isso preserva gestores, veículos e entidades
distintas que compartilham um site.

O catálogo público enumerou 49 publicações e 53 eventos. Somente os metadados
foram percorridos nesta onda. Os corpos, anexos e páginas externas permanecem
pendentes. A lista completa de membros em PDF também permanece pendente de
comparação com o HTML.

## Deduplicação

O baseline foi importado pelo normalizador do repositório. A comparação usou:

1. domínio oficial normalizado;
2. alias normalizado;
3. perfil canônico já associado ao domínio ou alias.

Quando duas ocorrências apontaram para o mesmo perfil do baseline, elas foram
mescladas no mesmo candidato e os nomes adicionais foram preservados em
`aliases`. Nomes idênticos em categorias diferentes da ABVCAP também foram
mesclados. Um domínio compartilhado, sozinho, não uniu entidades novas.

Diretórios foram tratados somente como descoberta. Os 212 candidatos novos não
foram marcados como elegíveis. Cada um possui uma próxima ação para validar
investimento direto, atividade recente e acesso de fundadores no site oficial.

## Evidências

Esta onda não gerou `evidence.jsonl`. Nenhuma página controlada pelo candidato
foi percorrida para comprovar investimento direto. Endeavor e ABVCAP são fontes
oficiais sobre seus próprios diretórios, mas continuam sendo fontes de terceiro
para a elegibilidade de cada candidato.

## Lacunas e fila restante

- Percorrer os corpos das 49 publicações em shards por item.
- Percorrer os corpos e páginas externas dos 53 eventos em shards por item.
- Extrair o PDF de membros e comparar suas entradas com as 205 entradas do
  HTML.
- Validar os 212 candidatos descobertos em sites oficiais.
- Confirmar país-base e atuação latino-americana dos 15 candidatos roteados
  para a #24.
- Manter a área autenticada fora da coleta até existir autorização explícita e
  acesso legítimo.

O [source-inventory.jsonl](source-inventory.jsonl) registra URL, recorte, hash
quando disponível, resultado, responsável e próxima ação. O
[run-manifest.jsonl](run-manifest.jsonl) mantém as tarefas concluídas e a fila
restante. A execução continua como `em execução` porque três shards públicos
permanecem abertos.

O arquivo local de startups não foi usado para descoberta, priorização,
comprovação ou decisão.
