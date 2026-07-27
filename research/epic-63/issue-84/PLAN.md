# Plano de auditoria de redes-anjo na região andina

Este plano congela a execução da issue
[#84](https://github.com/djairofilho/awesome-latam-vc/issues/84) antes da
coleta, com data de corte em 27 de julho de 2026 e janela de atividade iniciada
em 27 de julho de 2024.

## Recorte

A auditoria cobre Bolívia, Colômbia, Equador, Peru e Venezuela. Ela revalida
Startups Ventures, identificada na issue #26 por meio da ECUACAP, e procura
redes, clubes, alumni networks, capítulos e syndicates ativos. Não serão
criados ou alterados perfis.

O inventário inicial usa somente fontes institucionais dos ecossistemas
nacionais: BOCAP, ColCapital, ECUACAP, PECAP e Venecápital. Novas fontes só
podem ser consultadas depois de registradas no inventário do shard responsável.

## Particionamento

Há cinco workers de país e um consolidador. Cada worker escreve somente em
`research/epic-63/issue-84/shards/<worker-id>/`. O consolidador é o único
escritor dos cinco JSONLs canônicos e reduz os shards em ordem estável de ID.

## Decisões de fronteira

- capítulos sem autonomia comprovada são aliases do destino canônico;
- redes operadas por outra organização mantêm operador e rede separados;
- veículos de investimento recorrente são encaminhados para funds;
- aceleradoras, programas públicos e plataformas neutras recebem o
  encaminhamento previsto pelo contrato;
- nomes e domínios repetidos são deduplicados com destino explícito;
- organizações sem evidência oficial suficiente permanecem como candidatas
  decididas, sem inferências.

## Gates

1. plano, matriz, inventário e manifesto versionados antes da coleta;
2. cada fonte fica concluída, parcial ou indisponível, com justificativa;
3. cada candidato recebe decisão, inclusive duplicados e inelegíveis;
4. elegíveis exigem evidência oficial de categoria, atividade recente e acesso;
5. links representativos e `robots.txt` são auditados sem contornar bloqueios;
6. shards exclusivos e redução idempotente, conferida por hashes SHA-256;
7. validação do contrato, testes centrais, varredura UTF-8 e zero perfis;
8. relatório final resume cobertura, lacunas, responsáveis e próximas ações.
