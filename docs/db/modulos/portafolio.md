---
icon: lucide/lightbulb
---

# Portafolio de innovación

Cuatro tablas: la propuesta con sus diez clasificaciones, sus integrantes, las
actividades por las que ha pasado y su trayectoria.

Este módulo es el que traduce la matriz de portafolio, la más ambiciosa de las
tres. Sus riesgos de adopción están en [`R-07`][r-07] y [`R-08`][r-08], y no son
de modelado: son de si la DIEM logrará mantener veintidós campos por propuesta.

## Requerimientos cubiertos

- [`RF-A-37`][rf-a-37]
- [`RF-A-38`][rf-a-38]
- [`RF-A-39`][rf-a-39]
- [`RF-A-40`][rf-a-40]
- [`RF-A-41`][rf-a-41]

---

## `propuesta`

- **Régimen:** [Mutable rastreada][auditoria]
- **Volumen estimado:** 150-800 filas
- **Origen:**
  > - [`RF-A-37`][rf-a-37]
  > - [`RF-A-38`][rf-a-38]
  > - [`RF-A-39`][rf-a-39]

### Columnas

|          Campo           |      Tipo      | Nulo | Predeterminado |                       Descripción                       |
| :----------------------: | :------------: | :--: | :------------: | :-----------------------------------------------------: |
|         `codigo`         | `varchar(20)`  |  no  |                |           Único, generado. `UAM-INN-2026-014`           |
|         `nombre`         | `varchar(200)` |  no  |                |                                                         |
|      `anio_ingreso`      |   `smallint`   |  no  |                |            Año del primer ingreso; inmutable            |
|  `actividad_origen_id`   |     `uuid`     |  sí  |                |  Actividad en la que surgió; nula si no surgió de una   |
|        `problema`        |     `text`     |  no  |      `''`      |          Problema y oportunidad identificados           |
|        `solucion`        |     `text`     |  no  |      `''`      |            Síntesis de la solución propuesta            |
|  `usuario_beneficiario`  |     `text`     |  no  |      `''`      |                Quién usa o se beneficia                 |
|   `cliente_adoptante`    |     `text`     |  no  |      `''`      |                   Quién paga o adopta                   |
| `nivel_formalizacion_id` |     `uuid`     |  no  |                |                      Llave foránea                      |
|  `etapa_desarrollo_id`   |     `uuid`     |  no  |                |                      Llave foránea                      |
|       `estado_id`        |     `uuid`     |  no  |                |           Llave foránea a `estado_propuesta`            |
|    `ambito_helice_id`    |     `uuid`     |  no  |                |                      Llave foránea                      |
|    `sector_cuaen_id`     |     `uuid`     |  no  |                |                      Llave foránea                      |
|      `vertical_id`       |     `uuid`     |  no  |                |          Llave foránea a `vertical_innovacion`          |
|   `tipo_innovacion_id`   |     `uuid`     |  no  |                |                      Llave foránea                      |
|      `nivel_trl_id`      |     `uuid`     |  no  |                |                      Llave foránea                      |
|      `nivel_mrl_id`      |     `uuid`     |  no  |                |                      Llave foránea                      |
|    `ods_principal_id`    |     `uuid`     |  no  |                |                  Llave foránea a `ods`                  |
|   `ods_secundario_id`    |     `uuid`     |  no  |                |                  Llave foránea a `ods`                  |
|   `enlace_expediente`    | `varchar(500)` |  no  |      `''`      |                                                         |
|     `clasificada_at`     | `timestamptz`  |  sí  |                | Nulo mientras alguna clasificación siga en valor neutro |
|       `cerrada_at`       | `timestamptz`  |  sí  |                |                     Marca de cierre                     |
|       `motivo_id`        |     `uuid`     |  sí  |                |                  Obligatorio al cerrar                  |

### Llaves foráneas

Las diez columnas de clasificación referencian las tablas de
[`Taxonomías`][taxonomias] con `ON DELETE RESTRICT`. Además:

|        Columna        |     Referencia     | `ON DELETE` |            Notas             |
| :-------------------: | :----------------: | :---------: | :--------------------------: |
| `actividad_origen_id` |    `actividad`     | `RESTRICT`  |                              |
|      `estado_id`      | `estado_propuesta` | `RESTRICT`  |                              |
|      `motivo_id`      |      `motivo`      | `RESTRICT`  | De ámbito `cierre_propuesta` |

### Constraints

```postgresql
CONSTRAINT chk_propuesta_codigo_formato
CHECK (codigo ~ '^UAM-INN-[0-9]{4}-[0-9]{3,4}$')

CONSTRAINT chk_propuesta_anio
CHECK (anio_ingreso BETWEEN 2015 AND 2100)

CONSTRAINT chk_propuesta_ods_distintos
CHECK (ods_principal_id <> ods_secundario_id)

CONSTRAINT chk_propuesta_cierre
CHECK ((cerrada_at IS NULL) = (motivo_id IS NULL))
```

### Unicidad

|         Nombre         |    Definición     |
| :--------------------: | :---------------: |
| `unq_propuesta_codigo` |    `(codigo)`     |
| `unq_propuesta_nombre` | `(lower(nombre))` |

### Triggers

|              Nombre               |              Evento              | Momento  | Nivel |                                       Regla                                        |        Origen        |
| :-------------------------------: | :------------------------------: | :------: | :---: | :--------------------------------------------------------------------------------: | :------------------: |
|  `trg_propuesta_codigo_asignar`   |             `INSERT`             | `BEFORE` | `ROW` |  Genera el código correlativo dentro de `anio_ingreso`; ignora el valor recibido   | [`RF-A-38`][rf-a-38] |
|  `trg_propuesta_codigo_readonly`  | `UPDATE OF codigo, anio_ingreso` | `BEFORE` | `ROW` |            Rechaza cualquier cambio en el código y en el año de ingreso            | [`RF-A-38`][rf-a-38] |
| `trg_propuesta_clasificada_marca` |             `UPDATE`             | `BEFORE` | `ROW` | Fija o limpia `clasificada_at` según si queda alguna clasificación con `es_neutro` | [`RF-A-39`][rf-a-39] |
|      `trg_propuesta_evento`       |        `INSERT`, `UPDATE`        | `AFTER`  | `ROW` |     Escribe en `propuesta_evento` los cambios de etapa, estado y clasificación     | [`RF-A-41`][rf-a-41] |
| `trg_propuesta_estado_coherente`  | `INSERT`, `UPDATE OF estado_id`  | `BEFORE` | `ROW` |                Verifica la transición contra `transicion_propuesta`                |    [`D-10`][d-10]    |

### Índices

|            Nombre            |                               Definición                                |                Propósito                 |
| :--------------------------: | :---------------------------------------------------------------------: | :--------------------------------------: |
| `idx_propuesta_etapa_estado` |                   `(etapa_desarrollo_id, estado_id)`                    |     Tablero de [`RF-A-47`][rf-a-47]      |
|     `idx_propuesta_anio`     |                          `(anio_ingreso DESC)`                          |         Cohortes del portafolio          |
|   `idx_propuesta_vigente`    |            `(etapa_desarrollo_id) WHERE cerrada_at IS NULL`             |             Portafolio vivo              |
|    `gin_propuesta_texto`     | `((nombre \|\| ' ' \|\| problema \|\| ' ' \|\| solucion) gin_trgm_ops)` |              Búsqueda libre              |
|     `idx_propuesta_ods`      |                          `(ods_principal_id)`                           | Reporte de alineación con la Agenda 2030 |

### Notas de diseño

Las diez clasificaciones son obligatorias y ninguna es nulable. La nulabilidad
diría _no sabemos_ y las taxonomías ya dicen eso mejor: cada una tiene un valor
neutro de _por determinar_, marcado con `es_neutro`, que es el predeterminado al
registrar. La diferencia importa porque `NULL` no se puede agrupar en un reporte
y `por_determinar` sí, y porque una propuesta con nueve clasificaciones nulas y
una completada es indistinguible de una recién creada bajo el criterio de nulos.

