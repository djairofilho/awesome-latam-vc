# Plano de auditoria de aceleradoras no Brasil

Este plano é o gate anterior à coleta da issue
[#71](https://github.com/djairofilho/awesome-latam-vc/issues/71). A execução usa
data de corte em 27 de julho de 2026 e segue o contrato da epic #62.

## Recorte

A auditoria parte de fontes nacionais e de programas oficiais encontrados em
São Paulo, Rio de Janeiro, Minas Gerais, Rio Grande do Sul e Santa Catarina.
Diretórios nacionais e fontes da Anprotec e do Sebrae são usados para procurar
lacunas no Norte, Nordeste, Centro-Oeste, Espírito Santo e Paraná.

O recorte setorial começa generalista e testa programas de impacto, deep tech,
saúde, segurança digital, varejo, liderança feminina e inovação pública. A
ausência de um setor ou estado será declarada como lacuna, não como inexistência
de programas.

## Fontes planejadas

| Worker | Categoria | Fonte ou programa | Objetivo |
| --- | --- | --- | --- |
| `worker-br-01` | Associação | Anprotec | Descobrir aceleradoras e práticas reconhecidas nacionalmente |
| `worker-br-02` | Diretório | Sebraetec Negócios Inovadores | Percorrer a conexão nacional com incubadoras e aceleradoras |
| `worker-br-03` | Diretório | Mapeamento ABStartups | Procurar programas e lacunas estaduais |
| `worker-br-04` | Institucional | WOW | Validar programa, atividade, seleção e investimento |
| `worker-br-05` | Institucional | Darwin Startups | Separar programa próprio de corporate innovation |
| `worker-br-06` | Institucional | Ventiur | Separar aceleração, plataforma e investimento |
| `worker-br-07` | Governo | InovAtiva Brasil | Validar aceleração pública sem capital obrigatório |
| `worker-br-08` | Universidade | tecnoPARQ Acelera | Validar programa universitário e edição 2026 |
| `worker-br-09` | Universidade | BRDE Labs RS/Feevale | Validar programa regional recorrente |
| `worker-br-10` | Institucional | Softville Ágora | Testar a fronteira entre incubação e aceleração |
| `worker-br-11` | Governo | BNDES Garagem | Encaminhar corretamente programa público com capital |
| `worker-br-12` | Governo | Finep Mulheres Inovadoras | Encaminhar corretamente aceleração pública com prêmio |
| `worker-br-13` | Internacional | Google for Startups Accelerator Brasil | Encaminhar programa de operadora estrangeira |
| `worker-br-14` | Corporativa | GB Ventures | Separar aceleração estruturada de open innovation |
| `worker-br-15` | Corporativa | Oxigênio Porto Seguro | Reusar e atualizar a decisão do piloto sem duplicar |
| `worker-br-16` | Institucional | ACE Cortex | Verificar programa atual versus consultoria corporativa |
| `worker-br-17` | Institucional | Quintessa | Separar programa próprio de operação terceirizada |
| `worker-br-18` | Corporativa | Liga Ventures | Testar a fronteira de venture client e inovação aberta |
| `worker-br-19` | Governo | Capital Empreendedor RJ | Validar seleção e aceleração subnacional |
| `worker-br-20` | Governo | Acelera Divinópolis | Validar pré-aceleração municipal recorrente |

## Ownership e redução

Cada worker grava somente em
`research/epic-62/brazil/shards/<worker-id>/`. O arquivo consolidado não recebe
append concorrente. O coordenador reduz os shards em ordem de `candidate_id`,
resolve duplicatas e só então congela os cinco arquivos JSONL.

Uma fonte indisponível ou parcial mantém responsável e próxima ação. Fontes de
terceiros servem apenas para descoberta. Elegibilidade exige evidência oficial
de programa estruturado, acesso externo, geografia latino-americana e atividade
nos 24 meses anteriores à data de corte.

## Gates

1. plano, matriz e manifesto versionados;
2. coleta por fonte em shards exclusivos;
3. redução determinística e validação dos schemas;
4. resumo de cobertura estadual e setorial;
5. zero perfil publicado nesta issue;
6. decisões elegíveis revisadas independentemente na issue #77.
