# Plano congelado — plataformas na região Andina

Issue regional: #92. Contrato: #89. Data de corte: 27 de julho de 2026.

Este plano foi congelado antes da coleta externa. A execução cobre Bolívia,
Colômbia, Equador, Peru e Venezuela. Nenhum perfil ou índice de publicação faz
parte do escopo.

## Matriz de pesquisa

O schema do contrato #89 fixa quatro categorias técnicas. Nesta execução, elas
correspondem às quatro dimensões temáticas solicitadas:

| Dimensão temática | Categoria do contrato |
| --- | --- |
| Plataforma | `official_platform` |
| Regulador | `regulator` |
| Crowdfunding/equity | `discovery` |
| Dívida/recebíveis | `public_ecosystem` |

Cada combinação país × dimensão possui um worker e um shard exclusivos. A
fonte inicial é uma hipótese de pesquisa, não uma conclusão de elegibilidade.

| País | Dimensão | Worker | Fonte inicial |
| --- | --- | --- | --- |
| Bolívia | Plataforma | `worker-bo-platform` | `https://www.crowdfundingbolivia.com/` |
| Bolívia | Regulador | `worker-bo-regulator` | `https://www.asfi.gob.bo/` |
| Bolívia | Crowdfunding/equity | `worker-bo-crowdfunding` | `https://produccion.gob.bo/` |
| Bolívia | Dívida/recebíveis | `worker-bo-debt` | `https://www.iqfinanzas.com/` |
| Colômbia | Plataforma | `worker-co-platform` | `https://a2censo.com/` |
| Colômbia | Regulador | `worker-co-regulator` | `https://www.superfinanciera.gov.co/` |
| Colômbia | Crowdfunding/equity | `worker-co-crowdfunding` | `https://www.bvc.com.co/a2censo` |
| Colômbia | Dívida/recebíveis | `worker-co-debt` | `https://mesfix.com/` |
| Equador | Plataforma | `worker-ec-platform` | `https://www.hazvaca.com/` |
| Equador | Regulador | `worker-ec-regulator` | `https://www.supercias.gob.ec/` |
| Equador | Crowdfunding/equity | `worker-ec-crowdfunding` | `https://www.supercias.gob.ec/portalscvs/` |
| Equador | Dívida/recebíveis | `worker-ec-debt` | `https://www.factoringecuador.com/` |
| Peru | Plataforma | `worker-pe-platform` | `https://inversiones.io/` |
| Peru | Regulador | `worker-pe-regulator` | `https://www.smv.gob.pe/` |
| Peru | Crowdfunding/equity | `worker-pe-crowdfunding` | `https://www.smv.gob.pe/ServicioPFP/` |
| Peru | Dívida/recebíveis | `worker-pe-debt` | `https://prestamype.com/` |
| Venezuela | Plataforma | `worker-ve-platform` | `https://www.crowdfundingvenezuela.com/` |
| Venezuela | Regulador | `worker-ve-regulator` | `https://www.sunaval.gob.ve/` |
| Venezuela | Crowdfunding/equity | `worker-ve-crowdfunding` | `https://www.sunaval.gob.ve/financiamiento-colectivo/` |
| Venezuela | Dívida/recebíveis | `worker-ve-debt` | `https://financredit.com.ve/` |

## Regras de decisão

1. O worker verifica `robots.txt` antes do conteúdo e não contorna bloqueios.
2. A rota para founders, a geografia e a atividade atual exigem fonte oficial.
3. Situação regulatória só é afirmada com fonte do regulador ou documento
   oficial; ausência em lista não é convertida em proibição.
4. Operador legal, marca, plataforma, produto, oferta e registro regulatório
   permanecem entidades separadas.
5. Oferta isolada nunca vira perfil. Aceleradoras, fundos, redes e programas
   públicos recebem `other_category` e encaminhamento explícito.
6. Toda descoberta chega ao freeze com uma decisão. Evidência insuficiente e
   lacunas registram responsável e próxima ação verificável.
7. Somente o reducer escreve os cinco artefatos regionais canônicos.

## Fechamento

O fechamento exige reducer byte-idempotente, hashes SHA-256 dos quatro
artefatos não circulares, links críticos revalidados, zero candidatos
indecisos, zero perfis e validação integral do contrato.
