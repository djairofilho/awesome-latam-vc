# Issue 20: matriz de CVCs brasileiros

Data de corte: 2026-07-27.

As duas ondas cobrem os nove setores definidos na issue #20 e aprofundam
seguros, indústria e saúde. A cobertura é limitada às fontes, organizações e
consultas registradas abaixo. Ela não afirma que todos os CVCs de cada setor
foram encontrados.

O Ranking 100 Open Startups e o Cubo Itaú foram usados somente para descoberta.
As decisões usam páginas e documentos oficiais. O arquivo local de startups não
foi usado para descoberta, priorização, comprovação ou decisão.

## Método

1. Renderizar em navegador as categorias setoriais de 2025 do Ranking 100 Open
   Startups.
2. Particionar as vitrines públicas do Cubo em investors, corporates, partners
   e hubs.
3. Pesquisar os nomes e combinações setoriais nos domínios institucionais.
4. Separar empresa, programa corporativo, gestor e veículo.
5. Deduplicar o domínio e o nome contra os perfis já publicados.
6. Confirmar em fonte oficial equity, participação minoritária ou investimento
   por FIP. Pilotos, aceleração, contratação, grants e crédito não contam.
7. Registrar atividade recente quando uma fonte oficial dos 24 meses anteriores
   à data de corte estiver disponível.

## Matriz reproduzível

| Setor | Fonte de descoberta | Organizações oficiais consultadas | Resultado acumulado |
|---|---|---|---|
| Bancos | Open Startups, Bancos; Cubo | Bradesco/inovabra; Itaú | Fundo inovabra I elegível; Itaú Ventures duplicado |
| Seguradoras | Open Startups, Seguros; Cubo | Porto; Bradesco Seguros; Alper; Brasilseg | Oxigênio, Bradesco Seguros e Impulso Open classificados como ecossistema; AlperTech com evidência insuficiente |
| Energia | Open Startups, Energia; Cubo | EDP | EDP Ventures elegível |
| Indústria | Open Startups, seis categorias industriais e Automotivo; Cubo | Gerdau; ArcelorMittal Brasil; Suzano | Gerdau Next Ventures e Açolab Ventures elegíveis; Suzano Ventures inativa |
| Varejo | Open Startups, Varejo; Cubo | Lojas Renner; Grupo Boticário | RX Ventures elegível; Grupo Boticário Ventures duplicado |
| Saúde | Open Startups, Serviços de Saúde e Farmacêutica; Cubo | Grupo Panvel; RD Saúde; Eurofarma; Dasa | Panvel Ventures, RD Saúde Ventures e Eurofarma Ventures elegíveis; StartupLab Dasa classificado como ecossistema |
| Telecomunicações | Open Startups, Telecomunicações; Cubo | Telefônica Brasil/Vivo | Vivo Ventures elegível; Wayra duplicado |
| Logística | Open Startups, Transporte e Logística; Cubo | Randoncorp | RV elegível |
| Agronegócio | Open Startups, Agronegócio; Cubo | SLC Agrícola | SLC Ventures elegível |

As URLs e os escopos exatos estão em `source-inventory.jsonl`. O registro
`src-os-rendered-wave-2` consolida 15 categorias e 123 linhas renderizadas. O
registro `src-cubo-partitions-wave-2` separa 23 investors, 77 corporates, 56
partners e 14 hubs. Ambos continuam sendo apenas fontes de descoberta.

## Decisões

Foram registrados 20 candidatos:

- 11 `elegível`;
- 3 `duplicado`;
- 4 `ecossistema`;
- 1 `inativo`;
- 1 `evidência insuficiente`.

Elegíveis:

- Fundo inovabra I;
- EDP Ventures;
- Gerdau Next Ventures;
- RX Ventures;
- Panvel Ventures;
- Vivo Ventures;
- RV, da Randoncorp;
- SLC Ventures;
- Açolab Ventures;
- RD Saúde Ventures;
- Eurofarma Ventures.

Duplicados do baseline:

- Itaú Ventures;
- Grupo Boticário Ventures;
- Wayra.

Frentes de ecossistema:

- Oxigênio Aceleradora, da Porto. A página oficial afirma que o programa não
  necessariamente investe em troca de participação societária.
- Inovação Aberta Bradesco Seguros. A página oficial comprova prospecção,
  testes e escala de soluções, mas não informa aporte direto desta frente.
- StartupLab Dasa. A FAQ oficial refuta investimento e limita o programa a
  contratos e parcerias comerciais.
- Impulso Open, da Brasilseg. O relatório de 2025 comprova apresentações e
  projetos com startups, mas não aporte societário.

Inativo:

- Suzano Ventures. O Relatório de Sustentabilidade 2025 informa que a iniciativa
  foi descontinuada.

Evidência insuficiente:

- AlperTech. A Alper afirma financiar startups, mas não esclarece se há equity,
  instrumento conversível ou participação minoritária.

## Entidades e aliases

O Fundo inovabra I e o Vivo Ventures foram registrados como veículos. RX
Ventures também foi registrado como veículo porque a página oficial descreve o
fundo e sua tese. EDP Ventures, Gerdau Next Ventures, Panvel Ventures e SLC
Ventures foram registrados como programas corporativos. A RV foi registrada
como organização porque a Randoncorp a descreve como empresa de investimento e
aceleração.

Aliases históricos ou operacionais foram preservados, incluindo Paris Ventures,
Ventures Gerdau, Randon Ventures, Wayra Brasil, GB Ventures e inovabra ventures.
Nenhum alias foi unido automaticamente a um veículo diferente.

## Lacunas e fila restante

O escopo de alto impacto desta onda foi encerrado. A fila residual é:

1. esclarecer em fonte societária se o financiamento da AlperTech inclui
   participação acionária;
2. validar eventuais veículos próprios de Porto, Brasilseg, Sompo e IRB(Re) que
   não usem a marca de seus programas de inovação aberta;
3. aprofundar hospitais, laboratórios e operadoras fora das organizações
   exibidas nos rankings renderizados;
4. revisar Qualcomm Ventures, encontrada na vitrine de investors do Cubo,
   somente se uma fonte oficial confirmar mandato ou atividade no Brasil;
5. confirmar canal de pitch para Gerdau Next Ventures, Panvel Ventures, Vivo
   Ventures, RV e SLC Ventures. A ausência pública foi mantida como `null`.

Responsável sugerido para a fila: `issue-20-next-run`.

## Artefatos

- `source-inventory.jsonl`: 32 fontes e recortes;
- `candidates.jsonl`: 20 candidatos deduplicados;
- `evidence.jsonl`: 23 evidências oficiais;
- `run-manifest.jsonl`: duas execuções e 15 tarefas.

O manifesto declara `local_startup_dataset_used: false`.
