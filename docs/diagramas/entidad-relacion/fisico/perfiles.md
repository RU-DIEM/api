---
icon: lucide/id-card
---

# Perfiles

Diez tablas: tres de estructura académica y siete de perfil.

```mermaid
---
config:
  elk:
    nodePlacementStrategy: NETWORK_SIMPLEX
  fontFamily: monospace
  layout: elk
---
erDiagram
  facultad {
    uuid      id           PK
    varchar   codigo       UK
    varchar   nombre
    varchar   nombre_corto
    boolean   activa
  }
  carrera {
    uuid      id             PK
    varchar   codigo         UK
    varchar   nombre         UK
    uuid      facultad_id    FK
    smallint  duracion_anios
    boolean   activa
  }
  institucion {
    uuid         id              PK
    varchar      nombre
    varchar      tipo
    varchar      pais
    timestamptz  normalizada_at
    uuid         fusionada_en_id FK
    boolean      activa
  }
  perfil_estudiante {
    uuid         id              PK
    uuid         usuario_id      UK
    varchar      origen
    uuid         institucion_id  FK
    varchar      carrera_externa
    text         ocupacion
    timestamptz  actualizado_at
  }
  estudiante_carrera {
    uuid         id              PK
    uuid         perfil_id       UK
    uuid         carrera_id      UK
    uuid         anio_carrera_id FK
    boolean      es_principal
    smallint     iniciada_en
    timestamptz  cerrada_at
  }
  perfil_docente {
    uuid         id                 PK
    uuid         usuario_id         UK
    uuid         facultad_id        FK
    uuid         nivel_academico_id FK
    varchar      cargo
    timestamptz  actualizado_at
  }
  perfil_mentor {
    uuid         id                      PK
    uuid         usuario_id              UK
    uuid         tipo_mentor_id          FK
    uuid         nivel_academico_id      FK
    uuid         municipio_id            FK
    text         descripcion_profesional
    text         necesidades_formacion
    timestamptz  confirmado_at
    uuid         confirmado_por          FK
  }
  mentor_area_experiencia {
    uuid      id               PK
    uuid      perfil_mentor_id UK
    uuid      area_id          UK
    boolean   es_principal
  }
  mentor_certificacion {
    uuid      id               PK
    uuid      perfil_mentor_id FK
    varchar   nombre
    varchar   institucion
    smallint  anio
    varchar   enlace_url
  }

  facultad          ||--|{ carrera                 : ""
  facultad          ||--o{ perfil_docente          : ""
  carrera           ||--o{ estudiante_carrera      : ""
  institucion       ||--o{ perfil_estudiante       : ""
  institucion       ||--o| institucion             : "fusionada_en_id"
  perfil_estudiante ||--|{ estudiante_carrera      : ""
  perfil_mentor     ||--o{ mentor_area_experiencia : ""
  perfil_mentor     ||--o{ mentor_certificacion    : ""
```

---

## Índices únicos que sostienen invariantes

|              Índice               |                       Definición                        |              Invariante               |
| :-------------------------------: | :-----------------------------------------------------: | :-----------------------------------: |
| `unq_estudiantecarrera_principal` | `(perfil_id) WHERE es_principal AND cerrada_at IS NULL` |   Exactamente una carrera principal   |
|    `unq_mentorarea_principal`     |         `(perfil_mentor_id) WHERE es_principal`         |  Como máximo un área de especialidad  |
|   `unq_carrera_nombre_facultad`   |             `(facultad_id, lower(nombre))`              | Sin carreras repetidas en la facultad |

---

## Notas del nivel físico

**Los cuatro perfiles llevan `usuario_id` con unicidad**, no llave primaria
compartida. La diferencia es práctica: un `id` propio permite que
`mentor_certificacion` apunte al perfil y no al usuario, de modo que retirar el
perfil de mentor se lleve sus certificaciones sin tocar nada más.

**`estudiante_carrera` es la única relación de muchos a muchos del módulo**, y
existe por la doble titulación. Sin ella, `carrera_id` sería una columna de
`perfil_estudiante` y la pregunta _¿en qué carrera cuento a esta persona?_ tendría
una respuesta única y equivocada.

**`institucion` es el único catálogo con autorreferencia.** Es también el único
que admite altas desde un formulario de registro, y por eso necesita el mecanismo
de normalización: tres personas escribiendo el nombre de la misma universidad de
tres maneras producen tres filas, y `fusionada_en_id` las unifica después sin
perder lo que cada una declaró.

**`perfil_mentor.confirmado_at` no es un estado.** Es la marca que separa el
aspirante del mentor: el perfil existe desde que la persona lo solicita, con sus
áreas y certificaciones ya cargadas, pero no aparece como mentor disponible hasta
que la DIEM lo confirma.
