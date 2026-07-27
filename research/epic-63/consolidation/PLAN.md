# Plano de consolidação das redes-anjo

## Entrada congelada

- Issue: #86.
- Epic: #63.
- Contrato: #80.
- Data de corte: 2026-07-27.
- Base inicial: `origin/agent/issue-85-angels-southern-cone` em
  `907bf9e39694c81f6c8094ab8be1043c20d842d8`.
- Auditorias: baseline #81, Brasil #82, México/América Central/Caribe #83,
  região andina #84 e Cone Sul #85.
- Perfis criados nesta etapa: zero.

`input-inventory.json` fixa caminhos, contagens e hashes antes da redução. O
consolidador deve abortar se qualquer entrada divergir do inventário.

## Redução e identidade

1. Ler os cinco artefatos canônicos de cada auditoria em ordem estável.
2. Rejeitar IDs repetidos com conteúdo divergente.
3. Preservar a auditoria de origem de cada candidato, evidência, fonte e célula.
4. Comparar domínio, operador, marca, aliases, capítulos, syndicates, perfis
   existentes, rotas e atores de capital.
5. Resolver duplicados diretamente contra um candidato ou perfil canônico, sem
   cadeias de aliases.
6. Manter operador, rede hospedada e veículo de capital como unidades distintas
   quando o contrato não autorizar a fusão.
7. Registrar cada saída para `funds/` ou epics #62, #64 e #65 com ID e destino.
8. Gerar fila publicável somente com candidatos elegíveis. Perfis baseline já
   existentes ficam separados dos candidatos pendentes de publicação.

## Before/after

O manifesto deve registrar:

- contagens por auditoria e por decisão antes da consolidação;
- 44 ocorrências e 44 IDs únicos na entrada;
- 57 evidências, 61 fontes e 42 células na entrada;
- contagens finais da fila canônica;
- duplicidades, aliases, identidades distintas e transferências;
- hashes de todas as entradas e saídas congeladas;
- drift zero após duas execuções consecutivas.

Nenhum registro negativo é descartado. A redução mantém decisões, razões,
responsáveis e próximas ações.

## Revisão independente

O consolidador e o revisor usam artefatos e identidades de autoria distintas:

- consolidador: `consolidator-issue-86`;
- revisor: `independent-reviewer-issue-86`;
- saída do revisor: `independent-review.jsonl` e `INDEPENDENT_REVIEW.md`.

O revisor confere:

- 100% dos elegíveis;
- 100% dos encaminhados;
- 100% dos casos limítrofes, definidos como `evidência-insuficiente`,
  `duplicado` ou identidade híbrida;
- amostra determinística mínima de 20% dos demais, ordenada pelo SHA-256 do
  `network_id`.

O freeze permanece provisório até a revisão cobrir o escopo, resolver todas as
divergências críticas ou altas e confirmar os destinos.

## Gates

- zero IDs ou referências órfãs;
- zero candidatos sem decisão;
- zero duplicatas conhecidas sem resolução;
- todo duplicado e encaminhamento com destino;
- capítulo standalone com quatro autonomias;
- 12 elegíveis revisados e fila publicável sem perfis novos;
- redutor determinístico e idempotente;
- hashes congelados e drift zero;
- testes específicos e da epic #63 aprovados;
- validação central aprovada;
- UTF-8 sem mojibake e `git diff --check` limpo;
- integração final com `origin/main` já contendo a #85.
