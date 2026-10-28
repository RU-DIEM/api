---
icon: lucide/chart-column
---

# Analítica

Una tabla y cuatro vistas materializadas.

El módulo es pequeño a propósito. Un reporte es una consulta, no una fila
guardada; lo único que se almacena es el **cierre anual**, porque un informe
entregado en enero tiene que seguir diciendo lo mismo en diciembre aunque las
participaciones de ese año se hayan corregido.

## Requerimientos cubiertos

- [`RF-A-42`][rf-a-42]
- [`RF-A-43`][rf-a-43]
- [`RF-A-44`][rf-a-44]
- [`RF-A-45`][rf-a-45]
- [`RF-A-47`][rf-a-47]

---

## `indicador_periodo`

Cierre congelado de un indicador para un período. Nunca se recalcula.

- **Régimen:** [`append-only`][auditoria], **no se borra**
- **Volumen estimado:** 40-120 filas por año cerrado
- **Origen:**
  > - [`RF-A-45`][rf-a-45]
  > - [`RN-18`][rn-18]

### Columnas

|       Campo       |      Tipo      | Nulo | Predeterminado |                      Descripción                       |
| :---------------: | :------------: | :--: | :------------: | :----------------------------------------------------: |
|    `indicador`    | `varchar(60)`  |  no  |                | `participantes_unicos`, `inscripciones`, `constancias` |
|      `anio`       |   `smallint`   |  no  |                |                    Período cerrado                     |
|    `dimension`    | `varchar(40)`  |  no  |      `''`      | `facultad`, `carrera`, `tipo_actividad`; `''` = total  |
| `dimension_valor` | `varchar(150)` |  no  |      `''`      |         Etiqueta legible del corte, no el UUID         |
|      `valor`      |   `numeric`    |  no  |                |                                                        |
|     `unidad`      | `varchar(20)`  |  no  |  `'personas'`  |   `personas` / `registros` / `puntos` / `porcentaje`   |
|   `cerrado_at`    | `timestamptz`  |  no  |    `now()`     |                                                        |
|   `cerrado_por`   |     `uuid`     |  sí  |                |      Nulo cuando lo ejecuta el proceso programado      |
|     `metodo`      |     `text`     |  no  |      `''`      |      Descripción del criterio con que se calculó       |
|  `filas_origen`   |   `integer`    |  no  |      `0`       |        Cuántas filas base sustentaron la cifra         |

### Constraints

```postgresql
CONSTRAINT chk_indicadorperiodo_anio
CHECK (anio BETWEEN 2000 AND 2100)

CONSTRAINT chk_indicadorperiodo_unidad
CHECK (unidad IN ('personas', 'registros', 'puntos', 'porcentaje'))

CONSTRAINT chk_indicadorperiodo_valor_no_negativo
CHECK (valor >= 0)

CONSTRAINT chk_indicadorperiodo_dimension_coherente
CHECK ((length(dimension) = 0) = (length(dimension_valor) = 0))
```

### Unicidad

|            Nombre            |                   Definición                    |           Propósito           |
| :--------------------------: | :---------------------------------------------: | :---------------------------: |
| `unq_indicadorperiodo_corte` | `(indicador, anio, dimension, dimension_valor)` | Un año se cierra una sola vez |

### Triggers

|               Nombre                |  Evento  | Momento  | Nivel |                     Regla                     |        Origen        |
| :---------------------------------: | :------: | :------: | :---: | :-------------------------------------------: | :------------------: |
|  `trg_indicadorperiodo_inmutable`   | `UPDATE` | `BEFORE` | `ROW` |        Rechaza cualquier modificación         |   [`RN-18`][rn-18]   |
|  `trg_indicadorperiodo_no_borrar`   | `DELETE` | `BEFORE` | `ROW` |              Bloquea el borrado               | [`RF-A-50`][rf-a-50] |
| `trg_indicadorperiodo_anio_cerrado` | `INSERT` | `BEFORE` | `ROW` | Rechaza cerrar un año que aún no ha terminado | [`RF-A-45`][rf-a-45] |

### Índices

|              Nombre              |        Definición        |            Propósito            |
| :------------------------------: | :----------------------: | :-----------------------------: |
|   `idx_indicadorperiodo_anio`    | `(anio DESC, indicador)` |     Comparativo interanual      |
| `idx_indicadorperiodo_indicador` | `(indicador, anio DESC)` | Serie histórica de un indicador |

### La diferencia frente al cierre

Corregir una participación de un año cerrado **no** reescribe su fila de cierre.
El sistema muestra las dos cifras y su diferencia:

```postgresql
SELECT
  ip.valor                    AS valor_cerrado,
  vm.valor                    AS valor_actual,
  vm.valor - ip.valor         AS diferencia
FROM indicador_periodo ip
JOIN mv_participante_unico_anio vm USING (anio)
WHERE ip.indicador = 'participantes_unicos'
  AND ip.dimension = '';
```

