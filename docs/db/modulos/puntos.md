---
icon: lucide/coins
---

# Puntos de innovación

Dos tablas en la app `rudi_puntos`: el baremo con vigencia y el libro mayor de
movimientos.

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

- **Régimen:** [Mutable rastreada][auditoria]
- **Volumen estimado:** 30-150 filas
- **Origen:**
  > - [`RF-A-30`][rf-a-30]
  > - [`RN-09`][rn-09]

### Columnas

|           Campo           |      Tipo      | Nulo | Predeterminado |                          Descripción                          |
| :-----------------------: | :------------: | :--: | :------------: | :-----------------------------------------------------------: |
|         `codigo`          | `varchar(50)`  |  no  |                |               Identificador estable de la regla               |
|        `etiqueta`         | `varchar(150)` |  no  |                |            Cómo se nombra en el detalle del saldo             |
|    `tipo_actividad_id`    |     `uuid`     |  sí  |                |                Nulo = aplica a cualquier tipo                 |
|       `programa_id`       |     `uuid`     |  sí  |                |              Nulo = aplica a cualquier programa               |
|         `rol_id`          |     `uuid`     |  sí  |                |        Nulo = aplica a cualquier rol de participación         |
| `estado_participacion_id` |     `uuid`     |  sí  |                | Desenlace exigido; nulo = cualquier estado con `allow_puntos` |
| `tipo_reconocimiento_id`  |     `uuid`     |  sí  |                |    Exige un reconocimiento de ese tipo en la participación    |
|         `puntos`          |   `smallint`   |  no  |                |                      Puede ser negativo                       |
|      `especificidad`      |   `smallint`   |  no  |    generada    |         **Almacenada**. Número de criterios no nulos          |
|        `vigencia`         |  `daterange`   |  no  |                |           Rango de vigencia, semiabierto por arriba           |
|        `is_active`        |   `boolean`    |  no  |     `true`     |                                                               |

### Constraints

```postgresql
CONSTRAINT chk_reglapuntuacion_puntos_rango
CHECK (puntos BETWEEN -500 AND 500)

CONSTRAINT chk_reglapuntuacion_vigencia
CHECK (NOT isempty(vigencia))

CONSTRAINT chk_reglapuntuacion_criterio_minimo
CHECK (
  tipo_actividad_id IS NOT NULL
  OR programa_id IS NOT NULL
  OR rol_id IS NOT NULL
  OR estado_participacion_id IS NOT NULL
  OR tipo_reconocimiento_id IS NOT NULL
)
```

### Unicidad

```postgresql
CONSTRAINT excl_reglapuntuacion_vigencia
EXCLUDE USING gist (
  coalesce(tipo_actividad_id,       '00000000-0000-0000-0000-000000000000') WITH =,
  coalesce(programa_id,             '00000000-0000-0000-0000-000000000000') WITH =,
  coalesce(rol_id,                  '00000000-0000-0000-0000-000000000000') WITH =,
  coalesce(estado_participacion_id, '00000000-0000-0000-0000-000000000000') WITH =,
  coalesce(tipo_reconocimiento_id,  '00000000-0000-0000-0000-000000000000') WITH =,
  vigencia WITH &&
) WHERE (is_active)
```

`btree_gist` se instala en la primera migración de la app: es lo que permite
`WITH =` sobre `uuid` dentro de un índice GiST.

|            Nombre            | Definición |
| :--------------------------: | :--------: |
| `unq_reglapuntuacion_codigo` | `(codigo)` |

### Índices

|              Nombre              |               Definición               |              Propósito               |
| :------------------------------: | :------------------------------------: | :----------------------------------: |
| `idx_reglapuntuacion_resolucion` | `(especificidad DESC) WHERE is_active` |   Orden de resolución de la regla    |
| `gist_reglapuntuacion_vigencia`  |        `(vigencia) USING gist`         | Filtro por fecha de la participación |

### Triggers

|                Nombre                 |       Evento       | Momento  | Nivel |                 Regla                  |        Origen         |
| :-----------------------------------: | :----------------: | :------: | :---: | :------------------------------------: | :-------------------: |
|         `trg_readonly_codigo`         | `UPDATE OF codigo` | `BEFORE` | `ROW` |  Rechaza cualquier cambio de `codigo`  |    [`D-08`][d-08]     |
| `trg_reglapuntuacion_catalogo_activo` |      `INSERT`      | `BEFORE` | `ROW` | Cada criterio citado debe estar activo | [Familia][t-catalogo] |

