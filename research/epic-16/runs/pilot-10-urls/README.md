# Piloto de 10 fontes

O piloto foi executado em 2026-07-27 por três workers, sem usar o arquivo local
de startups e sem aprofundar candidatos.

## Resultado

- 10 fontes verificadas.
- 8 fontes parcialmente acessíveis e prontas para particionamento.
- 2 fontes indisponíveis no endereço declarado.
- 0 candidatos classificados ou publicados.

## Ajustes encontrados

- A Finep exige substituição da URL e revisão manual enquanto o `robots.txt`
  bloquear a coleta automatizada.
- A página AgTech Innovation da PwC retorna HTTP 404.
- BNDES exige intervalo mínimo de dois segundos.
- Sebrae e Open Startups precisam de estratégia para conteúdo dinâmico.
- Endeavor e ABVCAP expõem sitemap e estrutura WordPress aproveitável.
- ACATE e Porto Digital permitem referência, mas declaram `ai-train=no`.

O inventário detalhado está em
[`source-inventory.jsonl`](source-inventory.jsonl).
