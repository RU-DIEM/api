---
icon: lucide/clipboard-check
---

# Inscripción y participación

Las dos tablas cuya separación motiva el proyecto entero, más los equipos, los
reconocimientos y la asignación de mentores. Viven en la app
`rudi_participacion`.

Contar inscripciones y llamarlas participantes es el error que la DIEM quiere
dejar de cometer. Aquí ese error deja de ser posible: son dos tablas, con dos
volúmenes distintos y dos significados distintos, y ninguna consulta puede
confundirlas sin decirlo ([`D-11`][d-11]).

El historial de transiciones (`participacion_evento` en el diseño original) no
es una tabla propia: lo registra pghistory en `ParticipacionEvent`, con el actor
y la petición en `pgh_context` ([`D-15`][d-15]).

## Requerimientos cubiertos

- [`RF-P-16`][rf-p-16]
- [`RF-P-17`][rf-p-17]
- [`RF-P-18`][rf-p-18]
- [`RF-P-19`][rf-p-19]
- [`RF-P-20`][rf-p-20]
- [`RF-P-21`][rf-p-21]
- [`RF-P-27`][rf-p-27]
- [`RF-A-20`][rf-a-20]
- [`RF-A-21`][rf-a-21]
- [`RF-A-22`][rf-a-22]
- [`RF-A-25`][rf-a-25]
- [`RF-A-26`][rf-a-26]
- [`RF-A-28`][rf-a-28]
- [`RF-A-29`][rf-a-29]

---

## `inscripcion`

Intención de participar. No prueba nada por sí sola.

- **Régimen:** [Mutable protegida][auditoria], rastreada
- **Volumen estimado:** 3,000-20,000 filas
- **Origen:**
  > - [`RF-P-16`][rf-p-16]
  > - [`RF-A-22`][rf-a-22]

### Columnas

|        Campo         |     Tipo      | Nulo | Predeterminado |                   Descripción                    |
| :------------------: | :-----------: | :--: | :------------: | :----------------------------------------------: |
|      `user_id`       |    `uuid`     |  no  |                |                     Persona                      |
|    `actividad_id`    |    `uuid`     |  no  |                |                  Llave foránea                   |
|     `estado_id`      |    `uuid`     |  no  |                |       Llave foránea a `estado_inscripcion`       |
|       `origen`       | `varchar(20)` |  no  |                |      `usuario` / `sistema` / `importacion`       |
|   `creada_por_id`    |    `uuid`     |  sí  |                | Cuenta administrativa; solo con origen `sistema` |
|  `posicion_espera`   |  `smallint`   |  sí  |                | Con valor solo mientras está en lista de espera  |
| `is_excepcion_cupo`  |   `boolean`   |  no  |    `false`     |     Inscripción admitida por encima del cupo     |
|   `confirmada_at`    | `timestamptz` |  sí  |                |                                                  |
|     `cerrada_at`     | `timestamptz` |  sí  |                |      Marca de cierre: cancelada o rechazada      |
|     `motivo_id`      |    `uuid`     |  sí  |                |              Obligatorio al cerrar               |
| `motivo_descripcion` |    `text`     |  no  |      `''`      |                                                  |

### Llaves foráneas

|     Columna     |      Referencia      | `ON DELETE` |                                      Notas                                      |
| :-------------: | :------------------: | :---------: | :-----------------------------------------------------------------------------: |
|    `user_id`    |     `rudi_user`      | `RESTRICT`  |                          La fusión traslada, no borra                           |
| `actividad_id`  |     `actividad`      | `RESTRICT`  |                                                                                 |
|   `estado_id`   | `estado_inscripcion` | `RESTRICT`  |                                                                                 |
| `creada_por_id` |      `ApiUser`       | `RESTRICT`  |              El historial debe seguir nombrando a quien inscribió               |
|   `motivo_id`   |       `motivo`       | `RESTRICT`  | `cancelacion_inscripcion`, o `cancelacion_actividad` si la cerró la cancelación |

