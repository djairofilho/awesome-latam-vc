# Auditoria de aceleradoras nos países andinos

Data de corte: 27 de julho de 2026. Issue: #73. Contrato: #68.

## Resultado

A auditoria percorreu 15 fontes oficiais, três por país, com workers e shards
exclusivos. Nenhum perfil foi criado.

| Decisão | Quantidade | Candidatos |
| --- | ---: | --- |
| Elegível | 2 | Aceleradora InnovaLab Mujeres Tech; Aceleradora UTEC Ventures |
| Evidência insuficiente | 4 | SOLYDES; Kruger Labs; BuenTrip Hub; IESA Emprende |
| Excluído | 4 | Aceleradora 100+ Bolivia; IMPAQTO; LIQUID Venture Studio; Impact Hub Caracas |
| Inativo | 1 | Wayra Venezuela |
| Encaminhado para outra epic | 3 | AgroInnovatec 2026; Emprendimiento Digital 2026; StartUp Perú |
| Operadora internacional | 1 | Rockstart LATAM |

InnovaLab comprovou programa para startups externas lideradas por mulheres,
mentorias, workshops e batch em março de 2026. UTEC Ventures comprovou seleção
externa, programa de 12 semanas, mentores, conexões de investimento e atividade
oficial em maio de 2026.

## Cobertura e lacunas

Colômbia, Equador e Venezuela concluíram as três fontes planejadas. Bolívia e
Peru ficaram parciais porque os domínios de SOLYDES e LIQUID não responderam no
link audit.

As lacunas acionáveis são:

- documentação atual do programa SOLYDES;
- percurso, seleção e chamada atuais de Kruger Labs e BuenTrip Hub;
- programa de aceleração atual do IESA;
- fonte oficial alternativa para LIQUID Venture Studio;
- confirmação histórica do encerramento da operação venezuelana da Wayra.

## Fronteiras

- Aceleradora 100+ foi tratada como desafio corporativo por edição.
- AgroInnovatec, Emprendimiento Digital e StartUp Perú foram encaminhados à
  Epic 65 por serem programas públicos.
- Rockstart foi encaminhada à auditoria de operadoras internacionais.
- IMPAQTO e Impact Hub Caracas foram tratados como comunidade, espaço e
  serviços sem programa canônico comprovado.
- LIQUID foi tratado como venture studio.

## Reprodutibilidade

Os 15 workers escreveram somente em
`research/epic-62/andean/shards/<worker-id>/`. O reducer de
`tools/research/shards.py` gerou os quatro JSONL reduzidos em ordem
determinística; o manifesto consolidado preserva as 15 tarefas.

Campos sem divulgação oficial usam `not_publicly_disclosed`. Nenhuma duração,
geografia, capital, instrumento ou equity foi inferido.
