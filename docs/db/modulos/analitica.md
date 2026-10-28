---
icon: lucide/chart-column
---

# Analítica

Una tabla y cuatro vistas materializadas en la app `rudi_analitica`.

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

- **Régimen:** [`append-only`][auditoria]
- **Volumen estimado:** 40-120 filas por año cerrado
- **Origen:**
  > - [`RF-A-45`][rf-a-45]
  > - [`RN-18`][rn-18]

### Columnas

|       Campo       |      Tipo       | Nulo | Predeterminado |                      Descripción                       |
| :---------------: | :-------------: | :--: | :------------: | :----------------------------------------------------: |
|    `indicador`    |  `varchar(60)`  |  no  |                | `participantes_unicos`, `inscripciones`, `constancias` |
|      `anio`       |   `smallint`    |  no  |                |                    Período cerrado                     |
|    `dimension`    |  `varchar(40)`  |  no  |      `''`      | `facultad`, `carrera`, `tipo_actividad`; `''` = total  |
| `dimension_valor` | `varchar(150)`  |  no  |      `''`      |         Etiqueta legible del corte, no el UUID         |
|      `valor`      | `numeric(12,2)` |  no  |                |                      No negativo                       |
|     `unidad`      |  `varchar(20)`  |  no  |  `'personas'`  |   `personas` / `registros` / `puntos` / `porcentaje`   |
|   `created_at`    |  `timestamptz`  |  no  |    `now()`     |                  Instante del cierre                   |
| `cerrado_por_id`  |     `uuid`      |  sí  |                |      Nulo cuando lo ejecuta el proceso programado      |
|     `metodo`      |     `text`      |  no  |      `''`      |      Descripción del criterio con que se calculó       |
|  `filas_origen`   |    `integer`    |  no  |      `0`       |        Cuántas filas base sustentaron la cifra         |

### Constraints

```postgresql
CONSTRAINT chk_indicadorperiodo_anio
CHECK (anio BETWEEN 2000 AND 2100)

CONSTRAINT chk_indicadorperiodo_unidad
CHECK (unidad IN ('personas', 'porcentaje', 'puntos', 'registros'))

CONSTRAINT chk_indicadorperiodo_valor
CHECK (valor >= 0)

CONSTRAINT chk_indicadorperiodo_dimension_coherente
CHECK ((dimension = '') = (dimension_valor = ''))
```

### Unicidad e índices

|              Nombre              |                   Definición                    |            Propósito            |
| :------------------------------: | :---------------------------------------------: | :-----------------------------: |
|   `unq_indicadorperiodo_corte`   | `(indicador, anio, dimension, dimension_valor)` |  Un año se cierra una sola vez  |
|   `idx_indicadorperiodo_anio`    |            `(anio DESC, indicador)`             |     Comparativo interanual      |
| `idx_indicadorperiodo_indicador` |            `(indicador, anio DESC)`             | Serie histórica de un indicador |

### Triggers

|               Nombre                |        Evento         | Momento  | Nivel |                     Regla                     |        Origen        |
| :---------------------------------: | :-------------------: | :------: | :---: | :-------------------------------------------: | :------------------: |
|          `trg_append_only`          | `UPDATE`<br/>`DELETE` | `BEFORE` | `ROW` |     Un cierre no se modifica ni se borra      |   [`RN-18`][rn-18]   |
| `trg_indicadorperiodo_anio_cerrado` |       `INSERT`        | `BEFORE` | `ROW` | Rechaza cerrar un año que aún no ha terminado | [`RF-A-45`][rf-a-45] |

### La diferencia frente al cierre

Corregir una participación de un año cerrado **no** reescribe su fila de cierre.
El sistema muestra las dos cifras y su diferencia:

```postgresql
SELECT
  ip.valor            AS valor_cerrado,
  vm.valor            AS valor_actual,
  vm.valor - ip.valor AS diferencia
FROM rudianalitica_indicadorperiodo AS ip
JOIN mv_participante_unico_anio AS vm USING (anio)
WHERE ip.indicador = 'participantes_unicos'
  AND ip.dimension = '';
```