`trg_touch_updatedat` excluye `especificidad` de su condición: PostgreSQL no
admite columnas generadas en la condición de un trigger `BEFORE`.

### Resolución de la regla aplicable

Al validar una participación, `trg_participacion_otorgar_puntos` aplica este
orden, fijo y sin empate:

1. Si el estado de la participación no declara `allow_puntos`, no se otorga
   nada.
1. Si la actividad declara `puntos_base`, prevalece y no se consulta el baremo:
   el movimiento es automático sin `regla_id`.
1. Entre las reglas activas cuya `vigencia` contiene la fecha de validación y
   cuyos criterios no nulos coinciden, gana la de mayor `especificidad`.
1. Si dos reglas empatan en especificidad, la restricción de exclusión ya impidió
   que ambas existieran a la vez.
1. Si ninguna aplica, la participación se valida sin puntos y aparece en la
   lista de revisión de [`RF-A-31`][rf-a-31].

### Notas de diseño

La restricción de exclusión es lo que convierte _no debería haber dos reglas
solapadas_ en algo que la base de datos impide. La alternativa —comprobarlo al
guardar desde la interfaz— falla exactamente cuando dos administradores editan el
baremo el mismo día.

El `coalesce` a un UUID de ceros existe porque `NULL` no es igual a `NULL` bajo
`WITH =`: sin él, dos reglas genéricas idénticas y vigentes a la vez no
colisionarían, que es justo el caso más peligroso.

Reglas con `puntos` negativos son legítimas: la matriz de participaciones
contempla el desenlace _no completó_, y la DIEM puede decidir que descuente.

---

## `movimiento_punto`

Libro mayor. Cada fila es un asiento y ninguna se edita ni se borra.

- **Régimen:** [Mutable protegida][auditoria] con todas las columnas de solo
  lectura salvo `revertido_at`; sin tabla de eventos, porque el libro ya es su
  propio historial
- **Volumen estimado:** 4,000-25,000 filas
- **Origen:**
  > - [`RF-A-31`][rf-a-31]
  > - [`RF-A-32`][rf-a-32]
  > - [`RF-A-33`][rf-a-33]
  > - [`RN-08`][rn-08]

### Columnas

|        Campo        |      Tipo      | Nulo | Predeterminado |                     Descripción                     |
| :-----------------: | :------------: | :--: | :------------: | :-------------------------------------------------: |
|      `user_id`      |     `uuid`     |  no  |                |   Persona; copiada de la participación si la hay    |
| `participacion_id`  |     `uuid`     |  sí  |                |   Nulo en los ajustes manuales sin participación    |
|     `regla_id`      |     `uuid`     |  sí  |                |            Solo en el origen automático             |
|      `puntos`       |   `smallint`   |  no  |                |                Con signo. Nunca cero                |
|      `origen`       | `varchar(20)`  |  no  |                | `automatico` / `manual` / `reverso` / `importacion` |
|     `motivo_id`     |     `uuid`     |  sí  |                |       Obligatorio en `manual` y en `reverso`        |
|    `descripcion`    | `varchar(300)` |  no  |      `''`      |   Lo que la persona lee en el detalle de su saldo   |
|    `revierte_id`    |     `uuid`     |  sí  |                |    Solo en `reverso`; apunta al asiento anulado     |
|   `revertido_at`    | `timestamptz`  |  sí  |                |         Lo fija el asiento que lo revierte          |
| `registrado_por_id` |     `uuid`     |  sí  |                |   Nulo cuando el actor es el motor de validación    |
|       `anio`        |   `smallint`   |  no  |                |     Año de reporte, copiado de la participación     |

### Constraints

```postgresql
CONSTRAINT chk_movimientopunto_origen
CHECK (origen IN ('automatico', 'importacion', 'manual', 'reverso'))

CONSTRAINT chk_movimientopunto_puntos_no_cero
CHECK (puntos <> 0)

CONSTRAINT chk_movimientopunto_regla_automatica
CHECK (regla_id IS NULL OR origen = 'automatico')

CONSTRAINT chk_movimientopunto_reverso_coherente
CHECK ((origen = 'reverso') = (revierte_id IS NOT NULL))

CONSTRAINT chk_movimientopunto_motivo_requerido
CHECK (origen NOT IN ('manual', 'reverso') OR motivo_id IS NOT NULL)

CONSTRAINT chk_movimientopunto_no_autorreverso
CHECK (revierte_id IS NULL OR revierte_id <> id)
```

### Unicidad

