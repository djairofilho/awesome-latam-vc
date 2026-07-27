# Piloto de revalidação de aceleradoras

Este diretório registra o piloto executado para a issue
[#70](https://github.com/djairofilho/awesome-latam-vc/issues/70), com data de
corte em 27 de julho de 2026. O objetivo foi validar o contrato e o tooling das
issues #68 e #69 antes das auditorias regionais, usando os sete candidatos
herdados da epic #16 como casos adversariais.

Nenhum perfil foi publicado neste piloto. Os dois casos elegíveis seguem para a
consolidação e revisão independente da epic.

## Escopo e método

Foram percorridos sete domínios ou conjuntos de páginas, um por candidato:

1. página oficial do programa ou da organização;
2. rota oficial de candidatura, quando disponível;
3. evidência oficial de atividade, formato, público e geografia;
4. documentação complementar oficial quando a página principal não bastava;
5. fonte de terceiros somente para descoberta, nunca para comprovar
   elegibilidade.

As fontes antigas da epic #16 serviram apenas como ponte de descoberta. Todas as
decisões foram refeitas conforme o contrato atual. Ausência de informação foi
registrada como lacuna, sem inferir duração, capital, equity, geografia,
atividade ou recorrência.

## Resultado

| Decisão | Quantidade | Candidatos |
| --- | ---: | --- |
| Elegível | 2 | Boost Acceleration Camp; The Ganesha Lab, Go Europe Connect |
| Evidência insuficiente | 3 | Oxigênio Aceleradora; Kruger Labs; Cibersons |
| Excluído | 2 | StartupLab Dasa; WePartner |
| Total | 7 | 7 |

As sete tarefas chegaram a uma decisão editorial. Seis das sete fontes
planejadas foram concluídas integralmente; Kruger Labs ficou parcial. As lacunas
dos três casos com evidência insuficiente possuem responsável e próxima ação nos
artefatos.

O piloto separou três situações que o inventário anterior tratava de forma
ambígua:

- programa estruturado elegível, mesmo sem capital divulgado;
- inovação aberta ou company building, que não satisfaz a fronteira editorial;
- nome associado a investimento ou aceleração sem evidência oficial suficiente,
  que permanece pendente em vez de ser publicado.

## Ajustes encontrados pelo piloto

O estado `closed` foi acrescentado ao vocabulário de candidatura. Ele representa
uma chamada explicitamente encerrada quando não existe evidência suficiente de
recorrência para usar `closed_between_cycles`. A distinção evita transformar
uma inscrição antiga em sinal de atividade atual.

O teste também confirmou que:

- operadora, programa e veículo de investimento precisam permanecer como
  unidades distintas;
- um programa pode ser elegível sem prometer aporte;
- uma página que chama algo de aceleração não basta sem percurso, seleção,
  atividade e acesso verificáveis;
- uma descrição de rede social não pode substituir uma fonte oficial;
- decisões conservadoras precisam carregar lacuna, responsável e próxima ação.

## Artefatos

- `source-inventory.jsonl`: sete fontes e o recorte efetivamente percorrido;
- `coverage-matrix.jsonl`: seis células de país e categoria;
- `evidence.jsonl`: doze registros de evidência por afirmação;
- `candidates.jsonl`: sete decisões canônicas;
- `run-manifest.jsonl`: execução e sete tarefas.

Os artefatos são validados por JSON Schema e pelas invariantes cruzadas do
tooling. O manifesto registra que houve scraping/revalidação das páginas, mas
nenhum conteúdo integral foi copiado para o repositório.

## Lacunas e continuidade

- **Oxigênio:** confirmar calendário, candidatura e geografia atuais com a
  operadora.
- **Kruger Labs:** obter a página detalhada ou documentação oficial atual do
  programa.
- **Cibersons:** obter documentação oficial de eventual programa e encaminhar
  separadamente eventual veículo de investimento para `funds/`.

Essas lacunas não bloqueiam o piloto: os casos foram decididos como
`evidência-insuficiente` e não serão publicados sem nova evidência oficial.
