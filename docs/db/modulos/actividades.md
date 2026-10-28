---
icon: lucide/calendar-days
---

# Actividades

Lo que la DIEM organiza. Tres tablas en la app `rudi_actividades`: el programa
recurrente, la edición concreta y sus responsables. Los mentores asignados a una
actividad viven en [`Participación`][asignacion], porque pueden acompañar a un
equipo concreto.

La separación entre programa y actividad es la decisión que ordena todo el
módulo, y está justificada en [`D-13`][d-13].

## Requerimientos cubiertos

- [`RF-A-15`][rf-a-15]
- [`RF-A-16`][rf-a-16]
- [`RF-A-17`][rf-a-17]
- [`RF-A-18`][rf-a-18]
- [`RF-A-19`][rf-a-19]
- [`RF-P-14`][rf-p-14]

---

## `programa`

Iniciativa recurrente que agrupa ediciones a lo largo de los años.

- **Régimen:** [Mutable rastreada][auditoria]
- **Volumen estimado:** 15-40 filas
- **Origen:**
  > - [`RF-A-15`][rf-a-15]

### Columnas

|        Campo        |      Tipo      | Nulo | Predeterminado |                     Descripción                     |
| :-----------------: | :------------: | :--: | :------------: | :-------------------------------------------------: |
|      `codigo`       | `varchar(50)`  |  no  |                |    Identificador estable: `hackathon_nicaragua`     |
|      `nombre`       | `varchar(200)` |  no  |                |                Denominación oficial                 |
|   `nombre_corto`    | `varchar(60)`  |  no  |      `''`      |               Para tablas y gráficos                |
|    `descripcion`    |     `text`     |  no  |      `''`      |                                                     |
| `tipo_actividad_id` |     `uuid`     |  sí  |                |          Tipo por defecto de sus ediciones          |
| `is_institucional`  |   `boolean`    |  no  |     `true`     | Falso en programas de terceros que la DIEM acompaña |
|     `is_active`     |   `boolean`    |  no  |     `true`     |       Falso = ya no se crean ediciones nuevas       |

### Unicidad

|        Nombre         |         Definición          |
| :-------------------: | :-------------------------: |
| `unq_programa_codigo` |         `(codigo)`          |
| `unq_programa_nombre` | `(upper(unaccent(nombre)))` |

### Triggers

|             Nombre             |       Evento       | Momento  | Nivel |                Regla                 |        Origen         |
| :----------------------------: | :----------------: | :------: | :---: | :----------------------------------: | :-------------------: |
|     `trg_readonly_codigo`      | `UPDATE OF codigo` | `BEFORE` | `ROW` | Rechaza cualquier cambio de `codigo` |    [`D-08`][d-08]     |
| `trg_programa_catalogo_activo` |      `INSERT`      | `BEFORE` | `ROW` |  `tipo_actividad` debe estar activo  | [Familia][t-catalogo] |

### Notas de diseño

Desactivar un programa no lo retira de los reportes: retira la posibilidad de
crearle ediciones nuevas. El Rally Latinoamericano puede dejar de organizarse y
sus tres ediciones anteriores siguen contando en la participación histórica.

`is_institucional` distingue lo que la DIEM organiza de lo que acompaña. La
distinción importa en los reportes de gestión, donde no es lo mismo haber
organizado veinte actividades que haber participado en veinte.

---

## `actividad`

Edición concreta con fechas, cupo y ventana de inscripción. Es la unidad con la
que se relacionan inscripciones, participaciones y mentores.

- **Régimen:** [Mutable protegida][auditoria], rastreada
- **Volumen estimado:** 100-500 filas
- **Origen:**
  > - [`RF-A-16`][rf-a-16]
  > - [`RF-A-17`][rf-a-17]
  > - [`RF-A-18`][rf-a-18]

### Columnas

