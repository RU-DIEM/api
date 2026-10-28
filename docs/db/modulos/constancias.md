---
icon: lucide/award
---

# Constancias

Tres tablas en la app `rudi_constancias`: la plantilla, la constancia emitida y
el puente con las participaciones que ampara.

Una constancia es una afirmación institucional escrita. Todo el módulo está
construido alrededor de una consecuencia de eso: lo que la constancia dice se
congela al emitirse y no vuelve a depender del estado actual de nada
([`D-16`][d-16]).

## Requerimientos cubiertos

- [`RF-A-34`][rf-a-34]
- [`RF-A-35`][rf-a-35]
- [`RF-A-36`][rf-a-36]
- [`RF-P-23`][rf-p-23]
- [`RF-P-24`][rf-p-24]

---

## `plantilla_constancia`

- **Régimen:** [Mutable protegida][auditoria], rastreada
- **Volumen estimado:** 5-15 filas
- **Origen:**
  > - [`RF-A-34`][rf-a-34]

### Columnas

|        Campo        |      Tipo       | Nulo | Predeterminado |                  Descripción                  |
| :-----------------: | :-------------: | :--: | :------------: | :-------------------------------------------: |
|      `codigo`       |  `varchar(50)`  |  no  |                |  `participacion`, `finalizacion`, `mentoria`  |
|     `etiqueta`      | `varchar(120)`  |  no  |                |                                               |
|      `version`      |   `smallint`    |  no  |      `1`       |        Una fila por versión del texto         |
|      `cuerpo`       |     `text`      |  no  |                |      Texto con marcadores de sustitución      |
| `campos_requeridos` | `varchar(50)[]` |  no  |      `{}`      | Marcadores que la emisión debe poder resolver |
|   `firma_nombre`    | `varchar(150)`  |  no  |      `''`      |        Quien firma institucionalmente         |
|    `firma_cargo`    | `varchar(150)`  |  no  |      `''`      |                                               |
| `firma_imagen_url`  | `varchar(500)`  |  no  |      `''`      |                                               |
|   `vigente_desde`   |     `date`      |  no  |                |                                               |
|   `vigente_hasta`   |     `date`      |  sí  |                |             Nulo = versión en uso             |

### Unicidad

|                  Nombre                  |               Definición               |            Propósito             |
| :--------------------------------------: | :------------------------------------: | :------------------------------: |
| `unq_plantillaconstancia_codigo_version` |          `(codigo, version)`           | Cada versión consta por separado |
|    `unq_plantillaconstancia_vigente`     | `(codigo) WHERE vigente_hasta IS NULL` | Una sola versión en uso por tipo |

### Triggers

|                 Nombre                  |           Evento            | Momento  | Nivel |                                   Regla                                    |        Origen        |
| :-------------------------------------: | :-------------------------: | :------: | :---: | :------------------------------------------------------------------------: | :------------------: |
|      `trg_readonly_codigo_version`      | `UPDATE OF codigo, version` | `BEFORE` | `ROW` |                     El código y la versión no cambian                      |    [`D-08`][d-08]    |
| `trg_plantillaconstancia_version_nueva` |     `UPDATE OF cuerpo`      | `BEFORE` | `ROW` | Rechaza editar el cuerpo de una versión ya usada; obliga a crear una nueva | [`RF-A-34`][rf-a-34] |

### Notas de diseño

La plantilla se versiona en lugar de editarse porque [`RF-A-34`][rf-a-34] exige
que editar no altere lo ya emitido, y porque el mecanismo que lo garantiza no es
el versionado sino el congelado del contenido en `constancia`. El versionado
sirve para otra cosa: saber, ante una constancia de 2024, qué texto la produjo.

---

## `constancia`

- **Régimen:** [Mutable protegida][auditoria], rastreada
- **Volumen estimado:** 800-6,000 filas
- **Origen:**
  > - [`RF-A-35`][rf-a-35]
  > - [`RF-A-36`][rf-a-36]
  > - [`RN-15`][rn-15]

### Columnas

