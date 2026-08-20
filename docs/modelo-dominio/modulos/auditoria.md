---
icon: lucide/scroll-text
---

# Auditoría y operación

Cinco tablas que no pertenecen al dominio pero sin las cuales el dominio no es
defendible: la bitácora, las notificaciones, la importación de las matrices y el
registro de exportaciones.

## Requerimientos cubiertos

- [`RF-A-04`][rf-a-04]
- [`RF-A-46`][rf-a-46]
- [`RF-A-49`][rf-a-49]
- [`RF-A-50`][rf-a-50]
- [`RF-P-26`][rf-p-26]

---

## `bitacora`

Registro de toda operación administrativa. Es la tabla que hace verificable el
resto del modelo.

- **Régimen:** [`append-only`][auditoria], **alto volumen**
- **Volumen estimado:** 50,000-400,000 filas
- **Origen:**
  > - [`RF-A-04`][rf-a-04]
  > - [`RN-16`][rn-16]

### Columnas

|      Campo      |     Tipo      | Nulo | Predeterminado |                     Descripción                     |
| :-------------: | :-----------: | :--: | :------------: | :-------------------------------------------------: |
|   `actor_id`    |    `uuid`     |  sí  |                |    Nulo cuando el actor es el proceso programado    |
|  `actor_tipo`   | `varchar(20)` |  no  |                |    `participante` / `administracion` / `sistema`    |
|    `accion`     | `varchar(60)` |  no  |                |    `usuario.fusion`, `participacion.validacion`     |
| `entidad_tabla` | `varchar(60)` |  no  |                |                   Tabla afectada                    |
|  `entidad_id`   |    `uuid`     |  sí  |                | Nulo en acciones que no afectan a una fila concreta |
|   `resultado`   | `varchar(20)` |  no  |     `'ok'`     |            `ok` / `rechazado` / `error`             |
|   `motivo_id`   |    `uuid`     |  sí  |                |                                                     |
|     `antes`     |    `jsonb`    |  no  |     `'{}'`     |           Solo las columnas que cambiaron           |
|    `despues`    |    `jsonb`    |  no  |     `'{}'`     |                                                     |
|   `contexto`    |    `jsonb`    |  no  |     `'{}'`     |    Petición, filtro aplicado, cantidad afectada     |
|      `ip`       |    `inet`     |  sí  |                |                                                     |
|  `ocurrido_at`  | `timestamptz` |  no  |    `now()`     |                                                     |

### Constraints

```postgresql
CONSTRAINT chk_bitacora_actor
CHECK (actor_tipo IN ('participante', 'administracion', 'sistema'))

CONSTRAINT chk_bitacora_resultado
CHECK (resultado IN ('ok', 'rechazado', 'error'))

CONSTRAINT chk_bitacora_actor_humano
CHECK ((actor_tipo = 'sistema') OR (actor_id IS NOT NULL))
```

### Triggers

|          Nombre          |  Evento  | Momento  | Nivel |             Regla              |        Origen        |
| :----------------------: | :------: | :------: | :---: | :----------------------------: | :------------------: |
| `trg_bitacora_inmutable` | `UPDATE` | `BEFORE` | `ROW` | Rechaza cualquier modificación |   [`RN-16`][rn-16]   |
| `trg_bitacora_no_borrar` | `DELETE` | `BEFORE` | `ROW` |       Bloquea el borrado       | [`RF-A-50`][rf-a-50] |

### Índices

|          Nombre          |                   Definición                    |           Propósito            |
| :----------------------: | :---------------------------------------------: | :----------------------------: |
| `brin_bitacora_ocurrido` |           `(ocurrido_at) USING BRIN`            | Consulta por rango y retención |
|  `idx_bitacora_entidad`  | `(entidad_tabla, entidad_id, ocurrido_at DESC)` |     Expediente de una fila     |
|   `idx_bitacora_actor`   |         `(actor_id, ocurrido_at DESC)`          |      Qué hizo una cuenta       |
| `gin_bitacora_contexto`  |             `(contexto) USING gin`              |  Búsqueda por filtro aplicado  |

### Notas de diseño

