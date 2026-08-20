---
icon: lucide/coins
---

# Puntos de innovación

Dos tablas: el baremo con vigencia y el libro mayor de movimientos.

No existe una columna `puntos` en ninguna parte del modelo. El saldo de una
persona es la suma de sus movimientos vivos, y esa ausencia es la decisión
central del módulo, justificada en [`D-12`][d-12].

## Requerimientos cubiertos

- [`RF-A-30`][rf-a-30]
- [`RF-A-31`][rf-a-31]
- [`RF-A-32`][rf-a-32]
- [`RF-A-33`][rf-a-33]
- [`RF-P-22`][rf-p-22]

---

## `regla_puntuacion`

Baremo vigente por rango de fechas. Cambiar el baremo no altera lo ya otorgado.

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 30-150 filas
- **Origen:**
  > - [`RF-A-30`][rf-a-30]
  > - [`RN-09`][rn-09]

### Columnas

|           Campo           |      Tipo      | Nulo | Predeterminado |                       Descripción                       |
| :-----------------------: | :------------: | :--: | :------------: | :-----------------------------------------------------: |
|         `codigo`          | `varchar(50)`  |  no  |                |            Identificador estable de la regla            |
|        `etiqueta`         | `varchar(150)` |  no  |                |         Cómo se nombra en el detalle del saldo          |
|    `tipo_actividad_id`    |     `uuid`     |  sí  |                |             Nulo = aplica a cualquier tipo              |
|       `programa_id`       |     `uuid`     |  sí  |                |           Nulo = aplica a cualquier programa            |
|         `rol_id`          |     `uuid`     |  sí  |                |     Nulo = aplica a cualquier rol de participación      |
| `estado_participacion_id` |     `uuid`     |  sí  |                |   Desenlace exigido; nulo = cualquier estado efectivo   |
| `tipo_reconocimiento_id`  |     `uuid`     |  sí  |                | Exige un reconocimiento de ese tipo en la participación |
|         `puntos`          |   `smallint`   |  no  |                |                   Puede ser negativo                    |
|      `especificidad`      |   `smallint`   |  no  |    generada    |      **Almacenada**. Número de criterios no nulos       |
|        `vigencia`         |  `daterange`   |  no  |                |        Rango de vigencia, semiabierto por arriba        |
|         `activa`          |   `boolean`    |  no  |     `true`     |                                                         |

### Llaves foráneas

|          Columna          |       Referencia       | `ON DELETE` | Notas |
| :-----------------------: | :--------------------: | :---------: | :---: |
|    `tipo_actividad_id`    |    `tipo_actividad`    | `RESTRICT`  |       |
|       `programa_id`       |       `programa`       | `RESTRICT`  |       |
|         `rol_id`          |  `rol_participacion`   | `RESTRICT`  |       |
| `estado_participacion_id` | `estado_participacion` | `RESTRICT`  |       |
| `tipo_reconocimiento_id`  | `tipo_reconocimiento`  | `RESTRICT`  |       |

### Constraints

```postgresql
CONSTRAINT chk_reglapuntuacion_puntos_rango
CHECK (puntos BETWEEN -500 AND 500)

CONSTRAINT chk_reglapuntuacion_vigencia_no_vacia
CHECK (NOT isempty(vigencia))

CONSTRAINT chk_reglapuntuacion_criterio_minimo
CHECK (especificidad > 0)
```

### Unicidad

```postgresql
CONSTRAINT exc_reglapuntuacion_vigencia
EXCLUDE USING gist (
  coalesce(tipo_actividad_id, '00000000-0000-0000-0000-000000000000'::uuid) WITH =,
  coalesce(programa_id,       '00000000-0000-0000-0000-000000000000'::uuid) WITH =,
  coalesce(rol_id,            '00000000-0000-0000-0000-000000000000'::uuid) WITH =,
  coalesce(estado_participacion_id, '00000000-0000-0000-0000-000000000000'::uuid) WITH =,
  coalesce(tipo_reconocimiento_id,  '00000000-0000-0000-0000-000000000000'::uuid) WITH =,
  vigencia WITH &&
) WHERE (activa)
```

|            Nombre            | Definición |
| :--------------------------: | :--------: |
| `unq_reglapuntuacion_codigo` | `(codigo)` |

### Índices

|              Nombre              |             Definición              |              Propósito               |
| :------------------------------: | :---------------------------------: | :----------------------------------: |
| `idx_reglapuntuacion_resolucion` | `(especificidad DESC) WHERE activa` |   Orden de resolución de la regla    |
| `gist_reglapuntuacion_vigencia`  |       `(vigencia) USING gist`       | Filtro por fecha de la participación |

### Resolución de la regla aplicable

Al validar una participación pueden coincidir varias reglas. El orden es fijo y
no admite empate:

1. Si la actividad declara `puntos_base`, prevalece y no se consulta el baremo.
1. Entre las reglas activas cuya `vigencia` contiene la fecha de la
   participación y cuyos criterios no nulos coinciden, gana la de mayor
   `especificidad`.
