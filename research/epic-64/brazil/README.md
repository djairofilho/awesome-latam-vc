# Auditoria de plataformas de captação no Brasil

Data de corte: 27 de julho de 2026. Issue regional: #90. Contrato: #89.

## Resultado

A auditoria percorreu o cadastro diário completo de plataformas de crowdfunding
da CVM, com 146 registros e 80 operadores em funcionamento normal no snapshot
de 24 de julho de 2026. O universo regulatório foi cruzado com fontes do Sebrae
e da CNI e com rotas oficiais que apresentavam sinais de captação para startups.
Isso produziu nove candidatos materialmente relacionados ao recorte:

| Decisão | Plataformas | Quantidade |
| --- | --- | ---: |
| Elegível | Captable, EqSeed, Kria e SMU | 4 |
| Evidência insuficiente | Arara Seed, Muse e Organismo | 3 |
| Outra categoria | 100 Open Angels e Ventiur | 2 |

Nenhum perfil foi criado. Uma oferta aberta da EqSeed foi registrada somente
como evidência temporária e permaneceu subordinada ao produto e à plataforma,
com `profile_eligible: false`.

## Cobertura

O inventário registra 17 fontes consultadas. As quatro categorias obrigatórias
ficaram completas por ao menos uma fonte concluída:

- regulador: cadastro diário da CVM, preservado no cache pelo SHA-256
  `9245ec8a9d1f0dec8d2e8679aecf1d25e507acaeb44aa740998f90a84646a622`;
- ecossistema público: enquadramento do Sebrae para capital empreendedor;
- plataforma oficial: rotas oficiais verificadas individualmente;
- descoberta: cartilha institucional da CNI/MEI.

O cadastro regulatório prova a situação da operadora, mas não prova sozinho que
exista uma rota atual e estruturada para founders. As páginas das plataformas
foram usadas para rota, instrumento, geografia e atividade. Fontes institucionais
de terceiros serviram apenas para descoberta.

## Pendências e fronteiras

- Arara Seed: o domínio mantém inscrições abertas, mas identifica no rodapé o
  CNPJ 35.440.796/0001-88, cancelado no cadastro da CVM em 4 de dezembro de
  2025. O operador ativo no mesmo cadastro é Arara Seed Investimentos S.A,
  CNPJ 46.638.808/0001-08. A identidade precisa ser reconciliada.
- Muse: a CVM registra funcionamento normal desde 1º de julho de 2026, mas o
  domínio publica apenas “Lançamento em breve”.
- Organismo: a CVM registra funcionamento normal sem website; o domínio derivado
  do e-mail cadastral não forneceu conteúdo verificável.
- Sebrae Agro Startups/Arara Seed: a página pública descoberta retornou HTTP
  502 e ficou bloqueada, sem participar da decisão.
- 100 Open Angels: a rota encontrada é um programa de 18 meses com seleção,
  smart money e desenvolvimento de negócios, encaminhado à fronteira da Epic 62.
- Ventiur: a apresentação auditada combina aceleração e investimento, sem rota
  pública distinta de plataforma de captação, também na fronteira da Epic 62.

Cada pendência de evidência possui `owner` e `next_action` em
`candidates.jsonl`; o acesso indisponível da Organismo também está explícito no
inventário e no manifesto.

## Reprodutibilidade

Os workers lógicos escreveram exclusivamente em:

```text
research/epic-64/brazil/shards/worker-regulator/
research/epic-64/brazil/shards/worker-public/
research/epic-64/brazil/shards/worker-discovery/
research/epic-64/brazil/shards/worker-platforms/
```

O reducer determinístico de `tools/research/shards.py` gerou os cinco arquivos
JSONL consolidados deste diretório. O ZIP regulatório original está em
`cache/cad_crowdfunding-2026-07-24.zip`.
