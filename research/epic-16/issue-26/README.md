# Auditoria de investidores da região Andina

Este diretório registra a auditoria da
[#26](https://github.com/djairofilho/awesome-latam-vc/issues/26), conforme o
contrato da #17. A lista elegível foi congelada em **2026-07-27** para a etapa
de publicação da #28.

## Resultado

- 34 candidatos únicos revisados.
- 10 candidatos `elegível`.
- 9 candidatos `duplicado`.
- 6 candidatos `ecossistema`.
- 1 candidato `excluído`.
- 8 candidatos com `evidência insuficiente`.
- 0 candidatos `inativo`.
- 0 candidatos sem decisão.

## Lista elegível congelada para a #28

| Candidato | País-base | Cobertura oficial relevante |
| --- | --- | --- |
| Babasú Ventures | Bolívia | Bolívia, Equador e Peru |
| Escalatec | Bolívia | Bolívia |
| iThink VC | Paraguai | Bolívia, Equador e Peru |
| ADN.VC | Estados Unidos | América Latina, incluindo presença descoberta no Peru |
| EWA Capital | Colômbia | América Latina de língua espanhola |
| BuenTrip Ventures | Equador | Equador e América Latina |
| IMPAQTO Capital | Equador | Bolívia, Colômbia, Equador e Peru |
| MatterScale | Estados Unidos | Colômbia, Equador, Peru e América Latina |
| Ventures Comfama | Colômbia | Colômbia |
| Lightrock | Reino Unido | Colômbia e América Latina |

O congelamento preserva apenas a decisão de pesquisa. A #28 ainda deve revisar
o diretório de destino e os campos editoriais antes de publicar perfis.

## Cobertura por país

### Bolívia

O diretório público da BOCAP foi percorrido por completo. Seus quatro membros
foram classificados. Babasú Ventures, Escalatec e iThink VC têm tese oficial de
investimento direto e sinais atuais. Cibersons foi separado como entidade do
ecossistema. O Fondo Startup do BDP foi inventariado como programa público do
ecossistema, sem ser tratado como fundo privado elegível.

### Colômbia

A área pública da ColCapital não oferece uma exportação completa e estável de
membros. O recorte reproduzível usou as páginas públicas de reconhecimentos e
do curso de venture capital, que nomeiam gestores de VC/CVC. EWA Capital,
MatterScale e Ventures Comfama foram considerados elegíveis. ALIVE Ventures e
Cometa já possuem perfis canônicos. InQlab e H20 Capital ficaram pendentes por
falta de sinal oficial atual suficiente. Lightrock foi elegível; BASF Venture
Capital e Qualcomm Ventures ficaram pendentes porque as fontes oficiais não
comprovam o recorte colombiano.

### Equador

A lista pública da ECUACAP foi percorrida. BuenTrip Ventures e IMPAQTO Capital
foram elegíveis. iThink VC também cobre o país. New Ventures Capital já possui
perfil canônico. BuenaVista Capital Partners foi excluída por declarar private
equity. Endeavor Ecuador, Kruger Labs e Startups Ventures foram separados como
ecossistema. Creas Ecuador e Telefunken Capital ficaram pendentes por ausência
de prova oficial atual suficiente. Bio Legal e Netlife, descritas pela própria
associação somente como corporativos, foram registradas no inventário e não
viraram candidatos a fundo.

### Peru

O recorte de organizações de investimento do diretório da PECAP foi
percorrido. ADN.VC e EWA Capital foram elegíveis. UTEC Ventures, Alaya Capital,
Winnipeg Capital, B Venture Capital, Salkantay Ventures e Krealo já possuem
perfis canônicos. LUCHA e Confrapar ficaram pendentes porque a associação
descobre os nomes, mas suas fontes oficiais não confirmam os critérios completos
para o Peru. iThink VC também cobre o país.

### Venezuela

A Venecápital confirma uma comunidade ativa e uma vertical de venture capital,
mas não expõe uma lista pública auditável de fundos nem evidência individual de
investimento direto. A associação foi classificada como `ecossistema`. Nenhum
fundo venezuelano alcançou elegibilidade dentro das fontes declaradas. Esta é
uma lacuna explícita, não uma conclusão de inexistência.

## Método e limites

ColCapital, PECAP, BOCAP, ECUACAP e Venecápital foram usadas para descoberta.
Elegibilidade exigiu site oficial, investimento direto, geografia compatível e
atividade pública atual. A ausência de um desses elementos levou a
`evidência insuficiente`, não a uma inferência favorável.

A deduplicação comparou domínio normalizado, nome e aliases contra os perfis
existentes em `funds/`. O arquivo local de startups não foi usado para
descoberta, priorização, comprovação ou decisão. Não houve tentativa de
contornar login, paywall, bloqueio automatizado ou diretório não público.

## Artefatos

- [candidates.jsonl](candidates.jsonl): candidatos classificados e fila
  congelada.
- [evidence.jsonl](evidence.jsonl): evidência oficial usada nas decisões.
- [source-inventory.jsonl](source-inventory.jsonl): fontes, recortes e lacunas.
- [run-manifest.jsonl](run-manifest.jsonl): partições reproduzíveis da coleta.