### Notas de diseño

`dimension` y `dimension_valor` son texto plano y no llaves foráneas. Un cierre
es un documento histórico: si la carrera de Ingeniería en Sistemas cambia de
nombre en 2027, el cierre de 2025 debe seguir diciendo cómo se llamaba en 2025.

`metodo` guarda en prosa cómo se calculó la cifra, y `filas_origen` permite
detectar el cierre ejecutado sobre datos incompletos.

---

## Vistas materializadas

Cuatro vistas que sostienen el tablero y los reportes, creadas con `RunSQL` en
`rudi_analitica/migrations/0002_vistas.py`. Cada una tiene un modelo no
administrado (`managed = False`) para leerla desde Django y un índice único que
permite `REFRESH MATERIALIZED VIEW CONCURRENTLY`. Son la única pieza del modelo
sin equivalente en hz-api ([`D-22`][d-22]).

Todas cuentan una participación solo si está validada, no anulada y en un estado
`efectiva` ([`RN-13`][rn-13]).

|            Vista             |           Modelo           |   Índice único   |                                             Contenido                                             |
| :--------------------------: | :------------------------: | :--------------: | :-----------------------------------------------------------------------------------------------: |
| `mv_participante_unico_anio` | `MvParticipanteUnicoAnio`  |     `(anio)`     |              Personas distintas por año: la cifra que la DIEM no puede producir hoy               |
| `mv_participacion_actividad` | `MvParticipacionActividad` | `(actividad_id)` | Las tres cifras de [`RF-A-42`][rf-a-42] por actividad: inscripciones, participaciones y validadas |
|    `mv_saldo_puntos_user`    |    `MvSaldoPuntosUser`     |   `(user_id)`    |       Saldo vigente por persona, con el desglose automático/manual de [`RF-A-32`][rf-a-32]        |
|    `mv_cobertura_carrera`    |    `MvCoberturaCarrera`    |    `(clave)`     | Estudiantes distintos por carrera y año, más una fila `total` que no es la suma de las anteriores |

`mv_cobertura_carrera` incorpora la advertencia de doble titulación de
[`RF-A-44`][rf-a-44]: la fila `total` cuenta personas distintas y declara en
`doble_titulacion` cuántas aparecen en más de una carrera.

`mv_participante_unico_anio` todavía cuenta por `user_id`. Cuando exista la
fusión de personas ([`RF-A-43`][rf-a-43]), la vista contará sobre la persona
conservada, de modo que un duplicado resuelto deje de contar doble **también en
los años anteriores**.

El detalle que se muestra a una persona nunca se sirve desde una vista: el saldo
de un participante se lee de [`movimiento_punto`][movimiento]; la vista sirve
para ordenar y filtrar.

### Por qué vistas y no tablas

Una tabla de agregados exige mantenerse en cada escritura y admite quedar
desincronizada sin que nadie lo note. Una vista materializada declara su
consulta, se reconstruye entera y su desfase es conocido: la fecha del último
refresco, que [`RF-A-47`][rf-a-47] obliga a mostrar junto a cada indicador. El
refresco es un [proceso programado][procesos].

[auditoria]: ../convenciones.md#auditoria-por-tabla
[movimiento]: puntos.md#movimiento_punto
[procesos]: ../procesos.md
[d-22]: ../decisiones.md#d-22
[rf-a-32]: ../../requerimientos/funcionales/administracion.md#rf-a-32
[rf-a-42]: ../../requerimientos/funcionales/administracion.md#rf-a-42
[rf-a-43]: ../../requerimientos/funcionales/administracion.md#rf-a-43
[rf-a-44]: ../../requerimientos/funcionales/administracion.md#rf-a-44
[rf-a-45]: ../../requerimientos/funcionales/administracion.md#rf-a-45
[rf-a-47]: ../../requerimientos/funcionales/administracion.md#rf-a-47
[rn-13]: ../../requerimientos/reglas-negocio.md#rn-13
[rn-18]: ../../requerimientos/reglas-negocio.md#rn-18
