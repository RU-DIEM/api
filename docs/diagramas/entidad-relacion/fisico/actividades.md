---
icon: lucide/calendar-days
---

# Actividades

Cuatro tablas. `actividad` es la más ancha del modelo y la que más triggers
lleva.

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
  programa {
    uuid      id                PK
    varchar   codigo            UK
    varchar   nombre            UK
    varchar   nombre_corto
    uuid      tipo_actividad_id FK
    boolean   es_institucional
    boolean   activo
  }
  actividad {
    uuid         id                    PK
    uuid         programa_id           FK
    varchar      nombre
    varchar      etiqueta_edicion      UK
    uuid         tipo_actividad_id     FK
    varchar      modalidad
    varchar      lugar
    smallint     anio
    date         fecha_inicio
    date         fecha_fin
    timestamptz  inscripcion_abre_at
    timestamptz  inscripcion_cierra_at
    smallint     cupo
    smallint     inscritos_activos
    boolean      admite_lista_espera
    boolean      admite_equipos
    smallint     equipo_min
    smallint     equipo_max
    smallint     puntos_base
    uuid         estado_id             FK
    timestamptz  publicada_at
    timestamptz  cancelada_at
    uuid         motivo_id             FK
  }
  actividad_responsable {
    uuid         id              PK
    uuid         actividad_id    UK
    uuid         usuario_id      UK
    varchar      rol
    boolean      visible_publico
    timestamptz  retirado_at
  }
  asignacion_mentor {
    uuid         id                  PK
    uuid         actividad_id        UK
    uuid         perfil_mentor_id    UK
    uuid         equipo_id           UK
    varchar      tipo_acompanamiento
    uuid         estado_id           FK
    timestamptz  propuesta_at
    timestamptz  respondida_at
    uuid         motivo_id           FK
    timestamptz  finalizada_at
    text         observaciones
  }

  programa      ||--o{ actividad             : ""
  actividad     ||--|{ actividad_responsable : ""
  actividad     ||--o{ asignacion_mentor     : ""
```

---

## El invariante del cupo

```postgresql
CONSTRAINT chk_actividad_cupo_coherente
CHECK (cupo IS NULL OR inscritos_activos <= cupo)
```

`inscritos_activos` es el **único contador denormalizado del modelo**. Existe
porque `CHECK` no puede contar filas de otra tabla y el invariante tiene que ser
estructural: es el que compite bajo concurrencia real, con decenas de personas
pulsando el botón sobre los últimos lugares de un hackathon.

El trigger que lo mantiene vive en `inscripcion` y se ejecuta dentro de la misma
transacción, de modo que el `CHECK` se evalúa con el valor ya incrementado y el
sobrecupo falla como error de transacción.

---

## Notas del nivel físico

**`programa_id` es nulable.** Una charla única no es la edición de nada. Forzarla
a pertenecer a un programa crearía programas de un solo elemento.

**`anio` es columna propia y no `EXTRACT(year FROM fecha_inicio)`.** La edición
del Rally que arranca en noviembre y cierra en febrero se reporta entera en el año
que la DIEM decida, y el índice de conteo anual necesita una columna real.

**`etiqueta_edicion` es `varchar` y no llave foránea.** Las etiquetas reales de la
matriz —`Edición 2024`, `I Cohorte 2026`, `II semestre 2025`— no comparten
estructura, y un catálogo de todas las combinaciones sería más largo que la tabla
de actividades.

**`asignacion_mentor.equipo_id` es nulable y forma parte de la unicidad.**
Distingue al mentor que acompaña a un equipo concreto del que da una charla a toda
la actividad, y permite que el mismo mentor acompañe a dos equipos distintos de la
misma actividad sin colisionar.