|           Campo           |      Tipo      | Nulo | Predeterminado |                          Descripción                          |
| :-----------------------: | :------------: | :--: | :------------: | :-----------------------------------------------------------: |
|          `folio`          | `varchar(30)`  |  no  |    asignado    | Único e irrepetible. `DIEM-2026-000412`; lo asigna el trigger |
|         `user_id`         |     `uuid`     |  no  |                |                            Persona                            |
|      `plantilla_id`       |     `uuid`     |  no  |                |                Versión concreta que se aplicó                 |
|        `estado_id`        |     `uuid`     |  no  |                |              Llave foránea a `estado_constancia`              |
|   `codigo_verificacion`   | `varchar(12)`  |  no  |                |             El que se teclea en la página pública             |
|    `nombre_congelado`     | `varchar(201)` |  no  |                |                  Nombre tal como se imprimió                  |
| `identificador_congelado` | `varchar(20)`  |  no  |      `''`      |               CIF o cédula tal como se imprimió               |
|   `contenido_congelado`   |    `jsonb`     |  no  |                |        Actividades, fechas, roles y horas, congelados         |
|     `texto_congelado`     |     `text`     |  no  |                |          Cuerpo ya sustituido, listo para reimprimir          |
|       `emitida_at`        | `timestamptz`  |  no  |    `now()`     |                                                               |
|     `emitida_por_id`      |     `uuid`     |  no  |                |                 Cuenta que emitió, `RESTRICT`                 |
|      `solicitada_at`      | `timestamptz`  |  sí  |                |     Con valor si nació de una solicitud del participante      |
|       `anulada_at`        | `timestamptz`  |  sí  |                |                                                               |
|        `motivo_id`        |     `uuid`     |  sí  |                |                     Obligatorio al anular                     |
|   `motivo_descripcion`    |     `text`     |  no  |      `''`      |                                                               |
|     `reemplaza_a_id`      |     `uuid`     |  sí  |                |     Apunta al folio anulado que esta constancia sustituye     |
|      `documento_url`      | `varchar(500)` |  no  |      `''`      |                                                               |

### Constraints

```postgresql
CONSTRAINT chk_constancia_folio_format
CHECK (folio ~ '^DIEM-[0-9]{4}-[0-9]{6}$')

CONSTRAINT chk_constancia_verificacion_format
CHECK (codigo_verificacion ~ '^[A-Z0-9]{8,12}$')

CONSTRAINT chk_constancia_anulacion
CHECK ((anulada_at IS NULL) = (motivo_id IS NULL))

CONSTRAINT chk_constancia_no_autoreemplazo
CHECK (reemplaza_a_id IS NULL OR reemplaza_a_id <> id)

CONSTRAINT chk_constancia_contenido
CHECK (jsonb_typeof(contenido_congelado) = 'object')
```

### Unicidad

|            Nombre             |                     Definición                      |                  Propósito                   |
| :---------------------------: | :-------------------------------------------------: | :------------------------------------------: |
|    `unq_constancia_folio`     |                      `(folio)`                      | Invariante crítico: el folio no se reutiliza |
| `unq_constancia_verificacion` |               `(codigo_verificacion)`               |    El código resuelve una sola constancia    |
|  `unq_constancia_reemplazo`   | `(reemplaza_a_id) WHERE reemplaza_a_id IS NOT NULL` |    Un folio anulado se reemplaza una vez     |

### Triggers

|               Nombre               |                     Evento                     | Momento  | Nivel |                                              Regla                                               |        Origen        |
| :--------------------------------: | :--------------------------------------------: | :------: | :---: | :----------------------------------------------------------------------------------------------: | :------------------: |
|   `trg_constancia_estado_activo`   |             `INSERT`<br/>`UPDATE`              | `BEFORE` | `ROW` |                               El estado asignado debe estar activo                               | [Familia][t-estado]  |
|  `trg_constancia_estado_terminal`  |         `UPDATE` con cambio de estado          | `BEFORE` | `ROW` |                              Una constancia anulada no vuelve atrás                              | [Familia][t-estado]  |
| `trg_constancia_estado_coherente`  | `INSERT`<br/>`UPDATE OF estado_id, anulada_at` | `BEFORE` | `ROW` |                       Una constancia anulada no está en un estado `valid`                        |    [`D-09`][d-09]    |
|      `trg_constancia_motivo`       |             `INSERT`<br/>`UPDATE`              | `BEFORE` | `ROW` | El motivo es de `anulacion_constancia`, o `anulacion_participacion` si la anuló la participación | [Familia][t-motivo]  |
|   `trg_constancia_folio_asignar`   |                    `INSERT`                    | `BEFORE` | `ROW` |                  Genera el folio desde una secuencia; ignora el valor recibido                   | [`RF-A-35`][rf-a-35] |
|      `trg_readonly_snapshot`       |                    `UPDATE`                    | `BEFORE` | `ROW` |           Folio, código, persona, plantilla, emisión y contenido congelado no cambian            |    [`D-16`][d-16]    |
| `trg_constancia_reemplazo_anulado` |    `INSERT`<br/>`UPDATE OF reemplaza_a_id`     | `BEFORE` | `ROW` |                           Exige que el folio reemplazado esté anulado                            | [`RF-A-36`][rf-a-36] |

