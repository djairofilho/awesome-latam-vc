---
{
  "schema_version": "1.0",
  "id": "editorial:methodology:es",
  "slug": "methodology",
  "locale": "es",
  "translation_of": "editorial:methodology:en",
  "translation_status": "complete",
  "title": "Metodología",
  "summary": "Cómo Awesome LatAm VC convierte perfiles Markdown respaldados por fuentes en un directorio estructurado y auditable.",
  "last_reviewed": "2026-07-27",
  "references": [
    {
      "title": "Canonical metadata and translation contract",
      "url": "https://github.com/djairofilho/awesome-latam-vc/blob/main/research/seo-geo/contract/README.md"
    }
  ]
}
---
# Metodología

Awesome LatAm VC publica vistas estructuradas de los perfiles Markdown canónicos
del repositorio. La compilación lee cada perfil en su ubicación, utiliza sus
metadatos iniciales validados para los datos normalizados y conserva la prosa
citada como registro editorial. El sitio no crea datos ausentes en esos archivos.

## Cómo se construye el directorio

Cada entidad tiene un identificador y un slug estables. Los metadatos registran
el tipo de entidad, la geografía, las etapas, los enfoques, las URL, las fuentes
y una fecha de verificación. El cuerpo Markdown aporta el contexto factual que
sustenta esos campos. El historial de Git conserva cambios que pueden revisarse.

## Qué significan los datos

Los valores normalizados facilitan la navegación y la comparación, pero no
reemplazan el lenguaje propio de una entidad. Una tesis declarada permanece
separada de las observaciones de cartera o actividad. Un valor explícito de
ausencia significa que la información no se divulgó públicamente en la evidencia
registrada, no que el proyecto la haya estimado.

## Controles de calidad

Los esquemas rechazan identidades y enumeraciones no válidas. Las verificaciones
de la colección rechazan perfiles duplicados, relaciones de traducción rotas y
divergencias en campos protegidos. Las verificaciones de compilación garantizan
que cada perfil canónico descubierto se renderice.

## Referencias

- [Canonical metadata and translation contract](https://github.com/djairofilho/awesome-latam-vc/blob/main/research/seo-geo/contract/README.md)