### Constraints

```postgresql
CONSTRAINT chk_inscripcion_origen
CHECK (origen IN ('importacion', 'sistema', 'usuario'))

CONSTRAINT chk_inscripcion_creador
CHECK ((origen = 'sistema') = (creada_por_id IS NOT NULL))

CONSTRAINT chk_inscripcion_cierre
CHECK ((cerrada_at IS NULL) = (motivo_id IS NULL))

CONSTRAINT chk_inscripcion_espera_positiva
CHECK (posicion_espera IS NULL OR posicion_espera > 0)
```

### Unicidad

|              Nombre               |                             Definición                              |       Propósito        |
| :-------------------------------: | :-----------------------------------------------------------------: | :--------------------: |
| `unq_inscripcion_persona_activa`  |         `(user_id, actividad_id) WHERE cerrada_at IS NULL`          |    [`RN-05`][rn-05]    |
| `unq_inscripcion_posicion_espera` | `(actividad_id, posicion_espera) WHERE posicion_espera IS NOT NULL` | Sin empates en la fila |

### Triggers

|               Nombre                |                             Evento                              | Momento  | Nivel |                                       Regla                                       |        Origen        |
| :---------------------------------: | :-------------------------------------------------------------: | :------: | :---: | :-------------------------------------------------------------------------------: | :------------------: |
|   `trg_inscripcion_estado_activo`   |                      `INSERT`<br/>`UPDATE`                      | `BEFORE` | `ROW` |                       El estado asignado debe estar activo                        | [Familia][t-estado]  |
|  `trg_inscripcion_estado_terminal`  |                  `UPDATE` con cambio de estado                  | `BEFORE` | `ROW` |                       Una inscripción cerrada no se reabre                        | [Familia][t-estado]  |
| `trg_inscripcion_transicion_valida` |                  `UPDATE` con cambio de estado                  | `BEFORE` | `ROW` |        El par debe estar en `transicion_estado_inscripcion` para el actor         |    [`D-10`][d-10]    |
| `trg_inscripcion_estado_coherente`  | `INSERT`<br/>`UPDATE OF estado_id, cerrada_at, posicion_espera` | `BEFORE` | `ROW` | Estado `terminal` ⇔ `cerrada_at`; en lista de espera, el estado no `consume_cupo` |    [`D-09`][d-09]    |
|      `trg_inscripcion_motivo`       |                      `INSERT`<br/>`UPDATE`                      | `BEFORE` | `ROW` |                        El motivo es de un ámbito de cierre                        | [Familia][t-motivo]  |
|  `trg_inscripcion_ventana_abierta`  |                            `INSERT`                             | `BEFORE` | `ROW` | Con origen `usuario`, la actividad `allow_inscripcion` y la ventana está abierta  | [`RF-P-16`][rf-p-16] |
| `trg_inscripcion_cierre_bloqueado`  |                     `UPDATE OF cerrada_at`                      | `BEFORE` | `ROW` |             Rechaza cerrar si existe participación validada asociada              | [`RF-P-19`][rf-p-19] |
|     `trg_inscripcion_contador`      |               `INSERT`<br/>`UPDATE OF estado_id`                | `AFTER`  | `ROW` |   Ajusta `actividad.inscritos_activos` según `consume_cupo`, salvo excepciones    |   [`RN-11`][rn-11]   |
|  `trg_inscripcion_promover_espera`  |                      `UPDATE OF estado_id`                      | `AFTER`  | `ROW` |        Si deja de consumir cupo, promueve al primero de la lista de espera        | [`RF-P-18`][rf-p-18] |

### Índices

|           Nombre            |          Definición          |            Propósito            |
| :-------------------------: | :--------------------------: | :-----------------------------: |
| `idx_inscripcion_actividad` | `(actividad_id, estado_id)`  | Bandeja de [`RF-A-22`][rf-a-22] |
|   `idx_inscripcion_user`    | `(user_id, created_at DESC)` | Listado propio del participante |

