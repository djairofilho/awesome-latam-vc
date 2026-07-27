# Plano de auditoria de plataformas no México, América Central e Caribe

Este plano congela a execução da issue
[#91](https://github.com/djairofilho/awesome-latam-vc/issues/91) antes da
coleta, com data de corte em 27 de julho de 2026.

## Recorte

A matriz cobre México, Costa Rica, Cuba, República Dominicana, Guatemala,
Honduras, Haiti, Nicarágua, Panamá e El Salvador. Cada país possui tarefas
separadas para regulador, ecossistema público, plataforma oficial e descoberta.

O México recebe uma segunda passagem regulatória sobre a lista completa de
Instituciones de Financiamiento Colectivo da CNBV e uma passagem de produto
sobre Arkangeles, Play Business e Snowball. Nos demais países, a busca testa
rotas locais e estrangeiras de equity, dívida, revenue share, recebíveis e
matching, preservando como exclusão qualquer rota apenas de doação, recompensa,
imóveis, P2P genérico ou investimento sem fluxo para founders.

## Execução

Há 40 tarefas lógicas e 40 workers, um por célula país × categoria. Cada worker
escreve exclusivamente em
`research/epic-64/mexico-cac/shards/<worker-id>/`. O coordenador é o único
escritor dos cinco arquivos consolidados e executa o redutor em ordem estável de
ID.

Os workers devem respeitar `robots.txt`, autenticação e limites de acesso. Não
há bypass de CAPTCHA ou WAF. Fontes bloqueadas viram lacunas com responsável e
próxima ação.

## Fontes iniciais

- reguladores financeiros nacionais, com CNBV como fonte canônica mexicana;
- órgãos públicos de empreendedorismo e desenvolvimento empresarial;
- Arkangeles, Play Business, Snowball, Jompéame, Hagámosla, Zafèn e Fortesza;
- fontes institucionais de ecossistema e descoberta regional.

Uma fonte inicial não é uma decisão. Reguladores comprovam somente autorização;
plataformas comprovam rota, instrumento, geografia e atividade; terceiros
servem apenas para descoberta.

## Gates

1. plano, matriz e manifesto versionados antes da coleta;
2. fonte inventariada com estado e justificativa;
3. candidato, evidência e entidade regulatória sem referências órfãs;
4. quatro categorias encerradas por país ou lacuna justificada;
5. shards isolados e redução determinística idempotente;
6. nenhum perfil publicado;
7. resumo explícito de cobertura e lacunas por país.
