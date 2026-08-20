---
icon: lucide/award
---

# Constancias

Tres tablas: la plantilla, la constancia emitida y el puente con las
participaciones que ampara.

Una constancia es una afirmación institucional escrita. Todo el módulo está
construido alrededor de una consecuencia de eso: lo que la constancia dice se
congela al emitirse y no vuelve a depender del estado actual de nada.

## Requerimientos cubiertos

- [`RF-A-34`][rf-a-34]
- [`RF-A-35`][rf-a-35]
- [`RF-A-36`][rf-a-36]
- [`RF-P-23`][rf-p-23]
- [`RF-P-24`][rf-p-24]

---

## `plantilla_constancia`

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 5-15 filas
- **Origen:**
  > - [`RF-A-34`][rf-a-34]

### Columnas

|        Campo        |      Tipo      | Nulo | Predeterminado |                  Descripción                  |
| :-----------------: | :------------: | :--: | :------------: | :-------------------------------------------: |
|      `codigo`       | `varchar(50)`  |  no  |                |  `participacion`, `finalizacion`, `mentoria`  |
|     `etiqueta`      | `varchar(120)` |  no  |                |                                               |
|      `version`      |   `smallint`   |  no  |      `1`       |       Se incrementa al editar el cuerpo       |
|      `cuerpo`       |     `text`     |  no  |                |      Texto con marcadores de sustitución      |
| `campos_requeridos` |    `jsonb`     |  no  |     `'[]'`     | Marcadores que la emisión debe poder resolver |
|   `firma_nombre`    | `varchar(150)` |  no  |      `''`      |        Quien firma institucionalmente         |
|    `firma_cargo`    | `varchar(150)` |  no  |      `''`      |                                               |
| `firma_imagen_url`  | `varchar(500)` |  no  |      `''`      |                                               |
|   `vigente_desde`   |     `date`     |  no  |                |                                               |
|   `vigente_hasta`   |     `date`     |  sí  |                |             Nulo = versión en uso             |
|      `activa`       |   `boolean`    |  no  |     `true`     |                                               |

### Unicidad

|                  Nombre                  |                    Definición                     |            Propósito             |
| :--------------------------------------: | :-----------------------------------------------: | :------------------------------: |
| `unq_plantillaconstancia_codigo_version` |                `(codigo, version)`                | Cada versión consta por separado |
|    `unq_plantillaconstancia_vigente`     | `(codigo) WHERE vigente_hasta IS NULL AND activa` | Una sola versión en uso por tipo |

### Triggers

|                 Nombre                  |       Evento       | Momento  | Nivel |                                   Regla                                    |        Origen        |
| :-------------------------------------: | :----------------: | :------: | :---: | :------------------------------------------------------------------------: | :------------------: |
| `trg_plantillaconstancia_version_nueva` | `UPDATE OF cuerpo` | `BEFORE` | `ROW` | Rechaza editar el cuerpo de una versión ya usada; obliga a crear una nueva | [`RF-A-34`][rf-a-34] |

### Notas de diseño

La plantilla se versiona en lugar de editarse porque [`RF-A-34`][rf-a-34] exige
que editar no altere lo ya emitido, y porque el mecanismo que lo garantiza no es
el versionado sino el congelado del contenido en `constancia`. El versionado
sirve para otra cosa: saber, ante una constancia de 2024, qué texto la produjo.

`campos_requeridos` enumera los marcadores que la plantilla usa. La emisión
comprueba que puede resolverlos todos antes de generar el folio, de modo que una
plantilla que pide el nombre de la carrera nunca se aplique a un participante
externo y produzca una constancia con un hueco.

---

## `constancia`

- **Régimen:** [Mutable protegida][auditoria], **no se borra**
- **Volumen estimado:** 800-6,000 filas
- **Origen:**
  > - [`RF-A-35`][rf-a-35]
  > - [`RF-A-36`][rf-a-36]
  > - [`RN-15`][rn-15]

### Columnas

