# Auditoria de redes-anjo na região andina

Resultado da issue
[#84](https://github.com/djairofilho/awesome-latam-vc/issues/84), com data de
corte em 27 de julho de 2026. A execução decidiu 6 candidatos a partir de 12
fontes institucionais e 7 evidências oficiais. Nenhum perfil foi criado.

## Resultado

| País | Candidatos | Elegíveis | Resultado e lacuna |
| --- | ---: | ---: | --- |
| Bolívia | 0 | 0 | A BOCAP publica quatro membros ativos, todos fora da categoria de rede-anjo. |
| Colômbia | 2 | 0 | A Red Colombiana de Inversiones foi encaminhada para plataformas; VCAngeles não possui atividade datada ou acesso verificável. |
| Equador | 1 | 0 | A ECUACAP revalida Startups Ventures como clube de anjos, mas o domínio oficial estava indisponível. |
| Peru | 2 | 1 | A PAD foi validada; The Board permanece insuficiente pela colisão entre rede e fundo e pela ausência de atividade datada. |
| Venezuela | 1 | 0 | Venecápital é associação de capital privado, não rede-anjo. |

A única elegível é **PAD — Red de Inversionistas Ángeles**, operada pelo Hub
UDEP. A fonte oficial informa 130 investidores, fóruns recorrentes, conexão de
empresas com investidores que aportam capital próprio e atividade iniciada em
11 de novembro de 2025.

## Identidades e fronteiras

- não foram encontrados capítulos ou aliases geográficos que exigissem
  consolidação;
- PAD e Hub UDEP foram separados como rede e operador;
- The Board explicita capital dos diretores e de um fundo, portanto os atores
  foram registrados separadamente;
- a Red Colombiana de Inversiones é matching comercial e tem destino proposto
  em `ecosystem/funding-platforms/`;
- Venecápital é associação/comunidade e foi excluída;
- Startups Ventures mantém o ID derivado do domínio e a decisão negativa
  explícita, sem criar perfil.

## Reprodutibilidade

Os workers escreveram somente em seus shards. A redução com
`tools/research/shards.py` foi executada duas vezes e preservou os cinco hashes
em `sha256sums.txt`. `link-audit.json` registra 12 links representativos e 11
arquivos `robots.txt`; nenhuma restrição foi contornada.

## Lacunas e próximas ações

- `worker-colombia`: revalidar VCAngeles quando houver processo e atividade
  oficial datada;
- `worker-ecuador`: repetir o acesso a Startups Ventures e exigir evidência de
  recorrência e candidatura;
- `worker-peru`: separar formalmente rede e fundo da The Board e obter atividade
  datada;
- revisar novos diretórios nacionais em rodada futura, preservando as decisões
  negativas desta auditoria.
