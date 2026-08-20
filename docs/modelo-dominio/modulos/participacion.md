---
icon: lucide/clipboard-check
---

# Inscripción y participación

Las dos tablas cuya separación motiva el proyecto entero, más los equipos, los
reconocimientos y el historial de transiciones.

Contar inscripciones y llamarlas participantes es el error que la DIEM quiere
dejar de cometer. Aquí ese error deja de ser posible: son dos tablas, con dos
volúmenes distintos y dos significados distintos, y ninguna consulta puede
confundirlas sin decirlo.

## Requerimientos cubiertos

- [`RF-P-16`][rf-p-16]
- [`RF-P-17`][rf-p-17]
- [`RF-P-18`][rf-p-18]
- [`RF-P-19`][rf-p-19]
- [`RF-P-20`][rf-p-20]
- [`RF-P-21`][rf-p-21]
- [`RF-A-22`][rf-a-22]
- [`RF-A-23`][rf-a-23]
- [`RF-A-24`][rf-a-24]
- [`RF-A-25`][rf-a-25]
- [`RF-A-26`][rf-a-26]
- [`RF-A-27`][rf-a-27]
- [`RF-A-28`][rf-a-28]
- [`RF-A-29`][rf-a-29]

---

## `inscripcion`

Intención de participar. No prueba nada por sí sola.

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 3,000-20,000 filas
- **Origen:**
  > - [`RF-P-16`][rf-p-16]
  > - [`RF-A-22`][rf-a-22]

### Columnas

|        Campo        |     Tipo      | Nulo |  Predeterminado  |                    Descripción                    |
| :-----------------: | :-----------: | :--: | :--------------: | :-----------------------------------------------: |
|    `usuario_id`     |    `uuid`     |  no  |                  |                   Llave foránea                   |
|   `actividad_id`    |    `uuid`     |  no  |                  |                   Llave foránea                   |
|     `estado_id`     |    `uuid`     |  no  |                  |       Llave foránea a `estado_inscripcion`        |
|      `origen`       | `varchar(20)` |  no  | `'autoservicio'` | `autoservicio` / `administracion` / `importacion` |
|    `creada_por`     |    `uuid`     |  sí  |                  |   Con valor solo si el origen es administrativo   |
|  `posicion_espera`  |  `smallint`   |  sí  |                  |  Con valor solo mientras está en lista de espera  |
| `es_excepcion_cupo` |   `boolean`   |  no  |     `false`      |     Inscripción admitida por encima del cupo      |
|   `confirmada_at`   | `timestamptz` |  sí  |                  |                                                   |
|    `cerrada_at`     | `timestamptz` |  sí  |                  |      Marca de cierre: cancelada o rechazada       |
|     `motivo_id`     |    `uuid`     |  sí  |                  |               Obligatorio al cerrar               |

### Llaves foráneas

|    Columna     |      Referencia      | `ON DELETE` |                        Notas                        |
| :------------: | :------------------: | :---------: | :-------------------------------------------------: |
|  `usuario_id`  |      `usuario`       | `RESTRICT`  |            La fusión traslada, no borra             |
| `actividad_id` |     `actividad`      | `RESTRICT`  |                                                     |
|  `estado_id`   | `estado_inscripcion` | `RESTRICT`  |                                                     |
|  `creada_por`  |      `usuario`       | `RESTRICT`  | La bitácora debe seguir nombrando a quien inscribió |
|  `motivo_id`   |       `motivo`       | `RESTRICT`  |         De ámbito `cancelacion_inscripcion`         |

### Constraints

```postgresql
CONSTRAINT chk_inscripcion_origen
CHECK (origen IN ('autoservicio', 'administracion', 'importacion'))

CONSTRAINT chk_inscripcion_creador
CHECK ((origen = 'administracion') = (creada_por IS NOT NULL))

CONSTRAINT chk_inscripcion_cierre
CHECK ((cerrada_at IS NULL) = (motivo_id IS NULL))

CONSTRAINT chk_inscripcion_espera_positiva
CHECK (posicion_espera IS NULL OR posicion_espera > 0)
```

### Unicidad

|              Nombre               |                             Definición                              |       Propósito        |
| :-------------------------------: | :-----------------------------------------------------------------: | :--------------------: |
| `unq_inscripcion_persona_activa`  |        `(usuario_id, actividad_id) WHERE cerrada_at IS NULL`        |    [`RN-05`][rn-05]    |
| `unq_inscripcion_posicion_espera` | `(actividad_id, posicion_espera) WHERE posicion_espera IS NOT NULL` | Sin empates en la fila |