|           Campo           |      Tipo      | Nulo | Predeterminado |                      Descripción                      |
| :-----------------------: | :------------: | :--: | :------------: | :---------------------------------------------------: |
|          `folio`          | `varchar(30)`  |  no  |                |        Único e irrepetible. `DIEM-2026-000412`        |
|       `usuario_id`        |     `uuid`     |  no  |                |                     Llave foránea                     |
|      `plantilla_id`       |     `uuid`     |  no  |                |            Versión concreta que se aplicó             |
|        `estado_id`        |     `uuid`     |  no  |                |          Llave foránea a `estado_constancia`          |
|   `codigo_verificacion`   | `varchar(12)`  |  no  |                |         El que se teclea en la página pública         |
|    `nombre_congelado`     | `varchar(201)` |  no  |                |              Nombre tal como se imprimió              |
| `identificador_congelado` | `varchar(20)`  |  no  |                |           CIF o cédula tal como se imprimió           |
|   `contenido_congelado`   |    `jsonb`     |  no  |                |    Actividades, fechas, roles y horas, congelados     |
|     `texto_congelado`     |     `text`     |  no  |                |      Cuerpo ya sustituido, listo para reimprimir      |
|       `emitida_at`        | `timestamptz`  |  no  |    `now()`     |                                                       |
|       `emitida_por`       |     `uuid`     |  no  |                |         Llave foránea `RESTRICT` a `usuario`          |
|      `solicitada_at`      | `timestamptz`  |  sí  |                | Con valor si nació de una solicitud del participante  |
|       `anulada_at`        | `timestamptz`  |  sí  |                |                                                       |
|        `motivo_id`        |     `uuid`     |  sí  |                |                 Obligatorio al anular                 |
|     `reemplaza_a_id`      |     `uuid`     |  sí  |                | Apunta al folio anulado que esta constancia sustituye |
|      `documento_url`      | `varchar(500)` |  no  |      `''`      |                                                       |

### Llaves foráneas

|     Columna      |       Referencia       | `ON DELETE` |                     Notas                     |
| :--------------: | :--------------------: | :---------: | :-------------------------------------------: |
|   `usuario_id`   |       `usuario`        | `RESTRICT`  |                                               |
|  `plantilla_id`  | `plantilla_constancia` | `RESTRICT`  |       La plantilla citada no desaparece       |
|   `estado_id`    |  `estado_constancia`   | `RESTRICT`  |                                               |
|  `emitida_por`   |       `usuario`        | `RESTRICT`  | El folio debe seguir nombrando a quien emitió |
|   `motivo_id`    |        `motivo`        | `RESTRICT`  |       De ámbito `anulacion_constancia`        |
| `reemplaza_a_id` |      `constancia`      | `RESTRICT`  |                Autorreferencia                |

### Constraints

```postgresql
CONSTRAINT chk_constancia_folio_formato
CHECK (folio ~ '^DIEM-[0-9]{4}-[0-9]{6}$')

CONSTRAINT chk_constancia_verificacion_formato
CHECK (codigo_verificacion ~ '^[A-Z0-9]{8,12}$')

CONSTRAINT chk_constancia_anulacion
CHECK ((anulada_at IS NULL) = (motivo_id IS NULL))

CONSTRAINT chk_constancia_no_autoreemplazo
CHECK (reemplaza_a_id IS DISTINCT FROM id)

CONSTRAINT chk_constancia_contenido_no_vacio
CHECK (jsonb_typeof(contenido_congelado) = 'object')
```

### Unicidad

|            Nombre             |                     Definición                      |                  Propósito                   |
| :---------------------------: | :-------------------------------------------------: | :------------------------------------------: |
|    `unq_constancia_folio`     |                      `(folio)`                      | Invariante crítico: el folio no se reutiliza |
| `unq_constancia_verificacion` |               `(codigo_verificacion)`               |    El código resuelve una sola constancia    |
|  `unq_constancia_reemplazo`   | `(reemplaza_a_id) WHERE reemplaza_a_id IS NOT NULL` |    Un folio anulado se reemplaza una vez     |

### Triggers

|                Nombre                 |                Evento                | Momento  | Nivel |                                             Regla                                             |        Origen        |
| :-----------------------------------: | :----------------------------------: | :------: | :---: | :-------------------------------------------------------------------------------------------: | :------------------: |
|    `trg_constancia_folio_asignar`     |               `INSERT`               | `BEFORE` | `ROW` |       Genera el folio correlativo del año desde una secuencia; ignora el valor recibido       | [`RF-A-35`][rf-a-35] |
|  `trg_constancia_congelado_readonly`  |               `UPDATE`               | `BEFORE` | `ROW` |             Rechaza cambios en folio, código, campos congelados y `plantilla_id`              |    [`D-16`][d-16]    |
| `trg_constancia_participacion_valida` |               `INSERT`               | `BEFORE` | `ROW` | Exige que toda participación amparada esté validada y su estado declare `habilita_constancia` |   [`RN-15`][rn-15]   |
|  `trg_constancia_reemplazo_anulado`   | `INSERT`, `UPDATE OF reemplaza_a_id` | `BEFORE` | `ROW` |                          Exige que el folio reemplazado esté anulado                          | [`RF-A-36`][rf-a-36] |
|      `trg_constancia_no_borrar`       |               `DELETE`               | `BEFORE` | `ROW` |                                      Bloquea el borrado                                       | [`RF-A-50`][rf-a-50] |

