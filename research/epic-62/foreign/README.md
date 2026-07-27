# Auditoria de aceleradoras estrangeiras

Auditoria executada para a issue #75, conforme o contrato da issue #68, com data
de corte em 27 de julho de 2026. O recorte cobre programas sediados fora da
América Latina com acesso latino-americano comprovado por fonte oficial.

## Resultado

Foram percorridas 12 fontes oficiais e decididos 12 candidatos:

| Decisão | Quantidade |
| --- | ---: |
| `elegível` | 8 |
| `excluído` | 2 |
| `encaminhado-para-funds` | 1 |
| `evidência-insuficiente` | 1 |

Os oito elegíveis comprovam acesso por escopo latino-americano explícito ou por
regra mundial aplicável:

- Google for Startups Accelerator: AI for Cybersecurity Latin America;
- Founder Institute LatAm Fall 2026;
- AWS Generative AI Accelerator;
- Berkeley SkyDeck Accelerator;
- Y Combinator Fall 2026;
- Alchemist Flagship;
- 500 Global Flagship Accelerator;
- Seedstars LIF CAF Rural Tech.

Nenhum perfil foi criado. Os elegíveis seguem para revisão independente na
issue #77.

## Fronteiras e lacunas

| Base | Fontes concluídas | Resultado e lacuna |
| --- | ---: | --- |
| Estados Unidos | 10/10 | Sete elegíveis. Microsoft Founders Hub e NVIDIA Inception foram excluídos por não terem coorte ou percurso finito. Techstars Anywhere ficou pendente porque a fonte não nomeia país latino-americano elegível. |
| Suíça | 1/1 | LIF CAF Rural Tech foi elegível por escopo explícito para América Latina e Caribe e encerramento recente dentro da janela de atividade. |
| Singapura | 1/1 | Antler foi encaminhada a `funds/` porque a própria operadora se define como VC de inception, com investimento recorrente. |

Portfólio e localização de alumni não foram usados para confirmar acesso.
Campos sem divulgação oficial permanecem como `not_publicly_disclosed`.

## Controles de execução

- 12 tarefas concluídas em 12 shards exclusivos;
- redução limitada à partição `foreign`;
- segunda redução com hashes SHA-256 idênticos nos quatro artefatos reduzidos;
- 12 URLs oficiais responderam HTTP 200;
- validação contratual e suíte de testes executadas sem erro;
- zero perfis publicados.

## Artefatos

- `source-inventory.jsonl`: inventário e estado das fontes;
- `candidates.jsonl`: decisões editoriais e campos canônicos;
- `evidence.jsonl`: evidência oficial por afirmação;
- `coverage-matrix.jsonl`: cobertura por país de origem da operadora;
- `run-manifest.jsonl`: execução, ownership e estado das tarefas;
- `shards/`: saídas exclusivas dos workers preservadas para auditoria.