### Triggers

|               Nombre               |             Evento              | Momento  | Nivel |                                      Regla                                       |        Origen        |
| :--------------------------------: | :-----------------------------: | :------: | :---: | :------------------------------------------------------------------------------: | :------------------: |
| `trg_inscripcion_ventana_abierta`  |            `INSERT`             | `BEFORE` | `ROW` |             Rechaza fuera de la ventana, salvo origen administrativo             | [`RF-P-16`][rf-p-16] |
|     `trg_inscripcion_contador`     | `INSERT`, `UPDATE OF estado_id` | `AFTER`  | `ROW` |  Ajusta `actividad.inscritos_activos` según el atributo `ocupa_cupo` del estado  |   [`RN-11`][rn-11]   |
| `trg_inscripcion_estado_coherente` | `INSERT`, `UPDATE OF estado_id` | `BEFORE` | `ROW` | Verifica la transición contra `transicion_inscripcion` y el actor que la ejecuta |    [`D-10`][d-10]    |
| `trg_inscripcion_promover_espera`  |     `UPDATE OF cerrada_at`      | `AFTER`  | `ROW` |  Al liberarse un lugar, promueve al primero de la lista y recalcula posiciones   | [`RF-P-18`][rf-p-18] |
| `trg_inscripcion_cierre_bloqueado` |     `UPDATE OF cerrada_at`      | `BEFORE` | `ROW` |             Rechaza cerrar si existe participación validada asociada             | [`RF-P-19`][rf-p-19] |
|    `trg_inscripcion_no_borrar`     |            `DELETE`             | `BEFORE` | `ROW` |                                Bloquea el borrado                                | [`RF-A-50`][rf-a-50] |

### Índices

|           Nombre            |                             Definición                              |            Propósito            |
| :-------------------------: | :-----------------------------------------------------------------: | :-----------------------------: |
| `idx_inscripcion_actividad` |                     `(actividad_id, estado_id)`                     | Bandeja de [`RF-A-22`][rf-a-22] |
|  `idx_inscripcion_usuario`  |                   `(usuario_id, created_at DESC)`                   | Listado propio del participante |
|  `idx_inscripcion_espera`   | `(actividad_id, posicion_espera) WHERE posicion_espera IS NOT NULL` |       Promoción en orden        |

### Notas de diseño

`trg_inscripcion_contador` lee `ocupa_cupo` del catálogo de estado en lugar de
comparar contra una lista de códigos. Cuando la DIEM añada un estado de
_inscripción provisional_, decidir si ocupa cupo será marcar un booleano.

`trg_inscripcion_cierre_bloqueado` implementa la parte de [`RF-P-19`][rf-p-19]
que impide cancelar lo que ya ocurrió. Sin él, un estudiante podría borrar de su
historial la actividad de la que se retiró a mitad, que es exactamente el dato que
la DIEM necesita conservar.

`es_excepcion_cupo` no es un estado: es una marca permanente sobre por qué esa
fila existe a pesar del límite. Los reportes de ocupación la restan para no
afirmar que una actividad de cuarenta cupos tuvo cuarenta y tres inscritos
regulares.

---

## `participacion`

Hecho verificado. Es la tabla que responde la pregunta que motiva el sistema.

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 2,500-15,000 filas
- **Origen:**
  > - [`RF-A-25`][rf-a-25]
  > - [`RF-A-26`][rf-a-26]
  > - [`RF-P-21`][rf-p-21]

### Columnas