### Notas de diseño

`trg_inscripcion_contador` lee `consume_cupo` del catálogo de estado en lugar de
comparar contra una lista de códigos. Cuando la DIEM añada un estado de
_inscripción provisional_, decidir si ocupa cupo será marcar un booleano.

`trg_inscripcion_cierre_bloqueado` implementa la parte de [`RF-P-19`][rf-p-19]
que impide cancelar lo que ya ocurrió. Sin él, un estudiante podría borrar de su
historial la actividad de la que se retiró a mitad, que es exactamente el dato que
la DIEM necesita conservar.

`is_excepcion_cupo` no es un estado: es una marca permanente sobre por qué esa
fila existe a pesar del límite. No suma a `inscritos_activos`, de modo que el
`CHECK` de cupo no la rechaza y los reportes de ocupación no afirman que una
actividad de cuarenta cupos tuvo cuarenta y tres inscritos regulares.

La promoción de la lista de espera la hace `rudi_promover_espera(actividad)`,
una función de la migración de la app que comparten
`trg_inscripcion_promover_espera` y `trg_actividad_promover_espera`. Toma la
inscripción con menor `posicion_espera` y la mueve, como actor `sistema`, al
estado que la tabla de transiciones declare desde su estado actual con
`consume_cupo`; repite mientras quede cupo. Notifica y **no confirma**: el estado
de destino lo decide la DIEM al declarar la transición.

---

## `participacion`

Hecho verificado. Es la tabla que responde la pregunta que motiva el sistema.

- **Régimen:** [Mutable protegida][auditoria], rastreada
- **Volumen estimado:** 2,500-15,000 filas
- **Origen:**
  > - [`RF-A-25`][rf-a-25]
  > - [`RF-A-26`][rf-a-26]
  > - [`RF-P-21`][rf-p-21]

### Columnas

|        Campo         |      Tipo      | Nulo |   Predeterminado   |                    Descripción                    |
| :------------------: | :------------: | :--: | :----------------: | :-----------------------------------------------: |
|      `user_id`       |     `uuid`     |  no  |                    |                      Persona                      |
|    `actividad_id`    |     `uuid`     |  no  |                    |                   Llave foránea                   |
|   `inscripcion_id`   |     `uuid`     |  sí  |                    |  Nulo cuando la persona asistió sin inscribirse   |
|        `anio`        |   `smallint`   |  no  |                    | Año de reporte, copiado de la actividad al crear  |
|       `rol_id`       |     `uuid`     |  no  |                    |        Llave foránea a `rol_participacion`        |
|     `equipo_id`      |     `uuid`     |  sí  |                    |                                                   |
|     `estado_id`      |     `uuid`     |  no  |                    |      Llave foránea a `estado_participacion`       |
|       `origen`       | `varchar(20)`  |  no  | `'administracion'` | `administracion` / `carga_masiva` / `importacion` |
|    `fecha_inicio`    |     `date`     |  sí  |                    |       Puede faltar en registros históricos        |
|     `fecha_fin`      |     `date`     |  sí  |                    |                                                   |
|    `validada_at`     | `timestamptz`  |  sí  |                    |        Nulo = registrada pero no validada         |
|  `validada_por_id`   |     `uuid`     |  sí  |                    |           Cuenta que validó, `RESTRICT`           |
|  `enlace_evidencia`  | `varchar(500)` |  no  |        `''`        |                                                   |
|   `observaciones`    |     `text`     |  no  |        `''`        |            Notas de la administración             |
|     `anulada_at`     | `timestamptz`  |  sí  |                    |                  Marca de cierre                  |
|     `motivo_id`      |     `uuid`     |  sí  |                    | Obligatorio al anular; `anulacion_participacion`  |
| `motivo_descripcion` |     `text`     |  no  |        `''`        |                                                   |

### Constraints

