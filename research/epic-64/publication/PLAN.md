# Plano de publicação das plataformas

## Entrada

- issue: #95;
- epic: #64;
- fila congelada: issue #94;
- elegíveis: 9;
- tamanho máximo do lote: 10;
- lotes esperados: `ceil(9 / 10) = 1`.

## Estratégia

1. Ordenar candidatos `eligible` por `platform_id`.
2. Fixar o caminho de cada perfil antes da publicação.
3. Publicar o lote único da sub-issue #151 na branch
   `agent/issue-95-platforms-publication`.
4. Gerar perfis e índices EN/PT/ES a partir da fila congelada.
5. Congelar hashes de insumos, lote, perfis e índices.

O lote é reversível como uma unidade: seus nove perfis, índices e manifesto são
reproduzidos pelo mesmo gerador.

## Gates

- cobertura exata dos nove elegíveis, sem sobreposição;
- nenhum perfil originado de outra decisão;
- um lote não vazio com no máximo dez perfis;
- operador, marca, aliases, produtos, países, regulação e fontes preservados;
- zero links internos quebrados, duplicatas ou referências órfãs;
- hashes, determinismo e ausência de drift;
- validações da epic #64 e do repositório aprovadas.
