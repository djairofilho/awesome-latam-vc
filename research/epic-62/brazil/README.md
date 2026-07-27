# Auditoria de aceleradoras no Brasil

Resultado da issue
[#71](https://github.com/djairofilho/awesome-latam-vc/issues/71), com data de
corte em 27 de julho de 2026. Esta etapa decide candidatos e lacunas; nenhum
perfil foi publicado.

## Resultado

- 20 fontes planejadas e percorridas: 19 concluídas e uma parcial;
- 20 candidatos decididos: oito elegíveis, três com evidência insuficiente,
  cinco encaminhados à epic #65, um encaminhado à issue #75 e três excluídos;
- 21 registros de evidência oficial;
- 20 tarefas concluídas, sem tarefa bloqueada;
- sete categorias de fonte cobertas.

As decisões elegíveis são WOW, Darwin Scale, Aceleração Digital FUNSES1,
InovAtiva Brasil, tecnoPARQ Acelera, GB Ventures, ACE Amazônia e Capital
Empreendedor RJ. Elas ainda dependem da revisão independente da issue #77 antes
de qualquer publicação.

Ventiur Acelera Impacto, Oxigênio e ACE For Doers ficaram com evidência
insuficiente. As fontes não demonstraram, na data de corte, uma edição recente
e verificável com todos os campos exigidos pelo contrato.

BRDE Labs RS, BNDES Garagem, Finep Mulheres Inovadoras, Acelera Divinópolis e
Acre for Startups foram encaminhados à epic #65. São iniciativas públicas com
rota estruturada de benefício financeiro.

Google for Startups Accelerator Brazil foi encaminhado à issue #75 porque a
operadora é estrangeira. A Aceleração Digital FUNSES1 permaneceu na epic #62:
a página oficial afirma que o programa não oferece investimento nem equity e
descreve o FIP associado como unidade separada.

Softville Ágora foi excluída por ser incubação; Quintessa, por operar programas
para terceiros; e Dasa Pulsa, por ser uma chamada de inovação aberta e prova de
conceito sem programa próprio de aceleração.

## Cobertura e lacunas

O recorte encontrou programas elegíveis com operação ou base verificável no Rio
Grande do Sul, Santa Catarina, Paraná, São Paulo, Minas Gerais e Rio de Janeiro,
além de programas nacionais. Também percorreu rotas públicas no Acre e no
Espírito Santo e uma chamada voltada à Amazônia.

O arquivo `state-coverage.jsonl` registra as 27 unidades federativas. Nove
receberam percurso direto: AC, ES, MG, PA, PR, RJ, RS, SC e SP. As outras
dezoito ficaram como lacuna acionável porque somente fontes nacionais foram
percorridas. A principal limitação é a ausência de um diretório público atual e
reproduzível da ABStartups por estado.

O recorte setorial alcançou programas generalistas, impacto socioambiental e
Amazônia, inteligência artificial, beleza e varejo, preparação para
investimento e tecnologia universitária. Agritech, biotecnologia, clima e saúde
apareceram em fontes de descoberta, mas sem uma quantidade suficiente de
programas privados locais que atendesse integralmente ao contrato.

## Artefatos

- `source-inventory.jsonl`: percurso e resultado de cada fonte;
- `coverage-matrix.jsonl`: cobertura final por categoria;
- `run-manifest.jsonl`: execução dos 20 workers;
- `candidates.jsonl`: decisão editorial de cada candidato;
- `evidence.jsonl`: evidências oficiais que sustentam as decisões.
- `state-coverage.jsonl`: fontes, candidatos e lacunas para as 27 UFs;
- `shards/`: saídas exclusivas dos vinte workers e do coordenador.

O plano foi congelado antes da coleta. A redução consolidada usa identificadores
estáveis, referências explícitas entre candidato e evidência e ordenação
determinística. A revisão da issue #77 deve testar novamente elegibilidade,
duplicatas, atividade, geografia e fronteira editorial.

O baseline congelado supercontou uma fonte corporativa e uma institucional. A
matriz preserva os valores originais, quatro e sete, e registra a errata para os
valores executáveis, três e seis. O manifesto congela os resultados com
SHA-256:

| Artefato | SHA-256 |
| --- | --- |
| `candidates.jsonl` | `cc05a4ee52fc151fc939694d9d961aad4899c25431aa6095a4e5fcc1a6293e01` |
| `coverage-matrix.jsonl` | `e2d3d878135f7fa55a17e9d658f5059efa1faa3ff0f578636ee99aec9ae3d28e` |
| `evidence.jsonl` | `cff9bdd0a7afe50498e28cd233c7ee874309071b7fc7ad37250e439df047f576` |
| `source-inventory.jsonl` | `ef039b96213e6341fcd047fe2d63f2950191b881e226c1ddacee182bcaf56886` |
| `state-coverage.jsonl` | `3187982f4c6107b0ff9d3142ce49038985fbbb599c39a2baddca98eeeeea33ac` |
