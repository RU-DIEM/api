---
icon: lucide/lightbulb
---

# Portafolio de innovación

Tres tablas en la app `rudi_portafolio`: la propuesta con sus diez
clasificaciones, sus integrantes y las actividades por las que ha pasado.

La trayectoria (`propuesta_evento` en el diseño original) no es una tabla
propia: cada cambio de etapa, estado o clasificación queda en
`PropuestaEvent` (pghistory, [`D-15`][d-15]). La lectura con etiquetas legibles
—_pasó de preincubación a incubación_— es un servicio que traduce el diff de dos
eventos con las etiquetas de las [`Taxonomías`][taxonomias].

## Requerimientos cubiertos

- [`RF-A-37`][rf-a-37]
- [`RF-A-38`][rf-a-38]
- [`RF-A-39`][rf-a-39]
- [`RF-A-40`][rf-a-40]
- [`RF-A-41`][rf-a-41]

---

## `propuesta`

- **Régimen:** [Mutable protegida][auditoria], rastreada
- **Volumen estimado:** 150-800 filas
- **Origen:**
  > - [`RF-A-37`][rf-a-37]
  > - [`RF-A-38`][rf-a-38]
  > - [`RF-A-39`][rf-a-39]

### Columnas

|         Campo          |      Tipo      | Nulo |  Predeterminado  |                       Descripción                       |
| :--------------------: | :------------: | :--: | :--------------: | :-----------------------------------------------------: |
|        `codigo`        | `varchar(20)`  |  no  |     asignado     |     Único, generado por trigger. `UAM-INN-2026-014`     |
|        `nombre`        | `varchar(200)` |  no  |                  |          Único sobre `upper(unaccent(nombre))`          |
|     `anio_ingreso`     |   `smallint`   |  no  |                  |            Año del primer ingreso; inmutable            |
| `actividad_origen_id`  |     `uuid`     |  sí  |                  |  Actividad en la que surgió; nula si no surgió de una   |
|       `problema`       |     `text`     |  no  |       `''`       |          Problema y oportunidad identificados           |
|       `solucion`       |     `text`     |  no  |       `''`       |            Síntesis de la solución propuesta            |
| `usuario_beneficiario` |     `text`     |  no  |       `''`       |                Quién usa o se beneficia                 |
|  `cliente_adoptante`   |     `text`     |  no  |       `''`       |                   Quién paga o adopta                   |
| `nivel_formalizacion`  | `varchar(30)`  |  no  |                  |                 `NivelesFormalizacion`                  |
|   `etapa_desarrollo`   | `varchar(30)`  |  no  | `por_determinar` |                   `EtapasDesarrollo`                    |
|  `ambito_aplicacion`   | `varchar(30)`  |  no  |                  |                   `AmbitosAplicacion`                   |
|  `sector_aplicacion`   | `varchar(30)`  |  no  | `por_determinar` |                  `SectoresAplicacion`                   |
|       `vertical`       | `varchar(30)`  |  no  | `por_determinar` |                 `VerticalesInnovacion`                  |
|   `tipo_innovacion`    | `varchar(30)`  |  no  | `por_determinar` |                    `TiposInnovacion`                    |
|         `trl`          | `varchar(30)`  |  no  | `por_determinar` |                          `TRL`                          |
|         `mrl`          | `varchar(30)`  |  no  | `por_determinar` |                          `MRL`                          |
|    `ods_principal`     | `varchar(30)`  |  no  | `por_determinar` |                          `ODS`                          |
|    `ods_secundario`    | `varchar(30)`  |  no  |   `no_aplica`    |                          `ODS`                          |
|      `estado_id`       |     `uuid`     |  no  |                  |           Llave foránea a `estado_propuesta`            |
|  `enlace_expediente`   | `varchar(500)` |  no  |       `''`       |                                                         |
|    `clasificada_at`    | `timestamptz`  |  sí  |                  | Nulo mientras alguna clasificación siga en valor neutro |
|      `cerrada_at`      | `timestamptz`  |  sí  |                  |                     Marca de cierre                     |
|      `motivo_id`       |     `uuid`     |  sí  |                  |        Obligatorio al cerrar; `cierre_propuesta`        |
|  `motivo_descripcion`  |     `text`     |  no  |       `''`       |                                                         |

### Constraints

Una por clasificación (`chk_propuesta_<campo>`, contra su enumeración), y:

```postgresql
CONSTRAINT chk_propuesta_codigo_format
CHECK (codigo ~ '^UAM-INN-[0-9]{4}-[0-9]{3,4}$')

CONSTRAINT chk_propuesta_anio
CHECK (anio_ingreso BETWEEN 2015 AND 2100)

CONSTRAINT chk_propuesta_ods_distintos
CHECK (ods_principal <> ods_secundario)

CONSTRAINT chk_propuesta_ods_principal
CHECK (ods_principal <> 'no_aplica')

CONSTRAINT chk_propuesta_cierre
CHECK ((cerrada_at IS NULL) = (motivo_id IS NULL))
```