`antes` y `despues` guardan **solo las columnas que cambiaron**, no la fila
entera. Una fila entera por evento multiplicaría el tamaño de la bitácora por el
ancho de las tablas más grandes y enterraría el dato relevante entre treinta
columnas idénticas.

El índice principal es BRIN y no B-tree por [`R-09`][r-09]: la tabla se escribe en
orden cronológico y se consulta por rangos de fecha, que es el caso exacto para
el que BRIN existe. Un B-tree sobre `ocurrido_at` aquí ocuparía dos órdenes de
magnitud más para responder lo mismo.

`resultado` incluye `rechazado`. Registrar solo lo que salió bien deja fuera la
información más útil de una auditoría: quién intentó qué y por qué el sistema no
se lo permitió.

---

## `notificacion`

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 20,000-150,000 filas
- **Origen:**
  > - [`RF-P-06`][rf-p-06]
  > - [`RF-A-23`][rf-a-23]

### Columnas

|      Campo      |      Tipo      | Nulo | Predeterminado |                 Descripción                 |
| :-------------: | :------------: | :--: | :------------: | :-----------------------------------------: |
|  `usuario_id`   |     `uuid`     |  sí  |                | Nulo si el destinatario aún no tiene cuenta |
| `plantilla_id`  |     `uuid`     |  no  |                |     Llave foránea a `plantilla_mensaje`     |
|     `canal`     | `varchar(20)`  |  no  |   `'correo'`   |           `correo` / `en_portal`            |
| `destinatario`  | `varchar(254)` |  no  |                |            Congelado al encolar             |
|    `asunto`     | `varchar(200)` |  no  |                |                Ya sustituido                |
|    `cuerpo`     |     `text`     |  no  |                |                Ya sustituido                |
| `entidad_tabla` | `varchar(60)`  |  no  |      `''`      |         Qué originó la notificación         |
|  `entidad_id`   |     `uuid`     |  sí  |                |                                             |
|  `encolada_at`  | `timestamptz`  |  no  |    `now()`     |                                             |
|  `enviada_at`   | `timestamptz`  |  sí  |                |                                             |
|   `leida_at`    | `timestamptz`  |  sí  |                |       Solo aplica al canal en portal        |
|   `intentos`    |   `smallint`   |  no  |      `0`       |                                             |
| `ultimo_error`  | `varchar(300)` |  no  |      `''`      |                                             |
| `descartada_at` | `timestamptz`  |  sí  |                |         Tras agotar los reintentos          |

### Constraints

```postgresql
CONSTRAINT chk_notificacion_canal
CHECK (canal IN ('correo', 'en_portal'))

CONSTRAINT chk_notificacion_intentos
CHECK (intentos BETWEEN 0 AND 10)

CONSTRAINT chk_notificacion_leida_en_portal
CHECK (leida_at IS NULL OR canal = 'en_portal')
```

### Índices

|            Nombre            |                             Definición                             |        Propósito         |
| :--------------------------: | :----------------------------------------------------------------: | :----------------------: |
| `idx_notificacion_pendiente` | `(encolada_at) WHERE enviada_at IS NULL AND descartada_at IS NULL` |      Cola de envío       |
|  `idx_notificacion_usuario`  |                  `(usuario_id, encolada_at DESC)`                  | Bandeja del participante |
| `brin_notificacion_encolada` |                     `(encolada_at) USING BRIN`                     |   Barrido de retención   |

### Notas de diseño

El asunto y el cuerpo se congelan al encolar en lugar de resolverse al enviar.
Una plantilla editada entre el encolado y el envío produciría dos correos
distintos para el mismo hecho, y la copia en portal diría algo diferente del
correo que la persona recibió.

`usuario_id` nulable admite la invitación a un correo que todavía no tiene cuenta,
que es el caso de la carga inicial de las matrices: la DIEM invita a
cuatrocientas personas cuyos registros existen pero cuyas cuentas no.

---

## `importacion`

Una fila por carga de matriz. Sostiene el ciclo de dos fases de
[`RF-A-49`][rf-a-49]: nada se crea hasta que el administrador confirma el resumen.

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 20-200 filas
- **Origen:**
  > - [`RF-A-49`][rf-a-49]