### Índices

|        Nombre         |          Definición          |            Propósito            |
| :-------------------: | :--------------------------: | :-----------------------------: |
| `idx_constancia_user` | `(user_id, emitida_at DESC)` | Listado propio del participante |

### Notas de diseño

`contenido_congelado`, `nombre_congelado` y `texto_congelado` duplican datos que
existen en otras tablas, y esa duplicación es el punto. Una constancia impresa en
2024 dice el nombre que la persona tenía entonces y las actividades tal como se
llamaban entonces. Reconstruirla por unión con los datos actuales produciría, tres
años después, un documento distinto del que la persona tiene en la mano.

`codigo_verificacion` es independiente del folio porque el folio es correlativo y
adivinable. Exigir ambos impide que alguien recorra los folios de un año y liste
las constancias emitidas, que es lo que [`RF-P-24`][rf-p-24] prohíbe.

El folio sale de `rudiconstancias_folio_seq`, una secuencia única creada en la
migración de la app; el año del folio es el de emisión. La secuencia se consume
aunque la transacción falle, y eso es correcto: un hueco en la numeración es
inocuo, un folio repetido no lo es.

La solicitud de constancia de [`RF-P-23`][rf-p-23] no es una fila de esta tabla:
`emitida_at` no es nulable, de modo que una constancia solo existe emitida. La
cola de solicitudes queda para la capa de servicios.

---

## `constancia_participacion`

Puente que registra qué participaciones ampara cada constancia.

- **Régimen:** [`append-only`][auditoria]
- **Volumen estimado:** 1,200-10,000 filas
- **Origen:**
  > - [`RF-A-35`][rf-a-35]

|       Campo        |    Tipo    | Nulo |                  Descripción                  |
| :----------------: | :--------: | :--: | :-------------------------------------------: |
|  `constancia_id`   |   `uuid`   |  no  |           Llave foránea `RESTRICT`            |
| `participacion_id` |   `uuid`   |  no  |           Llave foránea `RESTRICT`            |
|      `orden`       | `smallint` |  no  | Posición en la que se imprime en el documento |

|               Nombre                |             Definición              |            Propósito             |
| :---------------------------------: | :---------------------------------: | :------------------------------: |
|  `unq_constanciaparticipacion_par`  | `(constancia_id, participacion_id)` | Una participación consta una vez |
| `unq_constanciaparticipacion_orden` |      `(constancia_id, orden)`       |     Sin empates en el orden      |

|                              Trigger                              |         Evento         | Momento  | Nivel |                                               Regla                                                |        Origen        |
| :---------------------------------------------------------------: | :--------------------: | :------: | :---: | :------------------------------------------------------------------------------------------------: | :------------------: |
|        `trg_constanciaparticipacion_participacion_valida`         |        `INSERT`        | `BEFORE` | `ROW` | La participación es de la misma persona, está validada, no anulada, y su estado `allow_constancia` |   [`RN-15`][rn-15]   |
| `trg_participacion_invalidar_constancias` (sobre `participacion`) | `UPDATE OF anulada_at` | `AFTER`  | `ROW` |                             Anula las constancias vivas que la amparan                             | [`RF-A-29`][rf-a-29] |

La relación es de muchos a muchos: [`RF-A-35`][rf-a-35] contempla el
consolidado que la persona pide al graduarse, con todas sus participaciones en un
solo documento, además de la constancia individual emitida en su momento. La
llave foránea indexada sobre `participacion_id` es la que hace operativa la
anulación en cascada de [`RF-A-29`][rf-a-29].

[auditoria]: ../convenciones.md#auditoria-por-tabla
[t-estado]: ../triggers.md#ciclo-de-vida-del-estado
[t-motivo]: ../triggers.md#motivo-de-lista-cerrada
[d-08]: ../decisiones.md#d-08
[d-09]: ../decisiones.md#d-09
[d-16]: ../decisiones.md#d-16
[rf-a-29]: ../../requerimientos/funcionales/administracion.md#rf-a-29
[rf-a-34]: ../../requerimientos/funcionales/administracion.md#rf-a-34
[rf-a-35]: ../../requerimientos/funcionales/administracion.md#rf-a-35
[rf-a-36]: ../../requerimientos/funcionales/administracion.md#rf-a-36
[rf-p-23]: ../../requerimientos/funcionales/participantes.md#rf-p-23
[rf-p-24]: ../../requerimientos/funcionales/participantes.md#rf-p-24
[rn-15]: ../../requerimientos/reglas-negocio.md#rn-15