`clasificada_at` convierte esa diferencia en algo que se puede consultar: cuántas
propuestas del portafolio están realmente clasificadas y cuántas siguen a medias.
Es el indicador que [`R-07`][r-07] pide vigilar.

`anio_ingreso` es inmutable por trigger porque el glosario de la matriz lo dice
explícitamente: es el año del primer ingreso y no cambia aunque la propuesta siga
participando en actividades posteriores. Sin el trigger, la corrección más
razonable del mundo —_esta propuesta en realidad entró en 2024_— rompería el
correlativo del código.

Los dos ODS son columnas y no una tabla puente. La matriz admite exactamente dos y
el orden entre ellos es significativo: el principal y el secundario no son
intercambiables. Una tabla puente con una columna de orden modelaría lo mismo
admitiendo un tercero que el marco no contempla, y obligaría a unir para el
reporte más frecuente del módulo.

---

## `propuesta_integrante`

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 500-3,500 filas
- **Origen:**
  > - [`RF-A-40`][rf-a-40]

### Columnas

|     Campo      |     Tipo      | Nulo | Predeterminado |                Descripción                 |
| :------------: | :-----------: | :--: | :------------: | :----------------------------------------: |
| `propuesta_id` |    `uuid`     |  no  |                |               Llave foránea                |
|  `usuario_id`  |    `uuid`     |  no  |                |               Llave foránea                |
|     `rol`      | `varchar(30)` |  no  |                |                Ver `CHECK`                 |
|    `desde`     |    `date`     |  no  |                |    Inicio del período de participación     |
|    `hasta`     |    `date`     |  sí  |                |          Nulo = integrante activo          |
| `es_contacto`  |   `boolean`   |  no  |    `false`     | A quién escribe la DIEM sobre la propuesta |

### Constraints

```postgresql
CONSTRAINT chk_propuestaintegrante_rol
CHECK (
  rol IN (
    'responsable',
    'integrante',
    'docente_tutor',
    'mentor',
    'colaborador_externo'
  )
)

CONSTRAINT chk_propuestaintegrante_periodo
CHECK (hasta IS NULL OR hasta >= desde)
```

### Unicidad

|                Nombre                 |                          Definición                          |             Propósito             |
| :-----------------------------------: | :----------------------------------------------------------: | :-------------------------------: |
|   `unq_propuestaintegrante_vigente`   |       `(propuesta_id, usuario_id) WHERE hasta IS NULL`       | Sin integrantes repetidos activos |
|  `unq_propuestaintegrante_contacto`   |     `(propuesta_id) WHERE es_contacto AND hasta IS NULL`     |       Un solo contacto vivo       |
| `unq_propuestaintegrante_responsable` | `(propuesta_id) WHERE rol = 'responsable' AND hasta IS NULL` |     Un solo responsable vivo      |

### Índices

|              Nombre               |   Definición   |             Propósito              |
| :-------------------------------: | :------------: | :--------------------------------: |
| `idx_propuestaintegrante_usuario` | `(usuario_id)` | Portafolio propio del participante |

### Notas de diseño

El período con `desde` y `hasta` es lo que distingue esta tabla de
`equipo_miembro`. Un equipo existe durante una actividad y se congela al cerrar
la inscripción; una propuesta dura años y sus integrantes entran y salen. Quien
sostuvo el proyecto en 2024 sigue constando aunque hoy no participe, que es lo
que permite responder quién ha pasado por una propuesta y no solo quién está hoy.

Es también la razón por la que este módulo no referencia a `participacion`. La
persona se vincula a la propuesta por sí misma, no a través del hecho de haber
participado en la actividad de origen, porque hay integrantes que se sumaron
después y no participaron en ella.

---

## `propuesta_actividad`

Actividades por las que ha pasado la propuesta después de la de origen.

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 200-1,500 filas
- **Origen:**
  > - [`RF-A-41`][rf-a-41]

### Columnas