```postgresql
CONSTRAINT chk_participacion_origen
CHECK (origen IN ('administracion', 'carga_masiva', 'importacion'))

CONSTRAINT chk_participacion_anio
CHECK (anio BETWEEN 2000 AND 2100)

CONSTRAINT chk_participacion_validacion_coherente
CHECK ((validada_at IS NULL) = (validada_por_id IS NULL))

CONSTRAINT chk_participacion_anulacion
CHECK ((anulada_at IS NULL) = (motivo_id IS NULL))

CONSTRAINT chk_participacion_anulacion_validada
CHECK (anulada_at IS NULL OR validada_at IS NOT NULL)

CONSTRAINT chk_participacion_fechas
CHECK (fecha_fin IS NULL OR fecha_inicio IS NULL OR fecha_fin >= fecha_inicio)
```

### Unicidad

|               Nombre               |                                 Definición                                 |                      Propósito                      |
| :--------------------------------: | :------------------------------------------------------------------------: | :-------------------------------------------------: |
| `unq_participacion_persona_activa` |             `(user_id, actividad_id) WHERE anulada_at IS NULL`             |   Una participación viva por persona y actividad    |
|  `unq_participacion_inscripcion`   | `(inscripcion_id) WHERE inscripcion_id IS NOT NULL AND anulada_at IS NULL` | Una inscripción produce a lo sumo una participación |

### Triggers

|                  Nombre                   |                     Evento                      | Momento  | Nivel |                                        Regla                                        |        Origen         |
| :---------------------------------------: | :---------------------------------------------: | :------: | :---: | :---------------------------------------------------------------------------------: | :-------------------: |
|     `trg_participacion_estado_activo`     |              `INSERT`<br/>`UPDATE`              | `BEFORE` | `ROW` |                        El estado asignado debe estar activo                         |  [Familia][t-estado]  |
|    `trg_participacion_estado_terminal`    |          `UPDATE` con cambio de estado          | `BEFORE` | `ROW` |                      Un desenlace terminal no vuelve a cambiar                      |  [Familia][t-estado]  |
|   `trg_participacion_transicion_valida`   |          `UPDATE` con cambio de estado          | `BEFORE` | `ROW` |        El par debe estar en `transicion_estado_participacion` para el actor         |    [`D-10`][d-10]     |
|   `trg_participacion_estado_coherente`    | `INSERT`<br/>`UPDATE OF estado_id, validada_at` | `BEFORE` | `ROW` |                      Un estado `efectiva` exige `validada_at`                       |   [`RN-07`][rn-07]    |
|        `trg_participacion_motivo`         |              `INSERT`<br/>`UPDATE`              | `BEFORE` | `ROW` |                      El motivo es de `anulacion_participacion`                      |  [Familia][t-motivo]  |
|    `trg_participacion_catalogo_activo`    |                    `INSERT`                     | `BEFORE` | `ROW` |                              El rol debe estar activo                               | [Familia][t-catalogo] |
|       `trg_participacion_snapshot`        |                    `INSERT`                     | `BEFORE` | `ROW` |                 Copia `anio` desde la actividad, ignore lo recibido                 | [Familia][t-snapshot] |
|          `trg_readonly_snapshot`          |     `UPDATE OF user_id, actividad_id, anio`     | `BEFORE` | `ROW` |                    La persona, la actividad y el año no cambian                     |    [`D-14`][d-14]     |
|  `trg_participacion_actividad_coherente`  |              `INSERT`<br/>`UPDATE`              | `BEFORE` | `ROW` | La inscripción es de la misma persona y actividad; el equipo, de la misma actividad | [`RF-A-25`][rf-a-25]  |
|  `trg_participacion_actividad_validable`  |      `INSERT`<br/>`UPDATE OF validada_at`       | `BEFORE` | `ROW` |           Validar exige que el estado de la actividad `allow_validacion`            | [`RF-A-26`][rf-a-26]  |
|    `trg_participacion_otorgar_puntos`     |      `INSERT`<br/>`UPDATE OF validada_at`       | `AFTER`  | `ROW` |      Emite el `movimiento_punto` automático; ver [`Puntos`][puntos-resolucion]      | [`RF-A-31`][rf-a-31]  |
|    `trg_participacion_revertir_puntos`    |             `UPDATE OF anulada_at`              | `AFTER`  | `ROW` |                 Revierte los movimientos vivos de la participación                  | [`RF-A-29`][rf-a-29]  |
| `trg_participacion_invalidar_constancias` |             `UPDATE OF anulada_at`              | `AFTER`  | `ROW` |                 Anula las constancias que amparan la participación                  | [`RF-A-29`][rf-a-29]  |