|          Campo          |      Tipo      | Nulo | Predeterminado |                     Descripción                      |
| :---------------------: | :------------: | :--: | :------------: | :--------------------------------------------------: |
|      `programa_id`      |     `uuid`     |  sí  |                |       Nulo en actividades únicas sin programa        |
|        `nombre`         | `varchar(200)` |  no  |                |                                                      |
|   `etiqueta_edicion`    | `varchar(60)`  |  no  |      `''`      | `Edición 2025`, `I Cohorte 2026`, `II semestre 2025` |
|      `descripcion`      |     `text`     |  no  |      `''`      |                                                      |
|   `tipo_actividad_id`   |     `uuid`     |  no  |                |           Llave foránea a `tipo_actividad`           |
|       `modalidad`       | `varchar(20)`  |  no  | `'presencial'` |         `presencial` / `virtual` / `hibrida`         |
|         `lugar`         | `varchar(200)` |  no  |      `''`      |              Vacío en modalidad virtual              |
|         `anio`          |   `smallint`   |  no  |                |          Año de reporte, por [`D-14`][d-14]          |
|     `fecha_inicio`      |     `date`     |  no  |                |                                                      |
|       `fecha_fin`       |     `date`     |  sí  |                |             Nula mientras no se conozca              |
|  `inscripcion_abre_at`  | `timestamptz`  |  sí  |                |            Nula = sin inscripción previa             |
| `inscripcion_cierra_at` | `timestamptz`  |  sí  |                |                                                      |
|         `cupo`          |   `smallint`   |  sí  |                |                  Nulo = sin límite                   |
|   `inscritos_activos`   |   `smallint`   |  no  |      `0`       |            Contador mantenido por trigger            |
|  `admite_lista_espera`  |   `boolean`    |  no  |     `true`     |                                                      |
|    `admite_equipos`     |   `boolean`    |  no  |    `false`     |                                                      |
|      `equipo_min`       |   `smallint`   |  sí  |                |                                                      |
|      `equipo_max`       |   `smallint`   |  sí  |                |                                                      |
|      `puntos_base`      |   `smallint`   |  sí  |                |   Prevalece sobre el baremo general si tiene valor   |
|       `estado_id`       |     `uuid`     |  no  |                |          Llave foránea a `estado_actividad`          |
|     `publicada_at`      | `timestamptz`  |  sí  |                |                                                      |
|     `cancelada_at`      | `timestamptz`  |  sí  |                |                   Marca de cierre                    |
|       `motivo_id`       |     `uuid`     |  sí  |                |               Obligatorio al cancelar                |
|  `motivo_descripcion`   |     `text`     |  no  |      `''`      |  Exigida si el motivo declara `require_descripcion`  |
|   `enlace_evidencia`    | `varchar(500)` |  no  |      `''`      |         Carpeta o expediente de la actividad         |

### Llaves foráneas

|       Columna       |     Referencia     | `ON DELETE` |               Notas               |
| :-----------------: | :----------------: | :---------: | :-------------------------------: |
|    `programa_id`    |     `programa`     | `RESTRICT`  |                                   |
| `tipo_actividad_id` |  `tipo_actividad`  | `RESTRICT`  |                                   |
|     `estado_id`     | `estado_actividad` | `RESTRICT`  |                                   |
|     `motivo_id`     |      `motivo`      | `RESTRICT`  | De ámbito `cancelacion_actividad` |

### Constraints

```postgresql
CONSTRAINT chk_actividad_modalidad
CHECK (modalidad IN ('hibrida', 'presencial', 'virtual'))

CONSTRAINT chk_actividad_lugar_virtual
CHECK (modalidad <> 'virtual' OR lugar = '')

CONSTRAINT chk_actividad_anio
CHECK (anio BETWEEN 2000 AND 2100)

CONSTRAINT chk_actividad_fechas
CHECK (fecha_fin IS NULL OR fecha_fin >= fecha_inicio)

CONSTRAINT chk_actividad_ventana
CHECK (
  inscripcion_abre_at IS NULL
  OR inscripcion_cierra_at IS NULL
  OR inscripcion_cierra_at > inscripcion_abre_at
)

CONSTRAINT chk_actividad_cupo_positivo
CHECK (cupo IS NULL OR cupo > 0)

CONSTRAINT chk_actividad_cupo_coherente
CHECK (cupo IS NULL OR inscritos_activos <= cupo)

CONSTRAINT chk_actividad_equipos_coherente
CHECK (admite_equipos OR (equipo_min IS NULL AND equipo_max IS NULL))

CONSTRAINT chk_actividad_equipo_rango
CHECK (equipo_min IS NULL OR equipo_max IS NULL OR equipo_min <= equipo_max)

CONSTRAINT chk_actividad_cancelacion
CHECK ((cancelada_at IS NULL) = (motivo_id IS NULL))
```