|       Campo        |      Tipo      | Nulo | Predeterminado |               Descripción               |
| :----------------: | :------------: | :--: | :------------: | :-------------------------------------: |
|   `propuesta_id`   |     `uuid`     |  no  |                |              Llave foránea              |
|   `actividad_id`   |     `uuid`     |  no  |                |              Llave foránea              |
|       `rol`        | `varchar(30)`  |  no  | `'participa'`  | `participa` / `origina` / `se_presenta` |
|    `resultado`     | `varchar(200)` |  no  |      `''`      |       Desenlace en esa actividad        |
| `enlace_evidencia` | `varchar(500)` |  no  |      `''`      |                                         |

### Unicidad

|            Nombre            |           Definición           |
| :--------------------------: | :----------------------------: |
| `unq_propuestaactividad_par` | `(propuesta_id, actividad_id)` |

### Notas de diseño

`actividad_origen_id` vive en `propuesta` y además aparece aquí con rol
`origina`. La redundancia es deliberada: la columna sostiene la consulta directa
_de qué actividad salió_ y la fila sostiene el recorrido cronológico completo sin
tener que unir dos orígenes distintos. Un trigger mantiene ambas coherentes al
insertar.

---

## `propuesta_evento`

Trayectoria. Es lo que permite reconstruir la evolución de una propuesta sin
depender de la memoria de quien la acompañó.

- **Régimen:** [`append-only`][auditoria]
- **Volumen estimado:** 5-20 filas por propuesta
- **Origen:**
  > - [`RF-A-41`][rf-a-41]

### Columnas

|      Campo      |      Tipo      | Nulo |                         Descripción                          |
| :-------------: | :------------: | :--: | :----------------------------------------------------------: |
| `propuesta_id`  |     `uuid`     |  no  |                        Llave foránea                         |
|     `tipo`      | `varchar(30)`  |  no  | `etapa` / `estado` / `clasificacion` / `integrante` / `nota` |
|     `campo`     | `varchar(60)`  |  no  |            Columna que cambió; `''` en las notas             |
|  `valor_antes`  | `varchar(150)` |  no  |                 Etiqueta legible, no el UUID                 |
| `valor_despues` | `varchar(150)` |  no  |                                                              |
|     `nota`      |     `text`     |  no  |                             `''`                             |
|  `ocurrido_at`  | `timestamptz`  |  no  |                                                              |
|   `actor_id`    |     `uuid`     |  sí  |        Nulo cuando el actor es el proceso programado         |

### Constraints

```postgresql
CONSTRAINT chk_propuestaevento_tipo
CHECK (tipo IN ('etapa', 'estado', 'clasificacion', 'integrante', 'nota'))
```

### Índices

|             Nombre              |          Definición           |          Propósito          |
| :-----------------------------: | :---------------------------: | :-------------------------: |
| `idx_propuestaevento_propuesta` | `(propuesta_id, ocurrido_at)` | Trayectoria de la propuesta |
| `brin_propuestaevento_ocurrido` |  `(ocurrido_at) USING BRIN`   |    Barrido de retención     |

### Notas de diseño

Se guardan las **etiquetas legibles** y no los UUID de las taxonomías. La
trayectoria se lee años después y debe decir _pasó de preincubación a
incubación_, no dos identificadores que obligan a resolver contra un catálogo que
para entonces pudo haber cambiado de etiqueta.

Es la misma razón por la que esta tabla no tiene llaves foráneas a las taxonomías:
un evento histórico no debe impedir desactivar una clasificación que la DIEM ya no
usa.

[auditoria]: ../convenciones.md#auditoria-por-tabla
[d-10]: ../decisiones.md#d-10
[r-07]: ../riesgos.md#r-07
[r-08]: ../riesgos.md#r-08
[rf-a-37]: ../../requerimientos/funcionales/administracion.md#rf-a-37
[rf-a-38]: ../../requerimientos/funcionales/administracion.md#rf-a-38
[rf-a-39]: ../../requerimientos/funcionales/administracion.md#rf-a-39
[rf-a-40]: ../../requerimientos/funcionales/administracion.md#rf-a-40
[rf-a-41]: ../../requerimientos/funcionales/administracion.md#rf-a-41
[rf-a-47]: ../../requerimientos/funcionales/administracion.md#rf-a-47
[taxonomias]: taxonomias.md