### Triggers

|              Nombre               |                     Evento                     | Momento  | Nivel |                                                    Regla                                                    |        Origen        |
| :-------------------------------: | :--------------------------------------------: | :------: | :---: | :---------------------------------------------------------------------------------------------------------: | :------------------: |
|   `trg_propuesta_estado_activo`   |             `INSERT`<br/>`UPDATE`              | `BEFORE` | `ROW` |                                    El estado asignado debe estar activo                                     | [Familia][t-estado]  |
|  `trg_propuesta_estado_terminal`  |         `UPDATE` con cambio de estado          | `BEFORE` | `ROW` |                                     Una propuesta cerrada no se reabre                                      | [Familia][t-estado]  |
| `trg_propuesta_transicion_valida` |         `UPDATE` con cambio de estado          | `BEFORE` | `ROW` |                      El par debe estar en `transicion_estado_propuesta` para el actor                       |    [`D-10`][d-10]    |
| `trg_propuesta_estado_coherente`  | `INSERT`<br/>`UPDATE OF estado_id, cerrada_at` | `BEFORE` | `ROW` |                                      Estado `terminal` ⇔ `cerrada_at`                                       |    [`D-09`][d-09]    |
|      `trg_propuesta_motivo`       |             `INSERT`<br/>`UPDATE`              | `BEFORE` | `ROW` |                                     El motivo es de `cierre_propuesta`                                      | [Familia][t-motivo]  |
|  `trg_propuesta_codigo_asignar`   |                    `INSERT`                    | `BEFORE` | `ROW` |               Genera el código correlativo dentro de `anio_ingreso`; ignora el valor recibido               | [`RF-A-38`][rf-a-38] |
| `trg_readonly_codigo_anioingreso` |        `UPDATE OF codigo, anio_ingreso`        | `BEFORE` | `ROW` |                                  El código y el año de ingreso no cambian                                   | [`RF-A-38`][rf-a-38] |
| `trg_propuesta_clasificada_marca` |             `INSERT`<br/>`UPDATE`              | `BEFORE` | `ROW` | Fija `clasificada_at` cuando ninguna clasificación queda en valor neutro, y la limpia si vuelve a haber una | [`RF-A-39`][rf-a-39] |
| `trg_propuesta_actividad_origen`  |  `INSERT`<br/>`UPDATE OF actividad_origen_id`  | `AFTER`  | `ROW` |                 Registra la actividad de origen en `propuesta_actividad` con rol `origina`                  | [`RF-A-41`][rf-a-41] |

`trg_propuesta_codigo_asignar` toma un bloqueo de asesoría por año
(`pg_advisory_xact_lock`) antes de leer el correlativo, de modo que dos altas
simultáneas del mismo año no compiten por el mismo número.

### Índices

|            Nombre            |                                       Definición                                       |                Propósito                 |
| :--------------------------: | :------------------------------------------------------------------------------------: | :--------------------------------------: |
| `idx_propuesta_etapa_estado` |                            `(etapa_desarrollo, estado_id)`                             |     Tablero de [`RF-A-47`][rf-a-47]      |
|     `idx_propuesta_anio`     |                                 `(anio_ingreso DESC)`                                  |         Cohortes del portafolio          |
|   `idx_propuesta_vigente`    |                     `(etapa_desarrollo) WHERE cerrada_at IS NULL`                      |             Portafolio vivo              |
|     `idx_propuesta_ods`      |                                   `(ods_principal)`                                    | Reporte de alineación con la Agenda 2030 |
|    `gin_propuesta_texto`     | `(upper(unaccent(nombre \|\| ' ' \|\| problema \|\| ' ' \|\| solucion)) gin_trgm_ops)` |              Búsqueda libre              |

### Notas de diseño

Las diez clasificaciones son obligatorias y ninguna es nulable. La nulabilidad
diría _no sabemos_ y las taxonomías ya dicen eso mejor: casi todas tienen un
valor neutro de _por determinar_, que es el predeterminado al registrar. La
diferencia importa porque `NULL` no se puede agrupar en un reporte y
`por_determinar` sí. `nivel_formalizacion` y `ambito_aplicacion` no tienen valor
neutro: se exigen al registrar.

`clasificada_at` convierte esa diferencia en algo que se puede consultar: cuántas
propuestas del portafolio están realmente clasificadas y cuántas siguen a medias.