### Columnas

|        Campo         |      Tipo      | Nulo | Predeterminado |                      Descripción                      |
| :------------------: | :------------: | :--: | :------------: | :---------------------------------------------------: |
|       `matriz`       | `varchar(30)`  |  no  |                |                      Ver `CHECK`                      |
|   `archivo_nombre`   | `varchar(255)` |  no  |                |                                                       |
|    `archivo_hash`    | `varchar(64)`  |  no  |                | SHA-256; detecta la carga repetida del mismo archivo  |
|       `estado`       | `varchar(20)`  |  no  | `'analizada'`  | `analizada` / `confirmada` / `descartada` / `fallida` |
|   `filas_totales`    |   `integer`    |  no  |      `0`       |                                                       |
|  `filas_insertadas`  |   `integer`    |  no  |      `0`       |                                                       |
| `filas_actualizadas` |   `integer`    |  no  |      `0`       |                                                       |
|  `filas_rechazadas`  |   `integer`    |  no  |      `0`       |                                                       |
|     `subida_por`     |     `uuid`     |  no  |                |         Llave foránea `RESTRICT` a `usuario`          |
|    `analizada_at`    | `timestamptz`  |  no  |    `now()`     |                                                       |
|   `confirmada_at`    | `timestamptz`  |  sí  |                |                                                       |
|   `confirmada_por`   |     `uuid`     |  sí  |                |                                                       |

### Constraints

```postgresql
CONSTRAINT chk_importacion_matriz
CHECK (
  matriz IN ('estudiantes', 'participaciones', 'mentores', 'portafolio')
)

CONSTRAINT chk_importacion_estado
CHECK (estado IN ('analizada', 'confirmada', 'descartada', 'fallida'))

CONSTRAINT chk_importacion_confirmacion
CHECK ((confirmada_at IS NULL) = (confirmada_por IS NULL))

CONSTRAINT chk_importacion_suma_coherente
CHECK (
  filas_insertadas + filas_actualizadas + filas_rechazadas <= filas_totales
)
```

### Unicidad

|              Nombre               |                  Definición                  |                Propósito                |
| :-------------------------------: | :------------------------------------------: | :-------------------------------------: |
| `unq_importacion_hash_confirmada` | `(archivo_hash) WHERE estado = 'confirmada'` | El mismo archivo no se aplica dos veces |

---

## `importacion_fila`

Rastro fila por fila. Es lo que permite explicar por qué una fila de la hoja de
cálculo no llegó al sistema.

- **Régimen:** [`append-only`][auditoria], **alto volumen**
- **Volumen estimado:** 5,000-60,000 filas
- **Origen:**
  > - [`RF-A-49`][rf-a-49]

### Columnas

|      Campo       |      Tipo      | Nulo |                          Descripción                          |
| :--------------: | :------------: | :--: | :-----------------------------------------------------------: |
| `importacion_id` |     `uuid`     |  no  |                    Llave foránea `CASCADE`                    |
|  `numero_fila`   |   `integer`    |  no  |                  Número en la hoja original                   |
|   `resultado`    | `varchar(20)`  |  no  |     `insertada` / `actualizada` / `rechazada` / `omitida`     |
| `entidad_tabla`  | `varchar(60)`  |  no  |        `''` si fue rechazada antes de resolver destino        |
|   `entidad_id`   |     `uuid`     |  sí  |                                                               |
|     `motivo`     | `varchar(300)` |  no  |       Causa del rechazo, en lenguaje del administrador        |
|  `datos_crudos`  |    `jsonb`     |  no  | La fila tal como venía, incluidos los campos no interpretados |

### Unicidad

|            Nombre            |           Definición            |
| :--------------------------: | :-----------------------------: |
| `unq_importacionfila_numero` | `(importacion_id, numero_fila)` |

### Índices

|             Nombre              |                    Definición                    |      Propósito      |
| :-----------------------------: | :----------------------------------------------: | :-----------------: |
| `idx_importacionfila_rechazada` | `(importacion_id) WHERE resultado = 'rechazada'` | Informe de rechazos |

### Notas de diseño