Esto es lo que [`RF-A-45`][rf-a-45] pide: que el informe entregado siga siendo
reproducible y que las correcciones posteriores se vean como corrección, no como
si el número siempre hubiera sido otro.

### Notas de diseño

`dimension` y `dimension_valor` son texto plano y no llaves foráneas. Un cierre
es un documento histórico: si la carrera de Ingeniería en Sistemas cambia de
nombre en 2027, el cierre de 2025 debe seguir diciendo cómo se llamaba en 2025.
Una llave foránea al catálogo haría lo contrario.

`metodo` guarda en prosa cómo se calculó la cifra. Es el campo que responde, tres
años después, si _participantes únicos_ incluía a los mentores o solo a
estudiantes. Sin él, dos cierres de años distintos pueden no ser comparables y
nadie sabría por qué.

`filas_origen` permite detectar el cierre ejecutado sobre datos incompletos: un
año con doce mil filas base y otro con cuarenta, ambos con cifras plausibles, se
distinguen aquí y en ningún otro sitio.

---

## Vistas materializadas

Cuatro vistas que sostienen el tablero y los reportes en caliente. No son tablas
y no cuentan en el recuento de 82: se refrescan por
[proceso programado][procesos] y pueden reconstruirse desde cero en cualquier
momento.

### `mv_participante_unico_anio`

Personas distintas por año, resueltas tras las fusiones. Es la cifra que la DIEM
no puede producir hoy.

```postgresql
SELECT
  p.anio,
  count(DISTINCT coalesce(u.fusionado_en_id, u.id)) AS valor
FROM participacion p
JOIN usuario u ON u.id = p.usuario_id
WHERE p.validada_at IS NOT NULL
  AND p.anulada_at IS NULL
GROUP BY p.anio;
```

El `coalesce` sobre `fusionado_en_id` es lo que hace cumplir
[`RF-A-43`][rf-a-43]: un duplicado resuelto deja de contar doble **también en los
años anteriores**, porque la cifra se recalcula sobre el registro conservado y no
sobre el que existía cuando ocurrió la participación.

### `mv_participacion_actividad`

Las tres cifras de [`RF-A-42`][rf-a-42] por actividad: inscripciones,
participaciones registradas y participaciones validadas. Tenerlas en una sola
fila es lo que impide publicar una sin las otras dos.

### `mv_saldo_puntos_usuario`

Saldo vigente por persona, con el desglose entre automático y manual que
[`RF-A-32`][rf-a-32] exige separar. El detalle sigue leyéndose de
[`movimiento_punto`][movimiento]: la vista sirve para ordenar y filtrar, nunca
como fuente del dato que se muestra a la persona.

### `mv_cobertura_carrera`

Estudiantes distintos por carrera y por año, con la advertencia de doble
titulación de [`RF-A-44`][rf-a-44] incorporada: una fila por carrera y una fila
de total general que **no** es la suma de las anteriores, más el conteo explícito
de cuántas personas aparecen en más de una.

### Régimen de refresco

|            Vista             |      Frecuencia      |                 Nota                 |
| :--------------------------: | :------------------: | :----------------------------------: |
| `mv_participante_unico_anio` | Diaria y al fusionar |  La fusión la invalida de inmediato  |
| `mv_participacion_actividad` |       Horaria        |    Es la que alimenta el tablero     |
|  `mv_saldo_puntos_usuario`   |        Diaria        | El detalle nunca se sirve desde aquí |
|    `mv_cobertura_carrera`    |        Diaria        |                                      |

Todas se refrescan con `REFRESH MATERIALIZED VIEW CONCURRENTLY`, lo que exige un
índice único sobre cada una y permite que el tablero siga respondiendo durante el
refresco.

### Por qué vistas y no tablas

Una tabla de agregados exige mantenerse en cada escritura y admite quedar
desincronizada sin que nadie lo note. Una vista materializada declara su
consulta, se reconstruye entera y su desfase es conocido: la fecha del último
refresco, que [`RF-A-47`][rf-a-47] obliga a mostrar junto a cada indicador.

El cierre anual es el único caso en que un agregado sí se almacena, y no por
rendimiento sino porque su valor está en no recalcularse nunca.

[auditoria]: ../convenciones.md#auditoria-por-tabla
[movimiento]: puntos.md#movimiento_punto
[procesos]: ../procesos.md
[rf-a-32]: ../../requerimientos/funcionales/administracion.md#rf-a-32
[rf-a-42]: ../../requerimientos/funcionales/administracion.md#rf-a-42
[rf-a-43]: ../../requerimientos/funcionales/administracion.md#rf-a-43
[rf-a-44]: ../../requerimientos/funcionales/administracion.md#rf-a-44
[rf-a-45]: ../../requerimientos/funcionales/administracion.md#rf-a-45
[rf-a-47]: ../../requerimientos/funcionales/administracion.md#rf-a-47
[rf-a-50]: ../../requerimientos/funcionales/administracion.md#rf-a-50
[rn-18]: ../../requerimientos/reglas-negocio.md#rn-18