|       Campo        |      Tipo      | Nulo |   Predeterminado   |                    Descripción                    |
| :----------------: | :------------: | :--: | :----------------: | :-----------------------------------------------: |
|    `usuario_id`    |     `uuid`     |  no  |                    |                   Llave foránea                   |
|   `actividad_id`   |     `uuid`     |  no  |                    |                   Llave foránea                   |
|  `inscripcion_id`  |     `uuid`     |  sí  |                    |  Nulo cuando la persona asistió sin inscribirse   |
|       `anio`       |   `smallint`   |  no  |                    | Año de reporte, copiado de la actividad al crear  |
|      `rol_id`      |     `uuid`     |  no  |                    |        Llave foránea a `rol_participacion`        |
|    `equipo_id`     |     `uuid`     |  sí  |                    |                                                   |
|    `estado_id`     |     `uuid`     |  no  |                    |      Llave foránea a `estado_participacion`       |
|   `fecha_inicio`   |     `date`     |  sí  |                    |       Puede faltar en registros históricos        |
|    `fecha_fin`     |     `date`     |  sí  |                    |                                                   |
|   `validada_at`    | `timestamptz`  |  sí  |                    |        Nulo = registrada pero no validada         |
|   `validada_por`   |     `uuid`     |  sí  |                    |       Llave foránea `RESTRICT` a `usuario`        |
| `enlace_evidencia` | `varchar(500)` |  no  |        `''`        |                                                   |
|  `observaciones`   |     `text`     |  no  |        `''`        |            Notas de la administración             |
|    `anulada_at`    | `timestamptz`  |  sí  |                    |                  Marca de cierre                  |
|    `motivo_id`     |     `uuid`     |  sí  |                    |               Obligatorio al anular               |
|      `origen`      | `varchar(20)`  |  no  | `'administracion'` | `administracion` / `carga_masiva` / `importacion` |

### Llaves foráneas

|     Columna      |       Referencia       | `ON DELETE` |                       Notas                        |
| :--------------: | :--------------------: | :---------: | :------------------------------------------------: |
|   `usuario_id`   |       `usuario`        | `RESTRICT`  |            La fusión traslada, no borra            |
|  `actividad_id`  |      `actividad`       | `RESTRICT`  |                                                    |
| `inscripcion_id` |     `inscripcion`      | `RESTRICT`  |                                                    |
|     `rol_id`     |  `rol_participacion`   | `RESTRICT`  |                                                    |
|   `equipo_id`    |        `equipo`        | `RESTRICT`  |                                                    |
|   `estado_id`    | `estado_participacion` | `RESTRICT`  |                                                    |
|  `validada_por`  |       `usuario`        | `RESTRICT`  | El expediente debe seguir nombrando a quien validó |
|   `motivo_id`    |        `motivo`        | `RESTRICT`  |        De ámbito `anulacion_participacion`         |

### Constraints

```postgresql
CONSTRAINT chk_participacion_origen
CHECK (origen IN ('administracion', 'carga_masiva', 'importacion'))

CONSTRAINT chk_participacion_validacion_coherente
CHECK ((validada_at IS NULL) = (validada_por IS NULL))

CONSTRAINT chk_participacion_anulacion
CHECK ((anulada_at IS NULL) = (motivo_id IS NULL))

CONSTRAINT chk_participacion_anulacion_requiere_validacion
CHECK (anulada_at IS NULL OR validada_at IS NOT NULL)

CONSTRAINT chk_participacion_fechas
CHECK (fecha_fin IS NULL OR fecha_inicio IS NULL OR fecha_fin >= fecha_inicio)

CONSTRAINT chk_participacion_anio
CHECK (anio BETWEEN 2000 AND 2100)
```

### Unicidad

|               Nombre               |                                 Definición                                 |                      Propósito                      |
| :--------------------------------: | :------------------------------------------------------------------------: | :-------------------------------------------------: |
| `unq_participacion_persona_activa` |           `(usuario_id, actividad_id) WHERE anulada_at IS NULL`            |   Una participación viva por persona y actividad    |
|  `unq_participacion_inscripcion`   | `(inscripcion_id) WHERE inscripcion_id IS NOT NULL AND anulada_at IS NULL` | Una inscripción produce a lo sumo una participación |

### Triggers