Los tres últimos se declaran en `rudi_puntos` y `rudi_constancias` y se
registran sobre `Participacion` ([Efecto en otra tabla][t-efecto]): la
transacción que valida es la que emite los puntos, y la que anula es la que los
revierte, sin que `participacion` conozca a esos módulos.

### Índices

|                Nombre                |                                 Definición                                  |              Propósito              |
| :----------------------------------: | :-------------------------------------------------------------------------: | :---------------------------------: |
|    `idx_participacion_user_anio`     |                           `(user_id, anio DESC)`                            |  Historial de [`RF-P-21`][rf-p-21]  |
| `idx_participacion_actividad_estado` |                         `(actividad_id, estado_id)`                         | Listado de validación por actividad |
|  `idx_participacion_efectiva_anio`   | `(anio, actividad_id) WHERE validada_at IS NOT NULL AND anulada_at IS NULL` |   Conteo de participantes reales    |
|   `idx_participacion_sin_validar`    |      `(actividad_id) WHERE validada_at IS NULL AND anulada_at IS NULL`      |  Bandeja de pendientes de validar   |

### Notas de diseño

`inscripcion_id` es nulable y esa nulabilidad es la que hace honesta la tabla.
En una charla abierta la asistencia se recoge el mismo día y no hay inscripción
previa; forzar una inscripción sintética crearía inscripciones que nadie hizo y
arruinaría el conteo que [`RN-13`][rn-13] exige.

`anio` se copia de la actividad al crear la fila y no se lee por unión. Es
denormalización deliberada: el índice de conteo anual sostiene el reporte más
pedido del sistema. La copia la hace el trigger, no el servicio, y queda
congelada ([`D-14`][d-14]).

`chk_participacion_anulacion_validada` impide anular lo que nunca se validó. Una
participación registrada y no validada se corrige editándola; la anulación es
para deshacer un hecho ya afirmado.

---

## `equipo` y `equipo_miembro`

- **Régimen:** [Mutable protegida][auditoria], rastreada
- **Volumen estimado:** 200-1,500 equipos, 800-6,000 miembros
- **Origen:**
  > - [`RF-A-21`][rf-a-21]
  > - [`RF-P-20`][rf-p-20]

### `equipo`

|      Campo      |      Tipo      | Nulo |                        Descripción                        |
| :-------------: | :------------: | :--: | :-------------------------------------------------------: |
| `actividad_id`  |     `uuid`     |  no  |                       Llave foránea                       |
|    `nombre`     | `varchar(120)` |  no  |         Único por actividad sobre `lower(nombre)`         |
| `codigo_union`  | `varchar(10)`  |  no  | `^[A-Z0-9]{6,10}$`, único; el que se comparte para unirse |
| `creado_por_id` |     `uuid`     |  sí  |        Persona; nulo si lo creó la administración         |
| `congelado_at`  | `timestamptz`  |  sí  |         Composición fijada al cerrar inscripción          |

### `equipo_miembro`

|     Campo     |     Tipo      | Nulo | Predeterminado |       Descripción       |
| :-----------: | :-----------: | :--: | :------------: | :---------------------: |
|  `equipo_id`  |    `uuid`     |  no  |                | Llave foránea `CASCADE` |
|   `user_id`   |    `uuid`     |  no  |                |         Persona         |
|  `is_lider`   |   `boolean`   |  no  |    `false`     |                         |
| `retirado_at` | `timestamptz` |  sí  |                |     Marca de cierre     |

