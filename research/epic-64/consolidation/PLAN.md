# Plano de consolidação das plataformas de investimento

## Entrada

- Issue: #94.
- Contrato: #89.
- Data de corte: 2026-07-27.
- Auditorias: Brasil (#90), México/CAC (#91), região andina (#92) e Cone Sul
  (#93).
- Perfis publicados nesta etapa: zero.

## Deduplicação em duas passagens

1. Agrupar por domínio canônico e marca normalizada.
2. Agrupar por identidade legal e, quando existir, autoridade/jurisdição/número
   regulatório.
3. Ignorar como chave de identidade valores explicitamente desconhecidos.
4. Interromper diante de IDs repetidos ou grupos ambíguos não resolvidos.
5. Ordenar candidatos, evidências, fontes e cobertura por seus IDs.

Operador, marca, plataforma, produto, oferta e registro regulatório continuam
unidades distintas dentro do candidato canônico.

## Fronteiras

- todo `other_category` recebe destino canônico em outra epic;
- transferências recebidas da epic #63 são reconciliadas por ID e domínio;
- veículo, aceleradora, rede-anjo ou programa público não é convertido em
  plataforma apenas por aparecer em uma fonte de descoberta;
- decisões por evidência insuficiente permanecem com responsável e próxima
  ação.

## Gates

- 38 candidatos, 62 evidências, 117 fontes e 20 países antes e depois;
- zero IDs/referências órfãs, decisões nulas ou duplicatas conhecidas;
- relatório before/after e hashes SHA-256;
- gerador idempotente e validação da epic #64 aprovada;
- revisão independente de 100% dos elegíveis, pendências e fronteiras;
- manifesto somente congelado após a resolução das divergências.
