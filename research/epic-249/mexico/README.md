# Reauditoria de fundos — México

Data de corte: `2026-07-30`.

Esta execução registra **cobertura auditada**, sem afirmar totalidade do mercado mexicano.

- 11 fontes não regulatórias: 10 completas e 1 `gap_justified`;
- 8 candidatos: 2 elegíveis, 2 duplicatas e 4 insuficientes;
- zero consultas regulatórias;
- 100% dos elegíveis revisados; rotas e casos regulatórios têm população zero;
- amostra determinística de 2/6 não elegíveis, pelos dois menores SHA-256 de `candidate_id`;
- busca cega adicionou três exclusões e nenhuma elegibilidade;
- um lote congelado, com 2 fundos e 6 perfis localizados.

O commit `5b3a4e0` já integra Entrypoint e Flourish Ventures ao baseline publicado. Ambos foram tratados como duplicatas correntes e guardas de deduplicação; nenhum foi replicado.