1. Si dos reglas empatan en especificidad, la restricción de exclusión ya impidió
   que ambas existieran a la vez.
1. Si ninguna aplica, la participación se valida con cero puntos y aparece en la
   lista de revisión de [`RF-A-31`][rf-a-31].

### Notas de diseño

`especificidad` es columna generada y almacenada porque el orden de resolución la
consulta en cada validación y calcularla al vuelo obligaría a contar nulos en
cinco columnas dentro del `ORDER BY`.

La restricción de exclusión es lo que convierte _no debería haber dos reglas
solapadas_ en algo que la base de datos impide. La alternativa —comprobarlo al
guardar desde la interfaz— falla exactamente cuando dos administradores editan el
baremo el mismo día, que es cuando el solape se produce.

El `coalesce` a un UUID de ceros dentro de la exclusión existe porque `NULL` no es
igual a `NULL` bajo `WITH =`: sin él, dos reglas genéricas idénticas y vigentes a
la vez no colisionarían, que es justo el caso más peligroso.

`vigencia` es `daterange` y no dos columnas de fecha porque los operadores de
solape de PostgreSQL trabajan sobre rangos y la restricción de exclusión los
exige. El uso previsto es semiabierto: `[2026-01-01,)` para la regla vigente sin
fecha de término.

Reglas con `puntos` negativos son legítimas: la matriz de participaciones
contempla el desenlace _no completó_, y la DIEM puede decidir que descuente.

---

## `movimiento_punto`

Libro mayor. Cada fila es un asiento y ninguna se edita ni se borra.

- **Régimen:** [`append-only`][auditoria]
- **Volumen estimado:** 4,000-25,000 filas
- **Origen:**
  > - [`RF-A-31`][rf-a-31]
  > - [`RF-A-32`][rf-a-32]
  > - [`RF-A-33`][rf-a-33]
  > - [`RN-08`][rn-08]

### Columnas

|       Campo        |      Tipo      | Nulo | Predeterminado |                      Descripción                       |
| :----------------: | :------------: | :--: | :------------: | :----------------------------------------------------: |
|    `usuario_id`    |     `uuid`     |  no  |                |                     Llave foránea                      |
| `participacion_id` |     `uuid`     |  sí  |                |     Nulo en los ajustes manuales sin participación     |
|     `regla_id`     |     `uuid`     |  sí  |                |         Con valor solo en el origen automático         |
|      `puntos`      |   `smallint`   |  no  |                |                 Con signo. Nunca cero                  |
|      `origen`      | `varchar(20)`  |  no  |                |  `automatico` / `manual` / `reverso` / `importacion`   |
|    `motivo_id`     |     `uuid`     |  sí  |                |         Obligatorio en `manual` y en `reverso`         |
|   `descripcion`    | `varchar(300)` |  no  |      `''`      |    Lo que la persona lee en el detalle de su saldo     |
|   `revierte_id`    |     `uuid`     |  sí  |                | Con valor solo en `reverso`; apunta al asiento anulado |
|   `revertido_at`   | `timestamptz`  |  sí  |                |           Lo fija el asiento que lo revierte           |
|  `registrado_por`  |     `uuid`     |  sí  |                |     Nulo cuando el actor es el motor de validación     |
|       `anio`       |   `smallint`   |  no  |                |      Año de reporte, copiado de la participación       |

### Llaves foráneas

|      Columna       |     Referencia     | `ON DELETE` |                    Notas                    |
| :----------------: | :----------------: | :---------: | :-----------------------------------------: |
|    `usuario_id`    |     `usuario`      | `RESTRICT`  |        La fusión traslada, no borra         |
| `participacion_id` |  `participacion`   | `RESTRICT`  |                                             |
|     `regla_id`     | `regla_puntuacion` | `RESTRICT`  | Una regla citada por un asiento no se borra |
|    `motivo_id`     |      `motivo`      | `RESTRICT`  |          De ámbito `ajuste_puntos`          |
|   `revierte_id`    | `movimiento_punto` | `RESTRICT`  |               Autorreferencia               |
|  `registrado_por`  |     `usuario`      | `RESTRICT`  |                                             |

### Constraints

```postgresql
CONSTRAINT chk_movimientopunto_origen
CHECK (origen IN ('automatico', 'manual', 'reverso', 'importacion'))

CONSTRAINT chk_movimientopunto_puntos_no_cero
CHECK (puntos <> 0)

CONSTRAINT chk_movimientopunto_regla_automatica
CHECK ((origen = 'automatico') = (regla_id IS NOT NULL))

CONSTRAINT chk_movimientopunto_reverso_coherente
CHECK ((origen = 'reverso') = (revierte_id IS NOT NULL))

CONSTRAINT chk_movimientopunto_motivo_requerido
CHECK (origen NOT IN ('manual', 'reverso') OR motivo_id IS NOT NULL)

CONSTRAINT chk_movimientopunto_no_autorreverso
CHECK (revierte_id IS DISTINCT FROM id)
```