|           Nombre            |                      Definición                      |         Propósito         |
| :-------------------------: | :--------------------------------------------------: | :-----------------------: |
| `unq_equipomiembro_vigente` |   `(equipo_id, user_id) WHERE retirado_at IS NULL`   |  Sin miembros repetidos   |
|  `unq_equipomiembro_lider`  | `(equipo_id) WHERE is_lider AND retirado_at IS NULL` | Como máximo un líder vivo |

### Triggers

|                 Nombre                  |                Evento                | Momento  | Nivel |                                   Regla                                   |        Origen        |
| :-------------------------------------: | :----------------------------------: | :------: | :---: | :-----------------------------------------------------------------------: | :------------------: |
|      `trg_equipo_actividad_admite`      |               `INSERT`               | `BEFORE` | `ROW` |         Rechaza crear equipos en actividades sin `admite_equipos`         | [`RF-P-20`][rf-p-20] |
| `trg_equipomiembro_un_equipo_actividad` | `INSERT`<br/>`UPDATE OF retirado_at` | `BEFORE` | `ROW` |  Rechaza si la persona ya pertenece a otro equipo vivo de esa actividad   | [`RF-A-21`][rf-a-21] |
|     `trg_equipomiembro_tamano_max`      | `INSERT`<br/>`UPDATE OF retirado_at` | `BEFORE` | `ROW` |                 Rechaza si supera `actividad.equipo_max`                  | [`RF-P-20`][rf-p-20] |
|      `trg_equipomiembro_congelado`      |        `INSERT`<br/>`UPDATE`         | `BEFORE` | `ROW` | Rechaza cambios si el equipo está congelado, salvo actor `administracion` | [`RF-A-21`][rf-a-21] |

El tamaño mínimo **no** se comprueba por trigger: un equipo se construye
incorporando miembros de uno en uno y el primero siempre violaría el mínimo. Se
valida al cerrar la inscripción, donde la administración decide si disuelve el
equipo incompleto o lo admite.

---

## `reconocimiento`

Resultados obtenidos en una actividad. Una participación puede acumular varios.

- **Régimen:** [Mutable protegida][auditoria], rastreada
- **Volumen estimado:** 200-2,000 filas
- **Origen:**
  > - [`RF-A-28`][rf-a-28]

|       Campo        |      Tipo      | Nulo | Predeterminado |                      Descripción                      |
| :----------------: | :------------: | :--: | :------------: | :---------------------------------------------------: |
| `participacion_id` |     `uuid`     |  no  |                |                     Llave foránea                     |
|     `tipo_id`      |     `uuid`     |  no  |                |         Llave foránea a `tipo_reconocimiento`         |
|   `descripcion`    | `varchar(300)` |  no  |                |         Denominación del premio o credencial          |
|     `posicion`     |   `smallint`   |  sí  |                | Lugar obtenido, cuando es un concurso; mayor que cero |
|   `otorgado_en`    |     `date`     |  sí  |                |                                                       |
| `enlace_evidencia` | `varchar(500)` |  no  |      `''`      |                                                       |
|    `anulado_at`    | `timestamptz`  |  sí  |                |                                                       |

|          Nombre           |                       Definición                       |          Propósito          |
| :-----------------------: | :----------------------------------------------------: | :-------------------------: |
| `idx_reconocimiento_tipo` | `(tipo_id, otorgado_en DESC) WHERE anulado_at IS NULL` | Reporte anual de premiación |

`trg_reconocimiento_catalogo_activo` exige que el tipo esté activo al insertar
([Familia][t-catalogo]).

La matriz de participaciones guarda el resultado como una sola columna de texto
libre. Separarlo en filas tipificadas es lo que convierte _¿cuántas
microcredenciales entregó la DIEM en 2025?_ de una lectura manual en una consulta.

