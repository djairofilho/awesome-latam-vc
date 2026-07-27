# Auditoria de plataformas do Cone Sul

Este diretório fecha a issue #93 sob o contrato da epic #64. A data de corte é
27 de julho de 2026. A coleta foi manual, baseada em páginas oficiais e
regulatórias; não houve scraping. Os 16 shards exclusivos correspondem a quatro
países e quatro categorias de fonte.

## Resultado

Foram decididos oito candidatos, sem perfis publicados:

- **elegíveis:** Broota (Chile) e Crowder (Uruguai);
- **evidência insuficiente:** RedCapital e Cumplo (Chile), pois as rotas
  empresariais não confirmam oficialmente uma rota específica para startups;
- **excluídos:** Crowdium, por ser um produto imobiliário para investidores, e
  Afluenta Argentina, por ser crédito P2P genérico;
- **inativo:** Nexoos Paraguay, sem domínio oficial ou atividade paraguaia
  recente verificável;
- **outra categoria:** KOGA, incubadora/aceleradora pertencente à epic #62.

A matriz contém uma lacuna justificada: nenhuma plataforma oficial ativa pôde
ser confirmada no Paraguai. O domínio histórico da Nexoos permaneceu
indisponível, sem tentativa de contornar controles de acesso.

## Entidades e colisões

Operador, marca, plataforma, produto, oferta e registro regulatório possuem IDs
separados. A campanha Blanco é uma oferta encerrada da Broota e mantém
`profile_eligible: false`. O registro 4261 da Crowder está ligado diretamente à
evidência do Banco Central del Uruguay.

As fronteiras foram resolvidas assim:

- fundos e associações de venture capital encontrados por ARCAP, ACVC e URUCAP
  não foram tratados como plataformas;
- Broota Ventures é uma rota de aceleração da epic #62, distinta da plataforma
  permanente da Broota;
- redes de anjos da epic #63 não foram convertidas em plataformas;
- CORFO, MIC e ANDE são fontes do ecossistema ou programas públicos da epic
  #65, não candidatos privados desta auditoria;
- os fundos Moneda Cumplo não foram confundidos com a rota de crédito da
  plataforma Cumplo.

## Reprodução e auditoria

`prepare_dataset.py` materializa as decisões nos shards. `reduce.py` usa o
redutor central, rejeita colisões de chave, consolida em ordem determinística e
congela hashes SHA-256 com finais de linha normalizados em LF.

```powershell
python research/epic-64/southern-cone/prepare_dataset.py
python research/epic-64/southern-cone/reduce.py
python research/epic-64/southern-cone/audit_links.py
python -m unittest discover research/epic-64/southern-cone/tests
python research/epic-64/validate.py --dataset research/epic-64/southern-cone
```

`link-audit.jsonl` registra o estado dos 19 links inventariados e de seus
`robots.txt`, sem burlar bloqueios. Respostas 403, falhas de certificado e
indisponibilidade ficam explícitas e não anulam a evidência manual já registrada.
