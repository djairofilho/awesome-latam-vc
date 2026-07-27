# Plano de consolidação das aceleradoras

## Gate de entrada

- Issue: #76.
- Contrato: #68.
- Data de corte herdada das execuções: 2026-07-27.
- Entradas congeladas: piloto e auditorias de Brasil, México/CAC, região
  andina, Cone Sul e operadoras estrangeiras.
- Unidade de saída: um registro por `candidate_id` canônico.
- Perfis publicados nesta etapa: zero.

## Ordem determinística

1. Ler as execuções em `pilot`, `brazil`, `mexico-cac`, `andean`,
   `southern-cone` e `foreign`.
2. Ordenar cada entrada pelo ID definido em seu schema.
3. Em IDs repetidos, preferir a auditoria regional posterior ao piloto e unir
   as listas de fontes e evidências sem perder proveniência.
4. Aplicar somente as resoluções explícitas versionadas em
   `build_registry.py`.
5. Ordenar o registro final por `candidate_id`.
6. Gerar índices, relatório e hashes a partir dos mesmos bytes.

Uma divergência de ID entre duas auditorias regionais interrompe a execução.
Somente `accel-oxigenio` e `accel-kruger-labs`, duplicatas esperadas entre
piloto e revalidação regional, podem ser fundidos.

## Resoluções previstas

- converter o encaminhamento interno do Google Accelerator Brasil em
  `elegível`, pois a auditoria brasileira já contém todas as provas oficiais;
- converter Rockstart LATAM e SparkLabs Mexico em
  `evidência-insuficiente`, com responsável e próxima ação, pois a auditoria
  estrangeira não produziu registros canônicos correspondentes;
- normalizar encaminhamentos públicos para IDs da epic #65;
- normalizar encaminhamentos de fundos para caminhos publicados ou para o
  namespace explícito de backlog `funds/:<vehicle-id>`;
- manter programas e veículos como unidades separadas nos casos híbridos;
- registrar, sem inferência, todos os veículos ainda ausentes do catálogo.

## Gates

- 80 ocorrências de entrada e 78 candidatos canônicos;
- nenhum `decision: null`;
- toda evidência e fonte referenciada existe no bundle consolidado;
- toda pendência de evidência possui `owner` e `next_action`;
- todo encaminhamento possui destino canônico;
- nenhuma referência interna a “epic-75” ou “Issue #75” permanece;
- duas execuções consecutivas geram bytes idênticos;
- schemas, testes específicos e validação central passam;
- arquivos UTF-8 não contêm mojibake.
