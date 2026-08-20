---
icon: lucide/clipboard-check
---

# Participación

Seis tablas. Las dos primeras son la razón de ser del sistema.

```mermaid
---
config:
  elk:
    nodePlacementStrategy: NETWORK_SIMPLEX
  fontFamily: monospace
  layout: elk
---
erDiagram
  direction LR
  inscripcion {
    uuid         id                PK
    uuid         usuario_id        UK
    uuid         actividad_id      UK
    uuid         estado_id         FK
    varchar      origen
    uuid         creada_por        FK
    smallint     posicion_espera   UK
    boolean      es_excepcion_cupo
    timestamptz  confirmada_at
    timestamptz  cerrada_at
    uuid         motivo_id         FK
  }
  participacion {
    uuid         id                PK
    uuid         usuario_id        UK
    uuid         actividad_id      UK
    uuid         inscripcion_id    UK
    smallint     anio
    uuid         rol_id            FK
    uuid         equipo_id         FK
    uuid         estado_id         FK
    date         fecha_inicio
    date         fecha_fin
    timestamptz  validada_at
    uuid         validada_por      FK
    varchar      enlace_evidencia
    timestamptz  anulada_at
    uuid         motivo_id         FK
    varchar      origen
  }
  participacion_evento {
    uuid         id                PK
    uuid         participacion_id  FK
    uuid         estado_desde_id   FK
    uuid         estado_hasta_id   FK
    timestamptz  ocurrido_at
    uuid         actor_id          FK
    varchar      actor_tipo
    jsonb        contexto
  }
  equipo {
    uuid         id            PK
    uuid         actividad_id  UK
    varchar      nombre        UK
    varchar      codigo_union  UK
    uuid         creado_por    FK
    timestamptz  congelado_at
  }
  equipo_miembro {
    uuid         id           PK
    uuid         equipo_id    UK
    uuid         usuario_id   UK
    boolean      es_lider
    timestamptz  retirado_at
  }
  reconocimiento {
    uuid         id                PK
    uuid         participacion_id  FK
    uuid         tipo_id           FK
    varchar      descripcion
    smallint     posicion
    date         otorgado_en
    timestamptz  anulado_at
  }

  inscripcion   ||--o| participacion        : ""
  participacion ||--|{ participacion_evento : ""
  participacion ||--o{ reconocimiento       : ""
  equipo        ||--|{ equipo_miembro       : ""
  equipo        ||--o{ participacion        : ""
```

---

## Los índices únicos parciales

|               Índice               |                                 Definición                                 |               Qué impide                |
| :--------------------------------: | :------------------------------------------------------------------------: | :-------------------------------------: |
|  `unq_inscripcion_persona_activa`  |           `(usuario_id, actividad_id) WHERE cerrada_at IS NULL`            |   Dos inscripciones vivas a lo mismo    |
| `unq_participacion_persona_activa` |           `(usuario_id, actividad_id) WHERE anulada_at IS NULL`            |     Contar dos veces a una persona      |
|  `unq_participacion_inscripcion`   | `(inscripcion_id) WHERE inscripcion_id IS NOT NULL AND anulada_at IS NULL` | Una inscripción con dos participaciones |
| `unq_inscripcion_posicion_espera`  |    `(actividad_id, posicion_espera) WHERE posicion_espera IS NOT NULL`     |      Empates en la lista de espera      |
|     `unq_equipomiembro_lider`      |            `(equipo_id) WHERE es_lider AND retirado_at IS NULL`            |            Dos líderes vivos            |

El primero es el que hace cumplir la regla bajo concurrencia. Una comprobación
previa en la aplicación dejaría pasar dos peticiones simultáneas del mismo
estudiante pulsando dos veces el botón, que es como se produce la mayoría de los
duplicados reales.

---

## Notas del nivel físico

**`participacion.inscripcion_id` es nulable**, y esa nulabilidad es la que hace
honesta la tabla. En una charla abierta la asistencia se recoge el mismo día;
forzar una inscripción sintética crearía inscripciones que nadie hizo.

**`participacion.anio` se copia de la actividad al crear la fila.** Es
denormalización deliberada: el índice de conteo anual sostiene el reporte más
pedido del sistema.

**Ninguna de las dos admite `DELETE`.** Un trigger `BEFORE DELETE` lo bloquea. La
corrección se hace por cierre o anulación con motivo, conservando el original.

**`equipo_miembro` no valida el tamaño mínimo por trigger.** Un equipo se
construye de uno en uno y el primer miembro siempre violaría el mínimo; se valida
al cerrar la inscripción, donde alguien decide si el equipo incompleto se disuelve
o se admite.
