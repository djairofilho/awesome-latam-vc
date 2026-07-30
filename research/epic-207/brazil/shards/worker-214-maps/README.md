# Issue 214 — mapas setoriais e fontes regionais

Auditoria executada em 30 de julho de 2026. Foram usadas apenas fontes públicas não regulatórias. Nenhuma consulta à CVM e nenhum arquivo local de startups foi usado.

## Método

A primeira passagem partiu de mapas e guias com operador, edição e data identificáveis para climate/impacto/bioeconomia, AgFoodtech, fintech, health/biotech, deep tech, proptech/construtech e SaaS/B2B. A segunda passagem trocou o eixo para fontes locais: universidade, hub, parque, governo e imprensa regional nas cinco regiões.

Nomes de mapas nunca foram importados em bloco. Cada possível investidor passou por:

1. leitura da função atribuída pelo mapa;
2. deduplicação por nome, alias e domínio contra baseline e shards #210–#212;
3. validação individual em fonte oficial;
4. registro como `researching`, com `decision: null`.

## Rendimento por vertical

| Vertical | Superfícies | Concluídas | Leads novos | Observação |
| --- | ---: | ---: | ---: | --- |
| Climate, impacto e bioeconomia | 2 | 2 | 1 | Barn; Jatobá aparece no recorte regional e eleva o total temático para 2 |
| Agtech e foodtech | 5 | 5 | 4 | Barn, AgroVen, Rural Ventures e Arar Capital |
| Fintech | 3 | 2 | 1 | Parallax; Fincatch não expôs lista pública de investidores |
| Health e biotech | 1 | 1 | 0 | guia enumera startups, não fundos |
| Deep tech | 1 | 1 | 0 | mapa divulga empresas e capital agregado |
| Proptech e construtech | 1 | 1 | 0 | mapa de logos é de startups; Terracotta já estava no baseline |
| SaaS e B2B | 2 | 2 | 1 | Parallax tem B2B SaaS no portfólio, mas sua tese principal é fintech |

## Rendimento por região

| Região | Superfícies | Leads novos | Resultado |
| --- | ---: | ---: | --- |
| Norte | 1 | 1 | Jatobá Gestora / Fundo Impacto Amazônia |
| Nordeste | 2 | 1 | LH Invest / LH Tech Ventures |
| Centro-Oeste | 2 | 1 | IPÊ Investe, ainda ambíguo entre investidor e aceleradora |
| Sul | 1 | 0 | Primus/Sul Ventures já estava no baseline |
| Sudeste fora das listas centrais | 1 | 0 | report do Rio mapeia startups, não investidores |

## Candidatos

- Barn Investimentos
- AgroVen
- Rural Ventures
- Arar Capital
- Parallax Ventures
- Jatobá Gestora / Fundo Impacto Amazônia
- LH Invest / LH Tech Ventures
- IPÊ Investe

Todos permanecem em pesquisa. AgroVen exige classificação do clube; Jatobá ainda não comprova primeiro aporte; IPÊ precisa ser separado de aceleradoras; Rural, Arar, Parallax e LH precisam de atividade oficial datada ou reconciliação de veículo.

## Deduplicação

AMZ Venture Capital, Primus/Sul Ventures, SP Ventures, The Yield Lab LatAm, SLC Ventures e VivaTerra já constavam do baseline ou dos shards #210–#212 e não foram recriados. Suzano Ventures continuou excluída por memória de descontinuação.

## Lacunas

- Health/biotech, deep tech, proptech/construtech e SaaS/B2B têm bons mapas de empresas, mas pouca enumeração pública, datada e auditável de investidores.
- A página pública do Fincatch 2025 descreve o mapa, mas não permite percorrer os investidores.
- Norte, Sul e Sudeste interior ainda precisam de mais fontes universitárias e parques com listas explícitas de capital privado.
- Mapas de ecossistema frequentemente misturam fundo, CVC, clube, aceleradora, plataforma e instituição de fomento; nenhuma dessas classes foi decidida automaticamente.
- A cobertura mede superfícies percorridas e rendimento, não garante exaustividade matemática da internet aberta.
