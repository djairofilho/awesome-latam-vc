# Issue 20: matriz de CVCs brasileiros

Data de corte: 2026-07-27.

Esta primeira onda cobre os nove setores definidos na issue #20. A cobertura é
limitada às fontes, organizações e consultas registradas abaixo. Ela não afirma
que todos os CVCs de cada setor foram encontrados.

O Ranking 100 Open Startups e o Cubo Itaú foram usados somente para descoberta.
As decisões usam páginas e documentos oficiais. O arquivo local de startups não
foi usado para descoberta, priorização, comprovação ou decisão.

## Método

1. Abrir a categoria setorial de 2025 do Ranking 100 Open Startups.
2. Consultar a vitrine multissetorial do Cubo indicada pelo piloto.
3. Pesquisar os nomes e combinações setoriais nos domínios institucionais.
4. Separar empresa, programa corporativo, gestor e veículo.
5. Deduplicar o domínio e o nome contra os perfis já publicados.
6. Confirmar em fonte oficial equity, participação minoritária ou investimento
   por FIP. Pilotos, aceleração, contratação, grants e crédito não contam.
7. Registrar atividade recente quando uma fonte oficial dos 24 meses anteriores
   à data de corte estiver disponível.

## Matriz reproduzível

| Setor | Fonte de descoberta | Consultas registradas | Organizações oficiais consultadas | Resultado da primeira onda |
|---|---|---|---|---|
| Bancos | Open Startups, categoria Bancos 2025; Cubo Itaú | `site:inovabra.com.br ventures startups investimento`; `site:itau.com.br "Itaú Ventures"` | Bradesco/inovabra; Itaú | Fundo inovabra I elegível; Itaú Ventures duplicado |
| Seguradoras | Open Startups, categoria Seguros 2025; Cubo Itaú | `site:portoseguro.com.br "Oxigênio Aceleradora"`; `site:bradescoseguros.com.br "Inovação Aberta"` | Porto; Bradesco Seguros | Duas frentes de ecossistema; nenhum CVC elegível confirmado neste recorte |
| Energia | Open Startups, categoria Energia Elétrica e Renováveis 2025; Cubo Itaú | `site:edp.com "EDP Ventures" invest startups`; `site:edp.com.br "EDP Ventures" startups` | EDP | EDP Ventures elegível |
| Indústria | Open Startups, categoria Indústria Eletroeletrônica e Mecânica 2025; Cubo Itaú | `site:gerdau.com.br "Gerdau Next Ventures"`; `site:gerdau.com "Gerdau Next Ventures" startups` | Gerdau | Gerdau Next Ventures elegível |
| Varejo | Open Startups, categoria Varejo e Distribuição 2025; Cubo Itaú | `site:lojasrennersa.com.br "RX Ventures"`; `site:grupoboticario.com.br "Grupo Boticário Ventures"` | Lojas Renner; Grupo Boticário | RX Ventures elegível; Grupo Boticário Ventures duplicado |
| Saúde | Open Startups, categoria Indústria da Saúde 2025; Cubo Itaú | `site:grupopanvel.com.br "Corporate Venture Capital"`; `"Brazil healthcare corporate venture capital" site:.br` | Grupo Panvel | Panvel Ventures elegível |
| Telecomunicações | Open Startups, categoria Telecomunicações 2025; Cubo Itaú | `site:telefonica.com.br "Vivo Ventures" investimento`; `site:vivo.com.br "Vivo Ventures"` | Telefônica Brasil/Vivo | Vivo Ventures elegível; Wayra duplicado |
| Logística | Open Startups, categoria Transporte e Logística 2025; Cubo Itaú | `site:randoncorp.com "Randon Ventures" investimento`; `site:randoncorp.com "RV" startup investimento 2025` | Randoncorp | RV elegível |
| Agronegócio | Open Startups, categoria Agronegócio 2025; Cubo Itaú | `site:slcagricola.com.br ventures startups investimento`; `site:slcagricola.com.br "SLC Ventures"` | SLC Agrícola | SLC Ventures elegível |

As URLs exatas das categorias e das fontes oficiais estão em
`source-inventory.jsonl`. O inventário registra `parcial` para as fontes de
descoberta dinâmicas e `concluída` para cada recorte oficial percorrido.

## Decisões

Foram registrados 13 candidatos:

- 8 `elegível`;
- 3 `duplicado`;
- 2 `ecossistema`.

Elegíveis:

- Fundo inovabra I;
- EDP Ventures;
- Gerdau Next Ventures;
- RX Ventures;
- Panvel Ventures;
- Vivo Ventures;
- RV, da Randoncorp;
- SLC Ventures.

Duplicados do baseline:

- Itaú Ventures;
- Grupo Boticário Ventures;
- Wayra.

Frentes de ecossistema:

- Oxigênio Aceleradora, da Porto. A página oficial afirma que o programa não
  necessariamente investe em troca de participação societária.
- Inovação Aberta Bradesco Seguros. A página oficial comprova prospecção,
  testes e escala de soluções, mas não informa aporte direto desta frente.

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

As nove partições da primeira onda estão concluídas. A fila de uma segunda onda
é:

1. Renderizar em navegador as nove categorias do Ranking 100 Open Startups. O
   HTML público retorna `Carregando...` para as listas.
2. Particionar as vitrines públicas do Cubo em investors, corporates, partners e
   hubs, mantendo o hub somente como descoberta.
3. Ampliar seguradoras para todas as organizações exibidas na categoria e
   procurar separadamente veículos de seguradoras que não usem a marca do
   programa de inovação aberta.
4. Ampliar indústria para siderurgia, mineração, química, papel e celulose,
   bens de consumo e automotivo.
5. Ampliar saúde para hospitais, farmacêuticas, laboratórios, operadoras e
   varejo farmacêutico.
6. Confirmar canal de pitch para Gerdau Next Ventures, Panvel Ventures, Vivo
   Ventures, RV e SLC Ventures. A ausência pública foi mantida como `null`.

Responsável sugerido para a fila: `issue-20-next-run`.

## Artefatos

- `source-inventory.jsonl`: 23 fontes e recortes;
- `candidates.jsonl`: 13 candidatos deduplicados;
- `evidence.jsonl`: 16 evidências oficiais;
- `run-manifest.jsonl`: execução e nove tarefas setoriais.

O manifesto declara `local_startup_dataset_used: false`.
