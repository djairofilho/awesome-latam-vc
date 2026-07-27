# Plano de consolidação dos programas públicos

## Entrada

- Issue: #102.
- Contrato: #97.
- Data de corte: 2026-07-27.
- Auditorias de entrada: Brasil (#98), México (#99), região andina (#100) e
  Cone Sul (#101).
- Perfis publicados nesta etapa: zero.

## Redução

1. Ler os seis artefatos canônicos de cada auditoria regional.
2. Ordenar por ID e rejeitar qualquer ID repetido com conteúdo divergente.
3. Verificar relações agência → programa → chamada → evidência.
4. Reconciliar transferências recebidas da epic #62.
5. Registrar contagens antes/depois e hashes das entradas e saídas.
6. Submeter 100% dos elegíveis e casos limítrofes a um agente independente.
7. Congelar a fila somente depois de resolver todas as divergências da revisão.

O manifesto consolidado preserva as 55 tarefas regionais sob um único `run_id`.
Os shards originais continuam sendo a proveniência; esta etapa não executa
scraping novo.

## Gates mecânicos

- baseline mecânico de 27 agências, 39 programas, 21 chamadas e 90 evidências;
- contagens finais podem crescer apenas pela materialização adjudicada das
  transferências recebidas, com before/after e hashes explícitos;
- zero IDs duplicados ou referências órfãs;
- zero agências ou programas sem decisão;
- toda pendência com responsável e próxima ação;
- toda transferência entre categorias com destino explícito;
- gerador idempotente e sem drift;
- schema e validador da epic #65 aprovados.

## Gate independente

O revisor deve conferir:

- 100% das agências e programas elegíveis;
- 100% das decisões por evidência insuficiente;
- 100% das fronteiras com fundos, aceleradoras ou chamadas não publicáveis;
- ausência de generalização de valores, prazos e disponibilidade;
- divergências e resolução individual.

O revisor não pode ser o consolidador. Até o relatório independente existir,
`consolidation-manifest.json` permanece com `status: provisional`.