### Unicidad

|              Nombre              |                         Definición                         |                 Propósito                  |
| :------------------------------: | :--------------------------------------------------------: | :----------------------------------------: |
|  `unq_movimientopunto_reverso`   |       `(revierte_id) WHERE revierte_id IS NOT NULL`        |    Un asiento se revierte una sola vez     |
| `unq_movimientopunto_automatico` | `(participacion_id, regla_id) WHERE origen = 'automatico'` | La validación no otorga dos veces lo mismo |

### Triggers

|                 Nombre                  |  Evento  | Momento  | Nivel |                              Regla                               |        Origen        |
| :-------------------------------------: | :------: | :------: | :---: | :--------------------------------------------------------------: | :------------------: |
|     `trg_movimientopunto_inmutable`     | `UPDATE` | `BEFORE` | `ROW` | Solo admite fijar `revertido_at`; rechaza cualquier otro cambio  | [`RF-A-33`][rf-a-33] |
|     `trg_movimientopunto_no_borrar`     | `DELETE` | `BEFORE` | `ROW` |                        Bloquea el borrado                        | [`RF-A-50`][rf-a-50] |
| `trg_movimientopunto_marcar_revertido`  | `INSERT` | `AFTER`  | `ROW` |            Fija `revertido_at` en el asiento original            | [`RF-A-33`][rf-a-33] |
|  `trg_movimientopunto_reverso_exacto`   | `INSERT` | `BEFORE` | `ROW` | En `reverso`, exige signo contrario y magnitud igual al original |   [`RN-08`][rn-08]   |
| `trg_movimientopunto_usuario_coherente` | `INSERT` | `BEFORE` | `ROW` |     Exige que la participación pertenezca a la misma persona     | [`RF-A-31`][rf-a-31] |

### Índices

|                Nombre                 |                            Definición                             |                         Propósito                         |
| :-----------------------------------: | :---------------------------------------------------------------: | :-------------------------------------------------------: |
|  `idx_movimientopunto_usuario_vivo`   | `(usuario_id) WHERE revertido_at IS NULL AND origen <> 'reverso'` |                 Cálculo del saldo vigente                 |
| `idx_movimientopunto_usuario_detalle` |                  `(usuario_id, created_at DESC)`                  |              Detalle de [`RF-P-22`][rf-p-22]              |
|  `idx_movimientopunto_participacion`  |      `(participacion_id) WHERE participacion_id IS NOT NULL`      |            Reverso al anular la participación             |
|   `idx_movimientopunto_anio_origen`   |                         `(anio, origen)`                          | Separación de automático y manual en [`RF-A-32`][rf-a-32] |

### El saldo

```postgresql
SELECT coalesce(sum(puntos), 0) AS saldo
FROM movimiento_punto
WHERE usuario_id = $1
  AND revertido_at IS NULL
  AND origen <> 'reverso';
```

El filtro doble no es redundante: excluye el asiento original que fue revertido
**y** el asiento de reverso que lo anuló. Sumar ambos daría el mismo resultado
—se cancelan—, pero contarlos separadamente permite que la vista de detalle
muestre los dos y explique la corrección, que es lo que [`RF-P-22`][rf-p-22] pide.

### Notas de diseño

Un saldo almacenado en `usuario` sería más rápido de leer y estaría equivocado el
primer día en que un `UPDATE` fallara a mitad. El libro mayor no puede
desincronizarse de sí mismo: es la única fuente.

`trg_movimientopunto_reverso_exacto` impide el reverso parcial. Corregir cinco
puntos otorgados de más no es revertir cinco: es revertir el asiento completo y
emitir uno manual con el valor correcto, de modo que el rastro diga qué pasó en
lugar de dejar un asiento a medio anular.

`participacion_id` nulable admite el ajuste manual puro —puntos por representar a
la Universidad en un espacio que no se modeló como actividad— que
[`RF-A-32`][rf-a-32] contempla explícitamente.

`anio` se copia igual que en `participacion` y por la misma razón: el reporte
anual de puntos no debe unir tres tablas para saber a qué año pertenece un
asiento.

[auditoria]: ../convenciones.md#auditoria-por-tabla
[d-12]: ../decisiones.md#d-12
[rf-a-30]: ../../requerimientos/funcionales/administracion.md#rf-a-30
[rf-a-31]: ../../requerimientos/funcionales/administracion.md#rf-a-31
[rf-a-32]: ../../requerimientos/funcionales/administracion.md#rf-a-32
[rf-a-33]: ../../requerimientos/funcionales/administracion.md#rf-a-33
[rf-a-50]: ../../requerimientos/funcionales/administracion.md#rf-a-50
[rf-p-22]: ../../requerimientos/funcionales/participantes.md#rf-p-22
[rn-08]: ../../requerimientos/reglas-negocio.md#rn-08
[rn-09]: ../../requerimientos/reglas-negocio.md#rn-09