|                 Nombre                  |                          Evento                          | Momento  | Nivel |                                         Regla                                         |        Origen        |
| :-------------------------------------: | :------------------------------------------------------: | :------: | :---: | :-----------------------------------------------------------------------------------: | :------------------: |
|  `trg_participacion_estado_coherente`   |             `INSERT`, `UPDATE OF estado_id`              | `BEFORE` | `ROW` |     Verifica la transición y exige `validada_at` en todo estado con `es_efectiva`     |   [`RN-07`][rn-07]   |
| `trg_participacion_actividad_coherente` |     `INSERT`, `UPDATE OF inscripcion_id, equipo_id`      | `BEFORE` | `ROW` |         Exige que la inscripción y el equipo pertenezcan a la misma actividad         | [`RF-A-25`][rf-a-25] |
| `trg_participacion_actividad_validable` |                 `UPDATE OF validada_at`                  | `BEFORE` | `ROW` |      Rechaza validar si el estado de la actividad no declara `admite_validacion`      | [`RF-A-26`][rf-a-26] |
|   `trg_participacion_otorgar_puntos`    |                 `UPDATE OF validada_at`                  | `AFTER`  | `ROW` | Resuelve la regla vigente y emite el `movimiento_punto`; si no hay regla, cero puntos | [`RF-A-31`][rf-a-31] |
|   `trg_participacion_revertir_puntos`   |                  `UPDATE OF anulada_at`                  | `AFTER`  | `ROW` |         Emite el movimiento inverso e invalida las constancias que la amparan         | [`RF-A-29`][rf-a-29] |
|       `trg_participacion_evento`        | `INSERT`, `UPDATE OF estado_id, validada_at, anulada_at` | `AFTER`  | `ROW` |                    Escribe la transición en `participacion_evento`                    | [`RF-A-04`][rf-a-04] |
|      `trg_participacion_no_borrar`      |                         `DELETE`                         | `BEFORE` | `ROW` |                                  Bloquea el borrado                                   | [`RF-A-50`][rf-a-50] |

### Índices

|                Nombre                |                                 Definición                                  |              Propósito              |
| :----------------------------------: | :-------------------------------------------------------------------------: | :---------------------------------: |
|   `idx_participacion_usuario_anio`   |                          `(usuario_id, anio DESC)`                          |  Historial de [`RF-P-21`][rf-p-21]  |
| `idx_participacion_actividad_estado` |                         `(actividad_id, estado_id)`                         | Listado de validación por actividad |
|  `idx_participacion_efectiva_anio`   | `(anio, actividad_id) WHERE validada_at IS NOT NULL AND anulada_at IS NULL` |   Conteo de participantes reales    |
|   `idx_participacion_sin_validar`    |      `(actividad_id) WHERE validada_at IS NULL AND anulada_at IS NULL`      |  Bandeja de pendientes de validar   |
|      `idx_participacion_equipo`      |                  `(equipo_id) WHERE equipo_id IS NOT NULL`                  |   Composición efectiva del equipo   |

### Notas de diseño

`inscripcion_id` es nulable y esa nulabilidad es la que hace honesta la tabla.
En una charla abierta la asistencia se recoge el mismo día y no hay inscripción
previa; forzar una inscripción sintética para poder registrar la participación
crearía inscripciones que nadie hizo y arruinaría el conteo que [`RN-13`][rn-13]
exige.

`anio` se copia de la actividad al crear la fila y no se lee por unión. Es
denormalización deliberada: el índice de conteo anual es el que sostiene el
reporte más pedido del sistema, y sin la columna local exigiría unir con
`actividad` en cada consulta de agregación.

`chk_participacion_anulacion_requiere_validacion` impide anular lo que nunca se
validó. Una participación registrada y no validada se corrige editándola o
cerrando su inscripción; la anulación es para deshacer un hecho ya afirmado, y
usarla antes vaciaría de significado el rastro de anulaciones.

El trigger de otorgamiento de puntos vive aquí y no en el módulo de puntos porque
la transacción que valida es la que debe emitir el movimiento. Separarlos
permitiría que existiera, aunque fuera un instante, una participación validada
sin sus puntos, y ese instante es todo lo que hace falta para que un reporte
concurrente publique una cifra menor.

---

## `participacion_evento`

Historial de transiciones. Es el que permite responder cuándo se validó algo y
quién lo hizo, incluso después de una anulación.

- **Régimen:** [`append-only`][auditoria], **alto volumen**
- **Volumen estimado:** 3-5 filas por participación
- **Origen:**
  > - [`RF-A-04`][rf-a-04]

### Columnas

|       Campo        |     Tipo      | Nulo |                  Descripción                  |
| :----------------: | :-----------: | :--: | :-------------------------------------------: |
| `participacion_id` |    `uuid`     |  no  |                 Llave foránea                 |
| `estado_desde_id`  |    `uuid`     |  sí  |         Nulo en el evento de creación         |
| `estado_hasta_id`  |    `uuid`     |  no  |                                               |
|   `ocurrido_at`    | `timestamptz` |  no  |                                               |
|     `actor_id`     |    `uuid`     |  sí  | Nulo cuando el actor es el proceso programado |
|    `actor_tipo`    | `varchar(20)` |  no  | `participante` / `administracion` / `sistema` |
|    `motivo_id`     |    `uuid`     |  sí  |                                               |
|     `contexto`     |    `jsonb`    |  no  |     `'{}'`; petición, dirección de origen     |