### Índices

|            Nombre             |                 Definición                 |                   Propósito                    |
| :---------------------------: | :----------------------------------------: | :--------------------------------------------: |
|   `idx_constancia_usuario`    |      `(usuario_id, emitida_at DESC)`       |        Listado propio del participante         |
| `idx_constancia_emitida_anio` |     `(date_trunc('year', emitida_at))`     |            Reporte anual de emisión            |
|  `idx_constancia_pendiente`   | `(solicitada_at) WHERE emitida_at IS NULL` | Bandeja de solicitudes de [`RF-P-23`][rf-p-23] |

### Notas de diseño

`contenido_congelado`, `nombre_congelado` y `texto_congelado` duplican datos que
existen en otras tablas, y esa duplicación es el punto. Una constancia impresa en
2024 dice el nombre que la persona tenía entonces y las actividades tal como se
llamaban entonces. Reconstruirla por unión con los datos actuales produciría, tres
años después, un documento distinto del que la persona tiene en la mano.

El caso decisivo es la anulación de una participación amparada. La constancia
queda anulada por [`RF-A-29`][rf-a-29], pero la verificación pública tiene que
seguir mostrando qué decía ese folio para poder afirmar que dejó de tener validez.
Sin el congelado no habría qué mostrar.

`codigo_verificacion` es independiente del folio porque el folio es correlativo y
adivinable. Exigir ambos impide que alguien recorra los folios de un año y liste
las constancias emitidas, que es lo que [`RF-P-24`][rf-p-24] prohíbe.

La secuencia de folios se consume aunque la transacción falle, y eso es correcto:
un hueco en la numeración es inocuo, un folio repetido no lo es.

---

## `constancia_participacion`

Puente que registra qué participaciones ampara cada constancia.

- **Régimen:** [Mutable protegida][auditoria], **no se borra**
- **Volumen estimado:** 1,200-10,000 filas
- **Origen:**
  > - [`RF-A-35`][rf-a-35]

### Columnas

|       Campo        |    Tipo    | Nulo |                  Descripción                  |
| :----------------: | :--------: | :--: | :-------------------------------------------: |
|  `constancia_id`   |   `uuid`   |  no  |           Llave foránea `RESTRICT`            |
| `participacion_id` |   `uuid`   |  no  |           Llave foránea `RESTRICT`            |
|      `orden`       | `smallint` |  no  | Posición en la que se imprime en el documento |

### Unicidad

|              Nombre               |             Definición              |            Propósito             |
| :-------------------------------: | :---------------------------------: | :------------------------------: |
| `unq_constanciaparticipacion_par` | `(constancia_id, participacion_id)` | Una participación consta una vez |

### Índices

|                   Nombre                    |      Definición      |                     Propósito                     |
| :-----------------------------------------: | :------------------: | :-----------------------------------------------: |
| `idx_constanciaparticipacion_participacion` | `(participacion_id)` | Localizar las constancias que invalidar al anular |

### Notas de diseño

La relación es de muchos a muchos y no de una a una. [`RF-A-35`][rf-a-35]
contempla el consolidado que la persona pide al graduarse, con todas sus
participaciones en un solo documento; y una misma participación puede aparecer en
la constancia individual que se emitió en su momento y en ese consolidado
posterior.

Es el índice sobre `participacion_id` el que hace operativa la anulación en
cascada de [`RF-A-29`][rf-a-29]: anulada una participación, resolver qué folios
quedan invalidados es una búsqueda directa y no un recorrido del `jsonb` congelado
de cada constancia.

[auditoria]: ../convenciones.md#auditoria-por-tabla
[d-16]: ../decisiones.md#d-16
[rf-a-29]: ../../requerimientos/funcionales/administracion.md#rf-a-29
[rf-a-34]: ../../requerimientos/funcionales/administracion.md#rf-a-34
[rf-a-35]: ../../requerimientos/funcionales/administracion.md#rf-a-35
[rf-a-36]: ../../requerimientos/funcionales/administracion.md#rf-a-36
[rf-a-50]: ../../requerimientos/funcionales/administracion.md#rf-a-50
[rf-p-23]: ../../requerimientos/funcionales/participantes.md#rf-p-23
[rf-p-24]: ../../requerimientos/funcionales/participantes.md#rf-p-24
[rn-15]: ../../requerimientos/reglas-negocio.md#rn-15