Los dos ODS son columnas y no una tabla puente. La matriz admite exactamente dos y
el orden entre ellos es significativo: el principal y el secundario no son
intercambiables.

---

## `propuesta_integrante`

- **Régimen:** [Mutable protegida][auditoria], rastreada
- **Volumen estimado:** 500-3,500 filas
- **Origen:**
  > - [`RF-A-40`][rf-a-40]

|     Campo      |     Tipo      | Nulo | Predeterminado |                                    Descripción                                    |
| :------------: | :-----------: | :--: | :------------: | :-------------------------------------------------------------------------------: |
| `propuesta_id` |    `uuid`     |  no  |                |                                   Llave foránea                                   |
|   `user_id`    |    `uuid`     |  no  |                |                                      Persona                                      |
|     `rol`      | `varchar(30)` |  no  |                | `responsable` / `integrante` / `docente_tutor` / `mentor` / `colaborador_externo` |
|    `desde`     |    `date`     |  no  |                |                        Inicio del período de participación                        |
|    `hasta`     |    `date`     |  sí  |                |                       Nulo = integrante activo; `>= desde`                        |
| `is_contacto`  |   `boolean`   |  no  |    `false`     |                    A quién escribe la DIEM sobre la propuesta                     |

|                Nombre                 |                          Definición                          |             Propósito             |
| :-----------------------------------: | :----------------------------------------------------------: | :-------------------------------: |
|   `unq_propuestaintegrante_vigente`   |        `(propuesta_id, user_id) WHERE hasta IS NULL`         | Sin integrantes repetidos activos |
|  `unq_propuestaintegrante_contacto`   |     `(propuesta_id) WHERE is_contacto AND hasta IS NULL`     |       Un solo contacto vivo       |
| `unq_propuestaintegrante_responsable` | `(propuesta_id) WHERE rol = 'responsable' AND hasta IS NULL` |     Un solo responsable vivo      |

El período con `desde` y `hasta` es lo que distingue esta tabla de
`equipo_miembro`. Un equipo existe durante una actividad; una propuesta dura años
y sus integrantes entran y salen. Es también la razón por la que este módulo no
referencia a `participacion`: hay integrantes que se sumaron después y no
participaron en la actividad de origen.

---

## `propuesta_actividad`

Actividades por las que ha pasado la propuesta.

- **Régimen:** [Mutable protegida][auditoria], rastreada
- **Volumen estimado:** 200-1,500 filas
- **Origen:**
  > - [`RF-A-41`][rf-a-41]

|       Campo        |      Tipo      | Nulo | Predeterminado |               Descripción               |
| :----------------: | :------------: | :--: | :------------: | :-------------------------------------: |
|   `propuesta_id`   |     `uuid`     |  no  |                |              Llave foránea              |
|   `actividad_id`   |     `uuid`     |  no  |                |              Llave foránea              |
|       `rol`        | `varchar(30)`  |  no  | `'participa'`  | `participa` / `origina` / `se_presenta` |
|    `resultado`     | `varchar(200)` |  no  |      `''`      |       Desenlace en esa actividad        |
| `enlace_evidencia` | `varchar(500)` |  no  |      `''`      |                                         |

|             Nombre              |               Definición               |          Propósito           |
| :-----------------------------: | :------------------------------------: | :--------------------------: |
|  `unq_propuestaactividad_par`   |     `(propuesta_id, actividad_id)`     |                              |
| `unq_propuestaactividad_origen` | `(propuesta_id) WHERE rol = 'origina'` | Un solo origen por propuesta |

`actividad_origen_id` vive en `propuesta` y además aparece aquí con rol
`origina`. La redundancia es deliberada: la columna sostiene la consulta directa
_de qué actividad salió_ y la fila sostiene el recorrido cronológico completo.
`trg_propuesta_actividad_origen` mantiene ambas coherentes.

[auditoria]: ../convenciones.md#auditoria-por-tabla
[taxonomias]: taxonomias.md
[t-estado]: ../triggers.md#ciclo-de-vida-del-estado
[t-motivo]: ../triggers.md#motivo-de-lista-cerrada
[d-09]: ../decisiones.md#d-09
[d-10]: ../decisiones.md#d-10
[d-15]: ../decisiones.md#d-15
[rf-a-37]: ../../requerimientos/funcionales/administracion.md#rf-a-37
[rf-a-38]: ../../requerimientos/funcionales/administracion.md#rf-a-38
[rf-a-39]: ../../requerimientos/funcionales/administracion.md#rf-a-39
[rf-a-40]: ../../requerimientos/funcionales/administracion.md#rf-a-40
[rf-a-41]: ../../requerimientos/funcionales/administracion.md#rf-a-41
[rf-a-47]: ../../requerimientos/funcionales/administracion.md#rf-a-47