### Índices

|                 Nombre                  |            Definición             |        Propósito        |
| :-------------------------------------: | :-------------------------------: | :---------------------: |
| `idx_participacionevento_participacion` | `(participacion_id, ocurrido_at)` | Trayectoria de una fila |
|   `brin_participacionevento_ocurrido`   |    `(ocurrido_at) USING BRIN`     |  Barrido de retención   |

---

## `equipo`

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 200-1,500 filas
- **Origen:**
  > - [`RF-A-21`][rf-a-21]
  > - [`RF-P-20`][rf-p-20]

### Columnas

|     Campo      |      Tipo      | Nulo | Predeterminado |               Descripción                |
| :------------: | :------------: | :--: | :------------: | :--------------------------------------: |
| `actividad_id` |     `uuid`     |  no  |                |              Llave foránea               |
|    `nombre`    | `varchar(120)` |  no  |                |                                          |
| `codigo_union` | `varchar(10)`  |  no  |                |  Único; el que se comparte para unirse   |
|  `creado_por`  |     `uuid`     |  sí  |                |    Nulo si lo creó la administración     |
| `congelado_at` | `timestamptz`  |  sí  |                | Composición fijada al cerrar inscripción |

### Unicidad

|       Nombre        |           Definición            |               Propósito               |
| :-----------------: | :-----------------------------: | :-----------------------------------: |
| `unq_equipo_codigo` |        `(codigo_union)`         |   Un código lleva a un solo equipo    |
| `unq_equipo_nombre` | `(actividad_id, lower(nombre))` | Sin nombres repetidos en la actividad |

### Triggers

|            Nombre             |  Evento  | Momento  | Nivel |                           Regla                           |        Origen        |
| :---------------------------: | :------: | :------: | :---: | :-------------------------------------------------------: | :------------------: |
| `trg_equipo_actividad_admite` | `INSERT` | `BEFORE` | `ROW` | Rechaza crear equipos en actividades sin `admite_equipos` | [`RF-P-20`][rf-p-20] |

---

## `equipo_miembro`

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 800-6,000 filas

### Columnas

|     Campo     |     Tipo      | Nulo | Predeterminado |       Descripción       |
| :-----------: | :-----------: | :--: | :------------: | :---------------------: |
|  `equipo_id`  |    `uuid`     |  no  |                | Llave foránea `CASCADE` |
| `usuario_id`  |    `uuid`     |  no  |                |      Llave foránea      |
|  `es_lider`   |   `boolean`   |  no  |    `false`     |                         |
| `retirado_at` | `timestamptz` |  sí  |                |     Marca de cierre     |

### Unicidad

|           Nombre            |                      Definición                      |         Propósito         |
| :-------------------------: | :--------------------------------------------------: | :-----------------------: |
| `unq_equipomiembro_vigente` | `(equipo_id, usuario_id) WHERE retirado_at IS NULL`  |  Sin miembros repetidos   |
|  `unq_equipomiembro_lider`  | `(equipo_id) WHERE es_lider AND retirado_at IS NULL` | Como máximo un líder vivo |

### Triggers

|                 Nombre                  |              Evento               | Momento  | Nivel |                                  Regla                                  |        Origen        |
| :-------------------------------------: | :-------------------------------: | :------: | :---: | :---------------------------------------------------------------------: | :------------------: |
| `trg_equipomiembro_un_equipo_actividad` |             `INSERT`              | `BEFORE` | `ROW` | Rechaza si la persona ya pertenece a otro equipo vivo de esa actividad  | [`RF-A-21`][rf-a-21] |
|     `trg_equipomiembro_tamano_max`      | `INSERT`, `UPDATE OF retirado_at` | `BEFORE` | `ROW` |                Rechaza si supera `actividad.equipo_max`                 | [`RF-P-20`][rf-p-20] |
|      `trg_equipomiembro_congelado`      |   `INSERT`, `UPDATE`, `DELETE`    | `BEFORE` | `ROW` | Rechaza cambios si el equipo está congelado, salvo actor administrativo | [`RF-A-21`][rf-a-21] |

