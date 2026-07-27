# Plan de auditoría de programas públicos en México

Este directorio ejecuta el recorte mexicano de la
[#99](https://github.com/djairofilho/awesome-latam-vc/issues/99) conforme al
contrato de la [epic 65](../README.md). La fecha de corte es 2026-07-27.

## Cobertura congelada

Antes de iniciar la recopilación, la matriz y el manifiesto fijan cinco frentes
independientes:

1. SECIHTI como agencia federal de innovación;
2. Secretaría de Economía como ministerio responsable;
3. Nacional Financiera como banco público de desarrollo;
4. portal federal de convocatorias de la Secretaría de Economía;
5. FOJAL como fuente subnacional material.

Cada frente tiene un `worker_id` y un `shard_path` exclusivos. Este bundle cubre
México en los niveles federal y subnacional conforme al alcance solicitado. No
presume elegibilidad a partir de nombres, anuncios ni antecedentes.

## Orden de ejecución

1. congelar matriz y manifiesto;
2. recorrer inventarios y fuentes oficiales;
3. registrar cada frente solamente en su shard;
4. consolidar los cuatro archivos de entidades de forma determinista;
5. validar referencias, evidencia, fechas, enlaces, cobertura y decisiones.

Esta issue no publica perfiles.
