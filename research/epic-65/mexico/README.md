# Auditoría de programas públicos en México

Este directorio ejecuta el recorte mexicano de la
[#99](https://github.com/djairofilho/awesome-latam-vc/issues/99) conforme al
contrato de la [epic 65](../README.md). La fecha de corte es 2026-07-27.

## Cobertura

Antes de iniciar la recopilación, la matriz y el manifiesto fijaron cinco frentes
independientes:

1. SECIHTI como agencia federal de innovación;
2. Secretaría de Economía como ministerio responsable;
3. Nacional Financiera como banco público de desarrollo;
4. portal federal de convocatorias de la Secretaría de Economía;
5. FOJAL como fuente subnacional material.

Cada frente tiene un `worker_id` y un `shard_path` exclusivos. Las cinco tareas
terminaron. Este bundle cubre México en los niveles federal y subnacional
conforme al alcance solicitado. No presume elegibilidad a partir de nombres,
anuncios ni antecedentes.

## Resultado

Se consolidaron 5 agencias, 10 programas, 5 convocatorias y 22 evidencias
oficiales. Una ruta cumple el contrato:

- SECIHTI: el programa recurrente de desarrollo tecnológico e innovación otorga
  apoyo económico a micro y pequeñas empresas de base científica y tecnológica.
  Las convocatorias oficiales de 2025 y 2026 prueban recurrencia dentro de 24
  meses. La convocatoria 2026 conserva una etiqueta desactualizada frente a su
  fecha de cierre, por lo que su estado puntual queda `não confirmada`.

Impulsora de Innovación México sí ofreció coinversión directa a empresas
tecnológicas de alto crecimiento, pero el registro cerró el 30 de abril de 2026
y no existe recurrencia confirmada. El Fondo de Innovación Plan México tiene
recursos anunciados, pero todavía carece de reglas y canal propios. Ambos quedan
como `evidência insuficiente`, con responsable y próxima acción.

Plan México se excluyó porque es crédito sectorial general para MIPYMES; Capital
Emprendedor, porque recibe gestores y no tiene recursos disponibles; InnovaFest,
por ser una serie de premios; y Fondo Nacional Emprendedor, por inactividad.

En el nivel subnacional, FOJAL Emprende financia micronegocios tradicionales.
COMECYT mantiene abierta la convocatoria de Desarrollo de Prototipos 2026, pero
no confirma que la categoría editorial de startup sea elegible. Esta duda no se
resolvió por inferencia y quedó asignada.

## Consolidación y enlaces

Cada worker escribió solamente en `shards/<worker-id>/records.jsonl`.
[`consolidate.py`](consolidate.py) ordena shards e IDs, rechaza duplicados y
genera los cuatro archivos canónicos. La repetición de la reducción debe
conservar los mismos hashes.

[`link_audit.py`](link_audit.py) verifica HTTPS, dominios oficiales y, con
`--live`, disponibilidad HTTP. Respuestas 401, 403, 405 y 429 se registran como
bloqueo automatizado alcanzable; 404 y 410 fallan. Un timeout o fallo de DNS se
registra como no verificable, porque no demuestra por sí solo que el enlace esté
roto.

Esta issue no publica perfiles.

## Lagunas y límites

- La cobertura ministerial queda parcial hasta que el Fondo de Innovación Plan
  México publique reglas y una ruta operativa.
- La auditoría HTTP no pudo resolver el dominio de Impulsora de Innovación ni
  completar conexiones con varios portales estatales, aunque sus contenidos
  oficiales fueron recuperados por el índice y el navegador de investigación.
  Estos enlaces requieren una nueva comprobación manual.
- La admisión de startups en Desarrollo de Prototipos COMECYT requiere
  confirmación oficial; MIPYME innovadora no se trató automáticamente como
  startup.
- El recorte subnacional prueba rutas materiales en Jalisco y Estado de México,
  no la inexistencia de programas en las demás entidades federativas.
- Convocatorias y formularios son una fotografía del 2026-07-27 y deben
  recapturarse antes de publicar perfiles.