---

## `asignacion_mentor`

Vínculo de un mentor con una actividad, con su propio ciclo de vida. Implementa
[`RN-12`][rn-12]. Vive en este módulo y no en [`Actividades`][actividades]
porque referencia a `equipo`.

- **Régimen:** [Mutable protegida][auditoria], rastreada
- **Volumen estimado:** 200-1,200 filas
- **Origen:**
  > - [`RF-A-20`][rf-a-20]
  > - [`RF-P-27`][rf-p-27]

### Columnas

|         Campo         |      Tipo      | Nulo | Predeterminado |                                       Descripción                                       |
| :-------------------: | :------------: | :--: | :------------: | :-------------------------------------------------------------------------------------: |
|    `actividad_id`     |     `uuid`     |  no  |                |                                      Llave foránea                                      |
|      `mentor_id`      |     `uuid`     |  no  |                |                            Llave foránea a `mentor_profile`                             |
|      `equipo_id`      |     `uuid`     |  sí  |                |                       Con valor si acompaña a un equipo concreto                        |
| `tipo_acompanamiento` | `varchar(30)`  |  no  |                | `mentoria_tecnica` / `mentoria_negocio` / `jurado` / `facilitacion` / `charla` / `otro` |
|      `estado_id`      |     `uuid`     |  no  |                |                       Llave foránea a `estado_asignacion_mentor`                        |
|    `propuesta_at`     | `timestamptz`  |  no  |    `now()`     |                                                                                         |
|    `respondida_at`    | `timestamptz`  |  sí  |                |                            Instante en que aceptó o declinó                             |
|    `finalizada_at`    | `timestamptz`  |  sí  |                |                                     Marca de cierre                                     |
|      `motivo_id`      |     `uuid`     |  sí  |                |                       Obligatorio al declinar; `rechazo_mentoria`                       |
| `motivo_descripcion`  |     `text`     |  no  |      `''`      |                                                                                         |
|    `observaciones`    |     `text`     |  no  |      `''`      |                         Aporte que el mentor registra al cerrar                         |
|  `enlace_evidencia`   | `varchar(500)` |  no  |      `''`      |                                                                                         |

### Unicidad e índices

|              Nombre              |                                      Definición                                       |              Propósito               |
| :------------------------------: | :-----------------------------------------------------------------------------------: | :----------------------------------: |
|  `unq_asignacionmentor_vigente`  | `(actividad_id, mentor_id, equipo_id) NULLS NOT DISTINCT WHERE finalizada_at IS NULL` |   No se propone dos veces lo mismo   |
|  `idx_asignacionmentor_mentor`   |                           `(mentor_id, propuesta_at DESC)`                            |    Agenda de [`RF-P-28`][rf-p-28]    |
| `idx_asignacionmentor_pendiente` |        `(propuesta_at) WHERE respondida_at IS NULL AND finalizada_at IS NULL`         | Barrido de vencimiento de propuestas |

`NULLS NOT DISTINCT` hace que la asignación a toda la actividad (`equipo_id`
nulo) también sea única; sin él, dos propuestas idénticas sin equipo no
colisionarían.

### Triggers

