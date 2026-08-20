---
icon: lucide/calendar-days
---

# Actividades

Lo que la DIEM organiza. Cuatro tablas: el programa recurrente, la edición
concreta, sus responsables y los mentores asignados.

La separación entre programa y actividad es la decisión que ordena todo el
módulo, y está justificada en [`D-13`][d-13].

## Requerimientos cubiertos

- [`RF-A-15`][rf-a-15]
- [`RF-A-16`][rf-a-16]
- [`RF-A-17`][rf-a-17]
- [`RF-A-18`][rf-a-18]
- [`RF-A-19`][rf-a-19]
- [`RF-A-20`][rf-a-20]
- [`RF-P-14`][rf-p-14]
- [`RF-P-27`][rf-p-27]

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
| `es_institucional`  |   `boolean`    |  no  |     `true`     | Falso en programas de terceros que la DIEM acompaña |
|      `activo`       |   `boolean`    |  no  |     `true`     |       Falso = ya no se crean ediciones nuevas       |

### Unicidad

|        Nombre         |    Definición     |
| :-------------------: | :---------------: |
| `unq_programa_codigo` |    `(codigo)`     |
| `unq_programa_nombre` | `(lower(nombre))` |

### Notas de diseño

`activo` en falso no retira el programa de los reportes: retira la posibilidad de
crearle ediciones nuevas. El Rally Latinoamericano puede dejar de organizarse y
sus tres ediciones anteriores siguen contando en la participación histórica.

`es_institucional` distingue lo que la DIEM organiza de lo que acompaña. El Rally
Latinoamericano lo convoca una red externa y la UAM participa; el Programa PIA es
propio. La distinción importa en los reportes de gestión, donde no es lo mismo
haber organizado veinte actividades que haber participado en veinte.

---

## `actividad`

Edición concreta con fechas, cupo y ventana de inscripción. Es la unidad con la
que se relacionan inscripciones, participaciones y mentores.

- **Régimen:** [Mutable rastreada][auditoria]
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
CHECK (modalidad IN ('presencial', 'virtual', 'hibrida'))

CONSTRAINT chk_actividad_fechas
CHECK (fecha_fin IS NULL OR fecha_fin >= fecha_inicio)

CONSTRAINT chk_actividad_ventana
CHECK (
  inscripcion_abre_at IS NULL
  OR
  inscripcion_cierra_at IS NULL
  OR
  inscripcion_cierra_at > inscripcion_abre_at
)

CONSTRAINT chk_actividad_cupo_positivo
CHECK (cupo IS NULL OR cupo > 0)

CONSTRAINT chk_actividad_cupo_coherente
CHECK (cupo IS NULL OR inscritos_activos <= cupo)

CONSTRAINT chk_actividad_equipos_coherente
CHECK (
  admite_equipos
  OR
  (equipo_min IS NULL AND equipo_max IS NULL)
)

CONSTRAINT chk_actividad_equipo_rango
CHECK (
  equipo_min IS NULL
  OR
  equipo_max IS NULL
  OR
  equipo_min <= equipo_max
)

CONSTRAINT chk_actividad_cancelacion
CHECK ((cancelada_at IS NULL) = (motivo_id IS NULL))

