# Issue 212 — lançamentos, fechamentos e início de operação

Pesquisa executada em 30 de julho de 2026, com corte de anúncios entre 30 de julho de 2023 e 30 de julho de 2026. A coleta usou somente fontes públicas não regulatórias. Nenhuma consulta à CVM foi feita.

## Método

A primeira passagem usou vocabulário em português associado a “novo fundo”, “lança fundo”, “nova gestora” e “seleciona gestor”. A descoberta priorizou imprensa especializada e, em seguida, páginas oficiais para validação.

A segunda passagem trocou o vocabulário para “primeiro fechamento”, “first close”, “fundo evergreen”, “primeiro investimento” e “fundo operacional”. Essa passagem buscou separar marcos que frequentemente aparecem misturados nas notícias:

1. **Anúncio:** intenção pública de criar um fundo ou gestora.
2. **Captação:** recursos ainda em levantamento, sem fechamento comprovado.
3. **Fechamento:** first close ou close explicitamente confirmado.
4. **Operação:** investimento concluído, carteira divulgada ou capital comprometido.

Cada nome e domínio foi comparado com `catalog-baseline.jsonl` e `prior-candidates.jsonl`. Candidatos do baseline não foram recriados.

## Resultado

| Candidato | Marco encontrado | Situação na entrega |
| --- | --- | --- |
| Sororitê Ventures | lançamento em 2024 e tese oficial com canal para startups | pesquisando; falta confirmar aportes concluídos e atividade recente |
| Nido / Platypus | nova gestora em 2025 e primeiro veículo oficial | pesquisando; fundo de fundos e coinvestimento ainda precisam ser separados |
| Mundi Ventures LatAm Fund I | anúncio para Brasil/LatAm em 2025 e first close oficial em 2026 | pesquisando; falta resolver identidade do veículo e canal brasileiro |
| BS2 Ventures | lançamento e dois investimentos diretos confirmados em 2024 | pesquisando; falta atividade oficial em 2025–2026 |
| L4 Venture Builder | lançamento em 2023 convertido em operação; 17 investimentos e 80% comprometido em 2026 | pesquisando; falta confirmar acesso externo permanente |
| Big Bets | first close do Fund II em 2025 e atividade oficial da gestora | pesquisando; o close ainda depende de fonte setorial de terceiros |

Os seis registros permanecem em `researching`, com `decision: null`, para que a issue integradora aplique os critérios editoriais e de identidade.

## Duplicatas e resultados sem candidato novo

- **DNA Capital VC II:** o spot-check de 2026 apontou início do período de investimento, mas o veículo e a gestora já estavam em `prior-candidates.jsonl`. Não foi recriado.
- **FIP Nordeste Capital Semente / Triaxis:** a seleção pública do gestor apareceu na passagem 1, mas ambos já estavam no baseline. O edital foi mantido no inventário apenas para documentar que seleção de gestor não prova operação.
- **DOMO.VC, Crescera, Vox Capital, ABSeed e The Yield Lab LatAm:** apareceram nas buscas de novos veículos, mas já possuíam perfil ou memória prévia; não geraram candidatos.

## Lacunas

- A busca por “evergreen” produziu principalmente veículos de private equity, fundos de acesso ou gestores já conhecidos. O único lead próximo do recorte, ABSeed Winners, foi publicado muito perto do corte e pertence a uma gestora já presente no baseline; não foi tratado como nova organização.
- O site da Nido não comprova investimento direto já concluído. “Possibilidade de coinvestimento” não foi convertida em confirmação de operação direta.
- O first close da Big Bets não foi localizado em página controlada pela gestora.
- Lançamento ou captação, isoladamente, não foi tratado como atividade operacional.
- A cobertura é auditável por consulta e fonte, mas não representa garantia matemática de exaustividade da internet aberta.