`datos_crudos` conserva la fila íntegra, incluidos los campos que el importador no
supo interpretar. Es lo que rescata las certificaciones de mentor apiladas en una
celda, o la descripción de una actividad que no coincide con ningún catálogo:
nada de la matriz se pierde por no haber sido entendido en la primera pasada.

Es la única tabla del modelo que guarda deliberadamente datos sin normalizar, y
lo hace porque su función es documentar una migración, no sostener el dominio.

---

## `exportacion`

Registro de acceso a datos personales. La contrapartida de permitir descargar
listados.

- **Régimen:** [`append-only`][auditoria]
- **Volumen estimado:** 500-5,000 filas
- **Origen:**
  > - [`RF-A-46`][rf-a-46]
  > - [`RF-P-26`][rf-p-26]

### Columnas

|      Campo      |      Tipo      | Nulo | Predeterminado |               Descripción                |
| :-------------: | :------------: | :--: | :------------: | :--------------------------------------: |
|  `usuario_id`   |     `uuid`     |  no  |                |              Quién exportó               |
|    `alcance`    | `varchar(20)`  |  no  |                | `nominal` / `agregado` / `datos_propios` |
|    `recurso`    | `varchar(60)`  |  no  |                |            Listado exportado             |
|    `formato`    | `varchar(10)`  |  no  |    `'csv'`     |          `csv` / `xlsx` / `pdf`          |
|    `filtro`     |    `jsonb`     |  no  |     `'{}'`     |     Criterios aplicados, congelados      |
| `filas_totales` |   `integer`    |  no  |      `0`       |                                          |
|   `columnas`    |    `jsonb`     |  no  |     `'[]'`     |            Qué campos incluyó            |
|    `motivo`     | `varchar(200)` |  no  |      `''`      |      Obligatorio en alcance nominal      |
|      `ip`       |     `inet`     |  sí  |                |                                          |

### Constraints

```postgresql
CONSTRAINT chk_exportacion_alcance
CHECK (alcance IN ('nominal', 'agregado', 'datos_propios'))

CONSTRAINT chk_exportacion_motivo_nominal
CHECK (alcance <> 'nominal' OR length(motivo) > 0)
```

### Índices

|          Nombre           |                  Definición                   |               Propósito                |
| :-----------------------: | :-------------------------------------------: | :------------------------------------: |
| `idx_exportacion_usuario` |        `(usuario_id, created_at DESC)`        |      Qué ha descargado una cuenta      |
| `idx_exportacion_nominal` | `(created_at DESC) WHERE alcance = 'nominal'` | Revisión de accesos a datos personales |

### Notas de diseño

La distinción entre `nominal` y `agregado` es la que hace útil este registro. Una
exportación de conteos por facultad no expone a nadie; una lista de novecientos
estudiantes con nombre, correo y etnia autodeclarada sí. Registrarlas igual haría
que la revisión periódica tuviera que leer novecientas filas para encontrar las
tres que importan.

`datos_propios` cubre [`RF-P-26`][rf-p-26]: la persona descargando lo suyo queda
registrada como cualquier otro acceso, pero se distingue del administrador
descargando datos de terceros, que es una operación distinta aunque el mecanismo
sea el mismo.

El filtro se congela en `jsonb` porque _exportó el listado de participantes_ no
alcanza para una auditoría. Lo que importa es qué subconjunto: una actividad, un
año, una facultad, o todo.

[auditoria]: ../convenciones.md#auditoria-por-tabla
[r-09]: ../riesgos.md#r-09
[rf-a-04]: ../../requerimientos/funcionales/administracion.md#rf-a-04
[rf-a-23]: ../../requerimientos/funcionales/administracion.md#rf-a-23
[rf-a-46]: ../../requerimientos/funcionales/administracion.md#rf-a-46
[rf-a-49]: ../../requerimientos/funcionales/administracion.md#rf-a-49
[rf-a-50]: ../../requerimientos/funcionales/administracion.md#rf-a-50
[rf-p-06]: ../../requerimientos/funcionales/participantes.md#rf-p-06
[rf-p-26]: ../../requerimientos/funcionales/participantes.md#rf-p-26
[rn-16]: ../../requerimientos/reglas-negocio.md#rn-16