|              Nombre              |                    Definición                    |              Propósito              |
| :------------------------------: | :----------------------------------------------: | :---------------------------------: |
|  `unq_movimientopunto_reverso`   |  `(revierte_id) WHERE revierte_id IS NOT NULL`   | Un asiento se revierte una sola vez |
| `unq_movimientopunto_automatico` | `(participacion_id) WHERE origen = 'automatico'` |  La validación no otorga dos veces  |

### Triggers

|                 Nombre                 |        Evento         | Momento  | Nivel |                                     Regla                                     |        Origen         |
| :------------------------------------: | :-------------------: | :------: | :---: | :---------------------------------------------------------------------------: | :-------------------: |
|         `trg_readonly_asiento`         |       `UPDATE`        | `BEFORE` | `ROW` |              Solo `revertido_at` puede cambiar después del alta               | [`RF-A-33`][rf-a-33]  |
|     `trg_movimientopunto_snapshot`     |       `INSERT`        | `BEFORE` | `ROW` |              Con participación, copia de ella `user_id` y `anio`              | [Familia][t-snapshot] |
|      `trg_movimientopunto_motivo`      | `INSERT`<br/>`UPDATE` | `BEFORE` | `ROW` |  El motivo es de `ajuste_puntos`, o `anulacion_participacion` en un reverso   |  [Familia][t-motivo]  |
|  `trg_movimientopunto_reverso_exacto`  |       `INSERT`        | `BEFORE` | `ROW` | Un reverso anula un asiento vivo, de la misma persona, por su magnitud exacta |   [`RN-08`][rn-08]    |
| `trg_movimientopunto_marcar_revertido` |       `INSERT`        | `AFTER`  | `ROW` |                  Fija `revertido_at` en el asiento original                   | [`RF-A-33`][rf-a-33]  |

### Índices

|               Nombre               |                           Definición                           |                         Propósito                         |
| :--------------------------------: | :------------------------------------------------------------: | :-------------------------------------------------------: |
|  `idx_movimientopunto_user_vivo`   | `(user_id) WHERE revertido_at IS NULL AND origen <> 'reverso'` |                 Cálculo del saldo vigente                 |
| `idx_movimientopunto_user_detalle` |                  `(user_id, created_at DESC)`                  |              Detalle de [`RF-P-22`][rf-p-22]              |
| `idx_movimientopunto_anio_origen`  |                        `(anio, origen)`                        | Separación de automático y manual en [`RF-A-32`][rf-a-32] |

### El saldo

```postgresql
SELECT coalesce(sum(puntos), 0) AS saldo
FROM rudipuntos_movimientopunto
WHERE user_id = $1
  AND revertido_at IS NULL
  AND origen <> 'reverso';
```

El filtro doble excluye el asiento original que fue revertido **y** el asiento
de reverso que lo anuló. Sumar ambos daría el mismo resultado —se cancelan—,
pero contarlos separadamente permite que la vista de detalle muestre los dos y
explique la corrección, que es lo que [`RF-P-22`][rf-p-22] pide.

### Notas de diseño

`trg_movimientopunto_reverso_exacto` impide el reverso parcial. Corregir cinco
puntos otorgados de más no es revertir cinco: es revertir el asiento completo y
emitir uno manual con el valor correcto, de modo que el rastro diga qué pasó.

`participacion_id` nulable admite el ajuste manual puro —puntos por representar a
la Universidad en un espacio que no se modeló como actividad— que
[`RF-A-32`][rf-a-32] contempla explícitamente.

[auditoria]: ../convenciones.md#auditoria-por-tabla
[t-catalogo]: ../triggers.md#catalogo-activo
[t-motivo]: ../triggers.md#motivo-de-lista-cerrada
[t-snapshot]: ../triggers.md#derivacion-de-snapshot
[d-08]: ../decisiones.md#d-08
[d-12]: ../decisiones.md#d-12
[rf-a-30]: ../../requerimientos/funcionales/administracion.md#rf-a-30
[rf-a-31]: ../../requerimientos/funcionales/administracion.md#rf-a-31
[rf-a-32]: ../../requerimientos/funcionales/administracion.md#rf-a-32
[rf-a-33]: ../../requerimientos/funcionales/administracion.md#rf-a-33
[rf-p-22]: ../../requerimientos/funcionales/participantes.md#rf-p-22
[rn-08]: ../../requerimientos/reglas-negocio.md#rn-08
[rn-09]: ../../requerimientos/reglas-negocio.md#rn-09