|                  Nombre                  |               Evento               | Momento  | Nivel |                                                  Regla                                                  |        Origen        |
| :--------------------------------------: | :--------------------------------: | :------: | :---: | :-----------------------------------------------------------------------------------------------------: | :------------------: |
|   `trg_asignacionmentor_estado_activo`   |       `INSERT`<br/>`UPDATE`        | `BEFORE` | `ROW` |                                  El estado asignado debe estar activo                                   | [Familia][t-estado]  |
|  `trg_asignacionmentor_estado_terminal`  |   `UPDATE` con cambio de estado    | `BEFORE` | `ROW` |                                   Una asignación cerrada no se reabre                                   | [Familia][t-estado]  |
| `trg_asignacionmentor_estado_coherente`  | `INSERT`<br/>`UPDATE OF estado_id` | `BEFORE` | `ROW` | `require_motivo` exige motivo; salir del inicial fija `respondida_at`; un terminal fija `finalizada_at` | [`RF-P-27`][rf-p-27] |
|      `trg_asignacionmentor_motivo`       |       `INSERT`<br/>`UPDATE`        | `BEFORE` | `ROW` |                                   El motivo es de `rechazo_mentoria`                                    | [Familia][t-motivo]  |
| `trg_asignacionmentor_mentor_confirmado` |              `INSERT`              | `BEFORE` | `ROW` |                        Rechaza asignar a un perfil de mentor sin `confirmado_at`                        | [`RF-P-12`][rf-p-12] |
| `trg_asignacionmentor_equipo_coherente`  |       `INSERT`<br/>`UPDATE`        | `BEFORE` | `ROW` |                           Exige que el equipo pertenezca a la misma actividad                           |   [`RN-12`][rn-12]   |

La asignación no se autoconfirma por silencio. Una propuesta sin respuesta
permanece como propuesta y el proceso programado la marca como vencida, porque
publicar como mentor confirmado a alguien que nunca aceptó es una afirmación
institucional falsa sobre una persona.

[actividades]: actividades.md
[auditoria]: ../convenciones.md#auditoria-por-tabla
[puntos-resolucion]: puntos.md#resolucion-de-la-regla-aplicable
[t-catalogo]: ../triggers.md#catalogo-activo
[t-efecto]: ../triggers.md#efecto-en-otra-tabla
[t-estado]: ../triggers.md#ciclo-de-vida-del-estado
[t-motivo]: ../triggers.md#motivo-de-lista-cerrada
[t-snapshot]: ../triggers.md#derivacion-de-snapshot
[d-09]: ../decisiones.md#d-09
[d-10]: ../decisiones.md#d-10
[d-11]: ../decisiones.md#d-11
[d-14]: ../decisiones.md#d-14
[d-15]: ../decisiones.md#d-15
[rf-a-20]: ../../requerimientos/funcionales/administracion.md#rf-a-20
[rf-a-21]: ../../requerimientos/funcionales/administracion.md#rf-a-21
[rf-a-22]: ../../requerimientos/funcionales/administracion.md#rf-a-22
[rf-a-25]: ../../requerimientos/funcionales/administracion.md#rf-a-25
[rf-a-26]: ../../requerimientos/funcionales/administracion.md#rf-a-26
[rf-a-28]: ../../requerimientos/funcionales/administracion.md#rf-a-28
[rf-a-29]: ../../requerimientos/funcionales/administracion.md#rf-a-29
[rf-a-31]: ../../requerimientos/funcionales/administracion.md#rf-a-31
[rf-p-12]: ../../requerimientos/funcionales/participantes.md#rf-p-12
[rf-p-16]: ../../requerimientos/funcionales/participantes.md#rf-p-16
[rf-p-17]: ../../requerimientos/funcionales/participantes.md#rf-p-17
[rf-p-18]: ../../requerimientos/funcionales/participantes.md#rf-p-18
[rf-p-19]: ../../requerimientos/funcionales/participantes.md#rf-p-19
[rf-p-20]: ../../requerimientos/funcionales/participantes.md#rf-p-20
[rf-p-21]: ../../requerimientos/funcionales/participantes.md#rf-p-21
[rf-p-27]: ../../requerimientos/funcionales/participantes.md#rf-p-27
[rf-p-28]: ../../requerimientos/funcionales/participantes.md#rf-p-28
[rn-05]: ../../requerimientos/reglas-negocio.md#rn-05
[rn-07]: ../../requerimientos/reglas-negocio.md#rn-07
[rn-11]: ../../requerimientos/reglas-negocio.md#rn-11
[rn-12]: ../../requerimientos/reglas-negocio.md#rn-12
[rn-13]: ../../requerimientos/reglas-negocio.md#rn-13