El tamaño mínimo **no** se comprueba por trigger: un equipo se construye
incorporando miembros de uno en uno y el primero siempre violaría el mínimo. Se
valida al cerrar la inscripción, donde la administración decide si disuelve el
equipo incompleto o lo admite.

---

## `reconocimiento`

Resultados obtenidos en una actividad. Una participación puede acumular varios.

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 200-2,000 filas
- **Origen:**
  > - [`RF-A-28`][rf-a-28]

### Columnas

|       Campo        |      Tipo      | Nulo | Predeterminado |              Descripción              |
| :----------------: | :------------: | :--: | :------------: | :-----------------------------------: |
| `participacion_id` |     `uuid`     |  no  |                |             Llave foránea             |
|     `tipo_id`      |     `uuid`     |  no  |                | Llave foránea a `tipo_reconocimiento` |
|   `descripcion`    | `varchar(300)` |  no  |                | Denominación del premio o credencial  |
|     `posicion`     |   `smallint`   |  sí  |                | Lugar obtenido, cuando es un concurso |
|   `otorgado_en`    |     `date`     |  sí  |                |                                       |
| `enlace_evidencia` | `varchar(500)` |  no  |      `''`      |                                       |
|    `anulado_at`    | `timestamptz`  |  sí  |                |                                       |

### Constraints

```postgresql
CONSTRAINT chk_reconocimiento_posicion
CHECK (posicion IS NULL OR posicion > 0)
```

### Índices

|               Nombre               |                       Definición                       |          Propósito          |
| :--------------------------------: | :----------------------------------------------------: | :-------------------------: |
| `idx_reconocimiento_participacion` |                  `(participacion_id)`                  |  Ficha de la participación  |
|     `idx_reconocimiento_tipo`      | `(tipo_id, otorgado_en DESC) WHERE anulado_at IS NULL` | Reporte anual de premiación |

### Notas de diseño

La matriz de participaciones guarda el resultado como una sola columna de texto
libre. Separarlo en filas tipificadas es lo que convierte _¿cuántas
microcredenciales entregó la DIEM en 2025?_ de una lectura manual en una consulta,
y lo que permite que una participación tenga a la vez una posición en el concurso
y una certificación por haberlo completado, que en la matriz obliga a elegir cuál
escribir.

[auditoria]: ../convenciones.md#auditoria-por-tabla
[d-10]: ../decisiones.md#d-10
[rf-a-04]: ../../requerimientos/funcionales/administracion.md#rf-a-04
[rf-a-21]: ../../requerimientos/funcionales/administracion.md#rf-a-21
[rf-a-22]: ../../requerimientos/funcionales/administracion.md#rf-a-22
[rf-a-23]: ../../requerimientos/funcionales/administracion.md#rf-a-23
[rf-a-24]: ../../requerimientos/funcionales/administracion.md#rf-a-24
[rf-a-25]: ../../requerimientos/funcionales/administracion.md#rf-a-25
[rf-a-26]: ../../requerimientos/funcionales/administracion.md#rf-a-26
[rf-a-27]: ../../requerimientos/funcionales/administracion.md#rf-a-27
[rf-a-28]: ../../requerimientos/funcionales/administracion.md#rf-a-28
[rf-a-29]: ../../requerimientos/funcionales/administracion.md#rf-a-29
[rf-a-31]: ../../requerimientos/funcionales/administracion.md#rf-a-31
[rf-a-50]: ../../requerimientos/funcionales/administracion.md#rf-a-50
[rf-p-16]: ../../requerimientos/funcionales/participantes.md#rf-p-16
[rf-p-17]: ../../requerimientos/funcionales/participantes.md#rf-p-17
[rf-p-18]: ../../requerimientos/funcionales/participantes.md#rf-p-18
[rf-p-19]: ../../requerimientos/funcionales/participantes.md#rf-p-19
[rf-p-20]: ../../requerimientos/funcionales/participantes.md#rf-p-20
[rf-p-21]: ../../requerimientos/funcionales/participantes.md#rf-p-21
[rn-05]: ../../requerimientos/reglas-negocio.md#rn-05
[rn-07]: ../../requerimientos/reglas-negocio.md#rn-07
[rn-11]: ../../requerimientos/reglas-negocio.md#rn-11
[rn-13]: ../../requerimientos/reglas-negocio.md#rn-13
