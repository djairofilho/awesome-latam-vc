# Fechamento — redes-anjo do México, América Central e Caribe

## Escopo e corte

- Issue: #83.
- Contrato: #80.
- Data de corte: 2026-07-27.
- Janela de atividade recente: 2024-07-27 a 2026-07-27.
- Geografias: México, Belize, Costa Rica, El Salvador, Guatemala, Honduras, Nicarágua, Panamá, República Dominicana, Jamaica e Caribe regional.
- Perfis criados: zero.

AngelHub não foi recoletada. `ang-angelhub-mx` permanece somente como baseline mexicano validado na #81, sem fonte, tarefa, evidência ou candidato duplicado nesta execução.

## Resultado

Foram registradas 12 descobertas e todas receberam decisão:

| Decisão | Quantidade |
| --- | ---: |
| `elegível` | 2 |
| `evidência-insuficiente` | 2 |
| `inativo` | 1 |
| `encaminhado-para-funds` | 3 |
| `encaminhado-para-aceleradoras` | 2 |
| `encaminhado-para-plataformas` | 2 |

As entidades elegíveis são:

- [Enlaces](https://enlaces.org.do/preguntas-frecuentes/), da República Dominicana. A FAQ oficial confirma investimento anual desde 2015, seleção em três etapas, decisão por comitê/conselho e capital dos membros. Uma [publicação oficial de 22 de julho de 2026](https://es.linkedin.com/posts/enlaces-red-de-inversionistas-angeles_us53-millones-para-financiar-el-crecimiento-activity-7485823145283756032-0W8w) comprova atividade recente.
- [FirstAngels Caribbean](https://firstangelscaribbean.com/investor-faq/), sediada na Jamaica e antes chamada FirstAngels Jamaica. A FAQ oficial separa pré-seleção pela gestão de diligência, decisão e capital pelos membros e reuniões pelo menos bimestrais. A [publicação oficial de 28 de agosto de 2024](https://firstangelscaribbean.com/2024/08/28/celebrating-a-decade/) comprova atividade na janela.

Costa Rica Angels foi mantida como `evidência-insuficiente`: o [modelo oficial](https://www.parquetec.org/general-7) e a [convocatória oficial de 22 de julho de 2026](https://es.linkedin.com/posts/costa-rica-angels_startup-innovacion-fintech-activity-7485786275589861376-RMFA) confirmam rede, atores, acesso e atividade, mas a primeira convocatória ainda não prova seleção recorrente. Trigen Ventures também ficou pendente por não publicar rota externa, atores, recorrência ou atividade oficial datada.

As fronteiras foram aplicadas sem misturar categorias:

- Barrilete Ventures, Invertup e Venture Club Latam foram encaminhados para `funds/`.
- ParqueTec e Honduras Digital Challenge foram encaminhados para aceleradoras.
- Winverz e Caribbean Business Angel Network foram encaminhados para plataformas.
- O Venture Club histórico da Ciudad del Saber foi marcado inativo por não possuir identidade operacional ou atividade recente verificável.

## Cobertura e lacunas

| Geografia | Candidatos | Estado | Lacuna ou conclusão |
| --- | ---: | --- | --- |
| México | 0 | não aplicável | AngelHub já pertence ao baseline #81; as três sementes atribuídas ao México eram de Costa Rica, Guatemala e Panamá. |
| Belize | 0 | concluída | A estratégia oficial registra ausência de participação privada local e intenção de fomentar investimento-anjo; nenhuma rede operacional foi localizada. |
| Costa Rica | 4 | concluída | Uma rede recente pendente de recorrência, uma rede sem evidência operacional suficiente e duas fronteiras. |
| El Salvador | 0 | parcial | A fonte pública cobre inovação e empreendedorismo, mas não identifica rede-anjo operacional. |
| Guatemala | 2 | concluída | Um fundo e uma plataforma; nenhuma rede-anjo atual confirmada. |
| Honduras | 1 | concluída | A semente encontrada é aceleradora/programa. |
| Nicarágua | 0 | parcial | A fonte institucional não mantém diretório de capital empreendedor. |
| Panamá | 2 | concluída | Um fundo atual e um clube histórico inativo. |
| República Dominicana | 1 | concluída | Enlaces elegível. |
| Jamaica | 1 | concluída | FirstAngels Caribbean elegível; FirstAngels Jamaica é marca anterior, não capítulo autônomo. |
| Caribe regional | 1 | concluída | CBAN é plataforma de conexão e suporte, não rede com decisão e capital próprios. |

Pendências explícitas:

- El Salvador — responsável: `worker-el-salvador`; próxima ação: revalidar em diretório oficial de capital privado.
- Nicarágua — responsável: `worker-nicaragua`; próxima ação: revalidar em associação nacional de capital privado.
- Costa Rica Angels — responsável: `worker-costa-rica`; próxima ação: revalidar após o primeiro Demo Day e comprovar um novo ciclo oficial datado.
- Trigen Ventures — responsável: `worker-costa-rica`; próxima ação: obter publicação oficial datada e documentação do processo.

## Integridade

- Os shards são exclusivos por partição e o consolidator só possui matriz e manifesto.
- O redutor de `tools/research/shards.py` foi executado duas vezes; os cinco hashes canônicos permaneceram iguais.
- O validador da epic 63 e os 22 testes do contrato passaram.
- `link-audit.json` e `robots-audit.json` registram status HTTP, redirecionamentos, indisponibilidades e restrições.
- `sha256sums.txt` fixa os hashes SHA-256 dos cinco JSONLs canônicos.