### Unicidad

|              Nombre              |                               Definición                               |                  Propósito                  |
| :------------------------------: | :--------------------------------------------------------------------: | :-----------------------------------------: |
| `unq_actividad_programa_edicion` | `(programa_id, lower(etiqueta_edicion)) WHERE programa_id IS NOT NULL` | No hay dos ediciones iguales de un programa |

### Triggers

|                 Nombre                 |               Evento               | Momento  | Nivel |                                Regla                                 |        Origen         |
| :------------------------------------: | :--------------------------------: | :------: | :---: | :------------------------------------------------------------------: | :-------------------: |
|     `trg_actividad_estado_activo`      |       `INSERT`<br/>`UPDATE`        | `BEFORE` | `ROW` |                 El estado asignado debe estar activo                 |  [Familia][t-estado]  |
|    `trg_actividad_estado_terminal`     |   `UPDATE` con cambio de estado    | `BEFORE` | `ROW` |                  Una actividad cerrada no se reabre                  |  [Familia][t-estado]  |
|   `trg_actividad_transicion_valida`    |   `UPDATE` con cambio de estado    | `BEFORE` | `ROW` |   El par debe estar en `transicion_estado_actividad` para el actor   | [`RF-A-17`][rf-a-17]  |
|    `trg_actividad_estado_coherente`    | `INSERT`<br/>`UPDATE OF estado_id` | `BEFORE` | `ROW` |  Al entrar en un estado `public`, fija `publicada_at` si está vacía  | [`RF-A-17`][rf-a-17]  |
|         `trg_actividad_motivo`         |       `INSERT`<br/>`UPDATE`        | `BEFORE` | `ROW` |               El motivo es de `cancelacion_actividad`                |  [Familia][t-motivo]  |
|    `trg_actividad_catalogo_activo`     |              `INSERT`              | `BEFORE` | `ROW` |                `tipo_actividad` y `programa` activos                 | [Familia][t-catalogo] |
|  `trg_actividad_publicacion_completa`  |       `UPDATE OF estado_id`        | `BEFORE` | `ROW` | Al pasar a un estado `public`, exige al menos un responsable vigente | [`RF-A-16`][rf-a-16]  |
|    `trg_actividad_promover_espera`     |          `UPDATE OF cupo`          | `AFTER`  | `ROW` |    Al ampliar el cupo, promueve desde la lista de espera en orden    | [`RF-P-18`][rf-p-18]  |
| `trg_actividad_cancelar_inscripciones` |      `UPDATE OF cancelada_at`      | `AFTER`  | `ROW` |  Al cancelarse, cierra las inscripciones vivas con el mismo motivo   | [`RF-A-17`][rf-a-17]  |

Los dos últimos escriben en `inscripcion`, así que se declaran en
`rudi_participacion` y se registran sobre `Actividad`
([Efecto en otra tabla][t-efecto]).

### Índices

|             Nombre             |                      Definición                      |                Propósito                 |
| :----------------------------: | :--------------------------------------------------: | :--------------------------------------: |
|    `idx_actividad_catalogo`    |   `(fecha_inicio DESC) WHERE cancelada_at IS NULL`   | Catálogo público de [`RF-P-14`][rf-p-14] |
| `idx_actividad_programa_anio`  |                `(programa_id, anio)`                 |       Reportes por programa y año        |
| `idx_actividad_ventana_cierre` | `(inscripcion_cierra_at) WHERE cancelada_at IS NULL` |       Barrido de cierre de ventana       |
|   `idx_actividad_anio_tipo`    |             `(anio, tipo_actividad_id)`              |   Segmentación de [`RF-A-42`][rf-a-42]   |

