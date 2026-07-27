# Plano de auditoria de redes-anjo no Cone Sul

Este plano congela a execução da issue
[#85](https://github.com/djairofilho/awesome-latam-vc/issues/85) antes da
coleta, com data de corte em 27 de julho de 2026 e janela de atividade iniciada
em 27 de julho de 2024.

## Recorte

A auditoria cobre Argentina, Chile, Paraguai e Uruguai. Ela procura redes,
clubes, alumni networks, capítulos e syndicates ativos. ARCAP, ACVC, PARCAPY e
URUCAP são fontes iniciais de descoberta e cobertura, não prova final de
elegibilidade. Nenhum perfil será criado ou alterado.

Novas fontes só podem ser consultadas depois de registradas no inventário do
shard responsável. Categoria, atividade, recorrência, acesso e atores de um
elegível exigem evidência oficial da própria organização ou do operador.

## Particionamento

Há quatro workers de país e um consolidador. Cada worker escreve somente em
`research/epic-63/southern-cone/shards/<worker-id>/`. O consolidador é o único
escritor dos cinco JSONLs canônicos e reduz os shards em ordem estável de ID.

## Identidade e fronteiras

- capítulos sem as quatro autonomias comprovadas são aliases da rede matriz;
- rede, operador e veículo de investimento mantêm atores e IDs separados;
- clubes e syndicates só entram quando os membros decidem e aportam capital;
- fundos recorrentes são encaminhados para `funds/`;
- aceleradoras, plataformas e programas públicos são encaminhados às epics
  #62, #64 e #65;
- comunidades, mentorias e investidores individuais são excluídos;
- duplicados e encaminhamentos preservam destino explícito.

## Gates

1. plano, matriz, inventário e manifesto versionados antes da coleta;
2. cada fonte fica concluída, parcial ou indisponível, com justificativa;
3. cada candidato recebe ID, decisão e evidência, inclusive negativos;
4. elegíveis comprovam seleção, decisão, capital, recorrência, atividade recente
   e acesso externo em fontes oficiais;
5. links representativos e `robots.txt` são auditados sem contornar bloqueios;
6. shards exclusivos e redução idempotente, conferida por hashes SHA-256;
7. validação do contrato, testes centrais, varredura UTF-8 e zero perfis;
8. relatório final resume cobertura, lacunas, responsáveis e próximas ações.