CONSTRAINT chk_actividad_anio
CHECK (anio BETWEEN 2000 AND 2100)
```

### Unicidad

|              Nombre              |                               Definición                               |                  Propósito                  |
| :------------------------------: | :--------------------------------------------------------------------: | :-----------------------------------------: |
| `unq_actividad_programa_edicion` | `(programa_id, lower(etiqueta_edicion)) WHERE programa_id IS NOT NULL` | No hay dos ediciones iguales de un programa |

### Triggers

|                 Nombre                 |             Evento              | Momento  | Nivel |                                          Regla                                           |        Origen        |
| :------------------------------------: | :-----------------------------: | :------: | :---: | :--------------------------------------------------------------------------------------: | :------------------: |
|    `trg_actividad_estado_coherente`    | `INSERT`, `UPDATE OF estado_id` | `BEFORE` | `ROW` | Verifica la transición contra `transicion_actividad` y la correspondencia con las marcas | [`RF-A-17`][rf-a-17] |
|     `trg_actividad_cupo_no_reduce`     |        `UPDATE OF cupo`         | `BEFORE` | `ROW` |                Rechaza reducir el cupo por debajo de `inscritos_activos`                 | [`RF-A-18`][rf-a-18] |
|    `trg_actividad_promover_espera`     |        `UPDATE OF cupo`         | `AFTER`  | `ROW` |              Al ampliar el cupo, promueve desde la lista de espera en orden              | [`RF-P-18`][rf-p-18] |
| `trg_actividad_cancelar_inscripciones` |      `UPDATE OF estado_id`      | `AFTER`  | `ROW` |            Al pasar a cancelada, cierra las inscripciones vivas con el motivo            | [`RF-A-17`][rf-a-17] |
|  `trg_actividad_publicacion_completa`  |      `UPDATE OF estado_id`      | `BEFORE` | `ROW` |        Al publicar, exige nombre, tipo, fecha de inicio y al menos un responsable        | [`RF-A-16`][rf-a-16] |

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
pulsando el botón sobre los últimos lugares de un hackathon.

El trigger que lo mantiene se ejecuta dentro de la misma transacción que crea la
inscripción, de modo que el `CHECK` se evalúa con el valor ya incrementado y el
sobrecupo falla como error de transacción. Sin el contador haría falta
`SELECT ... FOR UPDATE` sobre la actividad en cada inscripción, que es lo mismo
pero explícito en cada consulta y olvidable en una de ellas.

`anio` es columna propia y no `EXTRACT(year FROM fecha_inicio)` por
[`D-14`][d-14]. La edición del Rally que arranca en noviembre y cierra en febrero
se reporta entera en el año que la DIEM decida.

`etiqueta_edicion` es texto y no llave foránea a un catálogo de ediciones. Las
etiquetas reales de la matriz —`Edición 2024`, `I Cohorte 2026`, `II semestre
2025`, `Sin edición / No aplica`— no comparten estructura, y un catálogo de todas
las combinaciones posibles sería más largo que la tabla de actividades. La
agrupación por año y por programa, que es lo que los reportes necesitan, ya la
dan `anio` y `programa_id`.

---

## `actividad_responsable`

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 200-1,000 filas
- **Origen:**
  > - [`RF-A-19`][rf-a-19]

### Columnas

|       Campo       |     Tipo      | Nulo | Predeterminado |                 Descripción                 |
| :---------------: | :-----------: | :--: | :------------: | :-----------------------------------------: |
|  `actividad_id`   |    `uuid`     |  no  |                |                Llave foránea                |
|   `usuario_id`    |    `uuid`     |  no  |                |                Llave foránea                |
|       `rol`       | `varchar(30)` |  no  |                |                 Ver `CHECK`                 |
| `visible_publico` |   `boolean`   |  no  |     `true`     | Aparece en la ficha pública de la actividad |
|   `retirado_at`   | `timestamptz` |  sí  |                |               Marca de cierre               |

### Constraints

```postgresql
CONSTRAINT chk_actividadresponsable_rol
CHECK (rol IN ('coordinacion', 'facilitacion', 'logistica', 'apoyo'))
```

### Unicidad

|               Nombre               |                       Definición                       |
| :--------------------------------: | :----------------------------------------------------: |
| `unq_actividadresponsable_vigente` | `(actividad_id, usuario_id) WHERE retirado_at IS NULL` |

Una persona cumple un solo rol de responsabilidad por actividad. Si coordina y
facilita, se registra el mayor.

---

## `asignacion_mentor`

Vínculo de un mentor con una actividad, con su propio ciclo de vida. Implementa
[`RN-12`][rn-12].

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 200-1,200 filas
- **Origen:**
  > - [`RF-A-20`][rf-a-20]
  > - [`RF-P-27`][rf-p-27]
  > - [`RF-P-29`][rf-p-29]

### Columnas

|         Campo         |      Tipo      | Nulo | Predeterminado |                Descripción                 |
| :-------------------: | :------------: | :--: | :------------: | :----------------------------------------: |
|    `actividad_id`     |     `uuid`     |  no  |                |               Llave foránea                |
|  `perfil_mentor_id`   |     `uuid`     |  no  |                |      Llave foránea a `perfil_mentor`       |
|      `equipo_id`      |     `uuid`     |  sí  |                | Con valor si acompaña a un equipo concreto |
| `tipo_acompanamiento` | `varchar(30)`  |  no  |                |                Ver `CHECK`                 |
|      `estado_id`      |     `uuid`     |  no  |                | Llave foránea a `estado_asignacion_mentor` |
|    `propuesta_at`     | `timestamptz`  |  no  |    `now()`     |                                            |
|    `respondida_at`    | `timestamptz`  |  sí  |                |      Instante en que aceptó o declinó      |
|      `motivo_id`      |     `uuid`     |  sí  |                |          Obligatorio al declinar           |
|    `finalizada_at`    | `timestamptz`  |  sí  |                |              Marca de cierre               |
|    `observaciones`    |     `text`     |  no  |      `''`      |  Aporte que el mentor registra al cerrar   |
|  `enlace_evidencia`   | `varchar(500)` |  no  |      `''`      |                                            |

### Llaves foráneas

|      Columna       |         Referencia         | `ON DELETE` |              Notas               |
| :----------------: | :------------------------: | :---------: | :------------------------------: |
|   `actividad_id`   |        `actividad`         | `RESTRICT`  |                                  |
| `perfil_mentor_id` |      `perfil_mentor`       | `RESTRICT`  |                                  |
|    `equipo_id`     |          `equipo`          | `RESTRICT`  |                                  |
|    `estado_id`     | `estado_asignacion_mentor` | `RESTRICT`  |                                  |
|    `motivo_id`     |          `motivo`          | `RESTRICT`  | De ámbito `declinacion_mentoria` |

### Constraints

```postgresql
CONSTRAINT chk_asignacionmentor_tipo
CHECK (
  tipo_acompanamiento IN (
    'mentoria_tecnica',
    'mentoria_negocio',
    'jurado',
    'facilitacion',
    'charla',
    'otro'
  )
)