### Notas de diseño

`inscritos_activos` es el único contador denormalizado del modelo. Existe porque
`CHECK` no puede contar filas de otra tabla y el invariante de cupo tiene que ser
estructural: es el que compite bajo concurrencia real, con decenas de personas
pulsando el botón sobre los últimos lugares de un hackathon. Lo mantiene
`trg_inscripcion_contador` ([Contadores][t-contador]). Reducir el cupo por
debajo de los inscritos no necesita trigger: lo rechaza el mismo
`chk_actividad_cupo_coherente`.

`anio` es columna propia y no `EXTRACT(year FROM fecha_inicio)` por
[`D-14`][d-14]. La edición del Rally que arranca en noviembre y cierra en febrero
se reporta entera en el año que la DIEM decida.

`etiqueta_edicion` es texto y no llave foránea a un catálogo de ediciones. Las
etiquetas reales de la matriz —`Edición 2024`, `I Cohorte 2026`, `II semestre
2025`— no comparten estructura, y la agrupación por año y por programa, que es lo
que los reportes necesitan, ya la dan `anio` y `programa_id`.

---

## `actividad_responsable`

- **Régimen:** [Mutable protegida][auditoria], rastreada
- **Volumen estimado:** 200-1,000 filas
- **Origen:**
  > - [`RF-A-19`][rf-a-19]

### Columnas

|     Campo      |     Tipo      | Nulo | Predeterminado |                       Descripción                       |
| :------------: | :-----------: | :--: | :------------: | :-----------------------------------------------------: |
| `actividad_id` |    `uuid`     |  no  |                |                      Llave foránea                      |
|   `user_id`    |    `uuid`     |  no  |                |                   Persona responsable                   |
|     `rol`      | `varchar(30)` |  no  |                | `coordinacion` / `facilitacion` / `logistica` / `apoyo` |
|  `is_public`   |   `boolean`   |  no  |     `true`     |       Aparece en la ficha pública de la actividad       |
| `retirado_at`  | `timestamptz` |  sí  |                |                     Marca de cierre                     |

### Unicidad

|               Nombre               |                     Definición                      |
| :--------------------------------: | :-------------------------------------------------: |
| `unq_actividadresponsable_vigente` | `(actividad_id, user_id) WHERE retirado_at IS NULL` |

Una persona cumple un solo rol de responsabilidad por actividad. Si coordina y
facilita, se registra el mayor.

[asignacion]: participacion.md#asignacion_mentor
[auditoria]: ../convenciones.md#auditoria-por-tabla
[t-catalogo]: ../triggers.md#catalogo-activo
[t-contador]: ../triggers.md#contadores-denormalizados
[t-efecto]: ../triggers.md#efecto-en-otra-tabla
[t-estado]: ../triggers.md#ciclo-de-vida-del-estado
[t-motivo]: ../triggers.md#motivo-de-lista-cerrada
[d-08]: ../decisiones.md#d-08
[d-13]: ../decisiones.md#d-13
[d-14]: ../decisiones.md#d-14
[rf-a-15]: ../../requerimientos/funcionales/administracion.md#rf-a-15
[rf-a-16]: ../../requerimientos/funcionales/administracion.md#rf-a-16
[rf-a-17]: ../../requerimientos/funcionales/administracion.md#rf-a-17
[rf-a-18]: ../../requerimientos/funcionales/administracion.md#rf-a-18
[rf-a-19]: ../../requerimientos/funcionales/administracion.md#rf-a-19
[rf-a-42]: ../../requerimientos/funcionales/administracion.md#rf-a-42
[rf-p-14]: ../../requerimientos/funcionales/participantes.md#rf-p-14
[rf-p-18]: ../../requerimientos/funcionales/participantes.md#rf-p-18
