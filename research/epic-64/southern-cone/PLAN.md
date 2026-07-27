# Plano de auditoria de plataformas no Cone Sul

Este plano congela a execução da
[#93](https://github.com/djairofilho/awesome-latam-vc/issues/93) antes da
coleta, com data de corte em 27 de julho de 2026.

## Recorte

A matriz cobre Argentina, Chile, Paraguai e Uruguai. Cada país possui tarefas
separadas para as quatro categorias obrigatórias do contrato da epic 64:

1. regulador;
2. ecossistema público;
3. plataforma oficial;
4. descoberta.

As passagens iniciais usam CNV Argentina, CMF Chile, Superintendencia de Valores
do Paraguai e BCU como fontes regulatórias; órgãos públicos nacionais como
fontes de ecossistema; Crowdium, Broota, Nexoos Paraguai e Crowder como pontos
de entrada de plataforma; e associações locais de capital empreendedor como
fontes de descoberta.

Uma fonte inicial não é uma decisão. Reguladores comprovam somente registro ou
autorização. Operadores e plataformas devem comprovar rota estruturada para
founders, instrumento, geografia e atividade recente.

## Identidade e fronteiras

Todo candidato material separará operador legal, marca, plataforma, produto,
oferta e registro regulatório. Oferta temporária nunca será perfil.

A coleta verificará colisões conhecidas antes de decidir:

- `funds/`, quando a organização investe capital próprio;
- epic 62, quando a rota é programa de aceleração;
- epic 63, quando organiza uma rede de investidores-anjo;
- epic 65, quando concede ou opera apoio estatal.

Imóveis, P2P genérico, doações, recompensas, tokens, diretórios e rotas
exclusivas para investidores serão excluídos sem inferir elegibilidade pelo
nome da marca.

## Execução

Há 16 tarefas lógicas e 16 workers, um por célula país × categoria. Cada worker
escreve exclusivamente em
`research/epic-64/southern-cone/shards/<worker-id>/`. O coordenador é o único
escritor dos cinco artefatos consolidados e reduz os shards em ordem estável.

Os workers respeitarão `robots.txt`, autenticação, CAPTCHA, WAF e limites de
acesso. Não haverá bypass. Fonte bloqueada ou indisponível ficará com
responsável e próxima ação.

## Gates

1. plano, inventário, matriz e manifesto versionados antes da coleta;
2. fonte inventariada com estado, robots, método e justificativa;
3. candidato e evidência sem referência órfã;
4. quatro categorias encerradas por país ou lacuna justificada;
5. shards exclusivos e redução determinística idempotente;
6. hashes SHA-256 dos quatro artefatos não circulares;
7. zero candidatos indecisos, zero perfis e colisões categóricas explícitas;
8. auditoria de links e resumo de cobertura e lacunas por país.
