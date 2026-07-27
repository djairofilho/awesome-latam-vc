# Auditoria de aceleradoras no México, América Central e Caribe

Data de corte: 27 de julho de 2026. Issue: #72. Contrato: #68.

## Resultado

A auditoria percorreu 14 fontes oficiais em 12 mercados, com workers e shards
exclusivos. Nenhum perfil foi criado.

| Decisão | Quantidade | Candidatos |
| --- | ---: | --- |
| Elegível | 2 | 500 LatAm Accelerator; P18 |
| Evidência insuficiente | 6 | New Ventures; MassChallenge Mexico; Ruta Alterna; CREE Banreservas; Banj Accelerator; BELTRAIDE Entrepreneurship Development |
| Excluído | 3 | Centro de Innovación Ciudad del Saber; Honduras Digital Challenge; CubaEmprende |
| Encaminhado para `funds/` | 1 | Carao Ventures |
| Encaminhado para outra epic | 2 | SparkLabs Mexico; Programas CENPROMYPE |
| Total | 14 | 14 |

500 LatAm comprovou candidatura aberta até 31 de julho de 2026, seleção externa,
acesso latino-americano e percurso remoto personalizado de 6 a 12 meses. P18
comprovou geração 14, fase de avaliação, acompanhamento semanal e retomada de
inscrições em 2027.

## Cobertura e lacunas

México, Panamá, Honduras, Porto Rico, República Dominicana, Belize, El Salvador
e Nicarágua concluíram as fontes planejadas. Costa Rica, Guatemala, Haiti e Cuba
ficaram parciais porque uma fonte não respondeu de forma estável ou não publicou
sinal datado suficiente.

As principais lacunas são:

- atividade e candidatura atuais de New Ventures, Ruta Alterna, CREE
  Banreservas, Banj e BELTRAIDE;
- confirmação independente de um programa mexicano da SparkLabs;
- documentação oficial estável da Carao Ventures;
- fonte nacional adicional para El Salvador e Nicarágua além da CENPROMYPE.

Cada lacuna possui responsável e próxima ação em `candidates.jsonl`,
`source-inventory.jsonl` ou `coverage-matrix.jsonl`.

## Fronteiras editoriais

- Carao Ventures foi encaminhada para `funds/` porque a identidade localizada é
  dominada por investimento.
- CENPROMYPE foi encaminhada à Epic 65 por ser organismo público regional.
- SparkLabs foi encaminhada à auditoria de operadoras internacionais.
- Ciudad del Saber foi tratada como ecossistema/incubação.
- Honduras Digital Challenge foi tratado como competição por edição.
- CubaEmprende foi tratado como formação e apoio empresarial.

## Reprodutibilidade

Os 14 workers escreveram somente em
`research/epic-62/mexico-cac/shards/<worker-id>/`. O reducer de
`tools/research/shards.py` gerou `candidates.jsonl`, `evidence.jsonl`,
`source-inventory.jsonl` e `coverage-matrix.jsonl` em ordem determinística. O
manifesto consolidado registra as 14 tarefas, seus estados e eventuais erros.

Campos sem divulgação oficial permaneceram como `not_publicly_disclosed`.
Nenhuma duração, estágio, geografia, capital, instrumento ou equity foi inferido.
