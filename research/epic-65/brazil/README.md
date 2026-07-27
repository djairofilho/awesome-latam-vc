# Auditoria de programas públicos no Brasil

Este diretório executa a
[#98](https://github.com/djairofilho/awesome-latam-vc/issues/98) sob o contrato
da [epic 65](../README.md). A data de corte é 2026-07-27.

## Cobertura

Antes da coleta, a matriz e o manifesto congelaram cinco frentes independentes:

1. Finep como agência de inovação, incluindo os seeds Finep e Programa Inovar;
2. MCTI como ministério responsável;
3. BNDES como banco público de desenvolvimento, incluindo a Chamada de Clima;
4. Sebrae como portal oficial de chamadas e editais;
5. FAPESP PIPE como fonte subnacional material.

Cada frente possui um `worker_id` e um `shard_path` exclusivos. Todas foram
concluídas na data de corte. Nenhuma decisão de elegibilidade foi presumida a
partir dos seeds da epic 16.

## Resultado

Foram consolidadas 5 agências, 9 programas, 5 chamadas temporárias e 19
evidências oficiais. Três rotas permanentes atendem ao contrato:

- BNDES: Fundo Clima - Serviços e Inovação Verdes, com crédito para startups de
  inovação climática e solicitação pelo Portal do Cliente;
- Sebrae: Sebraetec Negócios Inovadores, com subsídio de até 90% do serviço
  tecnológico e formulário ativo para empresas com CNPJ;
- FAPESP: PIPE, com recursos não reembolsáveis e submissão contínua para
  pequenas empresas no estado de São Paulo.

Finep Startup foi classificado como inativo porque o fluxo contínuo está
suspenso desde 30 de junho de 2025. Programa Inovar, seleções de fundos do
BNDES, FIC-FIP do Sebrae e Mais Inovação Brasil foram preservados como
candidatos decididos, mas excluídos por não apresentarem rota explicitamente
destinada à candidatura de startups. Capital Empreendedor foi excluído por não
conceder benefício financeiro.

As chamadas foram avaliadas separadamente. PIPE Jornada Tecnológica e FIP
Conexões Startups estavam abertas na data de corte, mas a segunda recebe
propostas de gestores, não de startups. A Chamada de Clima e a seleção FIC-FIP
estavam encerradas. Nenhuma chamada recebe perfil.

## Consolidação

Cada worker gravou somente em `shards/<worker-id>/records.jsonl`. O
[`consolidate.py`](consolidate.py) percorre os shards em ordem lexicográfica,
rejeita IDs duplicados, separa os tipos e ordena cada arquivo canônico pelo ID.
Executá-lo novamente deve produzir os mesmos quatro arquivos consolidados.

Matriz e manifesto completam os seis artefatos do bundle. Nenhum perfil foi
publicado por esta issue.

## Limites e lacunas

- A auditoria comprova as cinco frentes declaradas, não a inexistência de toda
  iniciativa municipal, estadual ou setorial no Brasil.
- O PIPE é material, mas subnacional: sua rota exige sede ou unidade de P&D no
  estado de São Paulo.
- O percentual de subsídio do Sebraetec varia por unidade da federação; a
  confirmação local continua necessária antes de orientar uma candidatura.
- Chamadas e formulários são retratos de 2026-07-27 e precisam de nova captura
  após seus prazos ou antes da publicação de perfis.