CONSTRAINT chk_asignacionmentor_respuesta
CHECK (respondida_at IS NULL OR respondida_at >= propuesta_at)
```

### Unicidad

|             Nombre             |                                Definición                                 |            Propósito             |
| :----------------------------: | :-----------------------------------------------------------------------: | :------------------------------: |
| `unq_asignacionmentor_vigente` | `(actividad_id, perfil_mentor_id, equipo_id) WHERE finalizada_at IS NULL` | No se propone dos veces lo mismo |

### Triggers

|                  Nombre                  |             Evento              | Momento  | Nivel |                                 Regla                                 |        Origen        |
| :--------------------------------------: | :-----------------------------: | :------: | :---: | :-------------------------------------------------------------------: | :------------------: |
| `trg_asignacionmentor_mentor_confirmado` |            `INSERT`             | `BEFORE` | `ROW` |       Rechaza asignar a un perfil de mentor sin `confirmado_at`       | [`RF-P-12`][rf-p-12] |
| `trg_asignacionmentor_equipo_coherente`  | `INSERT`, `UPDATE OF equipo_id` | `BEFORE` | `ROW` |          Exige que el equipo pertenezca a la misma actividad          |   [`RN-12`][rn-12]   |
| `trg_asignacionmentor_estado_coherente`  | `INSERT`, `UPDATE OF estado_id` | `BEFORE` | `ROW` | Exige `motivo_id` al declinar y `respondida_at` al aceptar o declinar | [`RF-P-27`][rf-p-27] |

### Índices

|              Nombre              |                               Definición                               |              Propósito               |
| :------------------------------: | :--------------------------------------------------------------------: | :----------------------------------: |
|  `idx_asignacionmentor_mentor`   |                `(perfil_mentor_id, propuesta_at DESC)`                 |    Agenda de [`RF-P-28`][rf-p-28]    |
| `idx_asignacionmentor_pendiente` | `(propuesta_at) WHERE respondida_at IS NULL AND finalizada_at IS NULL` | Barrido de vencimiento de propuestas |

### Notas de diseño

`equipo_id` nulable distingue los dos modos de acompañamiento reales: el mentor
que acompaña a un equipo concreto durante un hackathon y el que da una charla a
toda la actividad. Ambos constan y ambos generan participación al validarse.

La asignación no se autoconfirma por silencio. Una propuesta sin respuesta
permanece como propuesta y el proceso programado la marca como vencida, porque
publicar como mentor confirmado a alguien que nunca aceptó es una afirmación
institucional falsa sobre una persona.

El listado de mentores de la DIEM tiene hoy una columna por actividad con una
marca. Esas cuatro columnas se convierten en filas de esta tabla, una por
actividad acompañada, lo que permite añadir la quinta actividad sin alterar la
estructura.

[auditoria]: ../convenciones.md#auditoria-por-tabla
[d-13]: ../decisiones.md#d-13
[d-14]: ../decisiones.md#d-14
[rf-a-15]: ../../requerimientos/funcionales/administracion.md#rf-a-15
[rf-a-16]: ../../requerimientos/funcionales/administracion.md#rf-a-16
[rf-a-17]: ../../requerimientos/funcionales/administracion.md#rf-a-17
[rf-a-18]: ../../requerimientos/funcionales/administracion.md#rf-a-18
[rf-a-19]: ../../requerimientos/funcionales/administracion.md#rf-a-19
[rf-a-20]: ../../requerimientos/funcionales/administracion.md#rf-a-20
[rf-a-42]: ../../requerimientos/funcionales/administracion.md#rf-a-42
[rf-p-12]: ../../requerimientos/funcionales/participantes.md#rf-p-12
[rf-p-14]: ../../requerimientos/funcionales/participantes.md#rf-p-14
[rf-p-18]: ../../requerimientos/funcionales/participantes.md#rf-p-18
[rf-p-27]: ../../requerimientos/funcionales/participantes.md#rf-p-27
[rf-p-28]: ../../requerimientos/funcionales/participantes.md#rf-p-28
[rf-p-29]: ../../requerimientos/funcionales/participantes.md#rf-p-29
[rn-12]: ../../requerimientos/reglas-negocio.md#rn-12
