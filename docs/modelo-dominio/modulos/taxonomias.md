---
icon: lucide/tags
---

# Taxonomías de innovación

Los nueve marcos de clasificación que la matriz de portafolio aplica a cada
propuesta. Se separan de [`Catálogos`][catalogos] porque no los administra la
DIEM: los definen normas externas —el clasificador de actividades económicas, la
escala de madurez tecnológica, los Objetivos de Desarrollo Sostenible— y editar
una etiqueta aquí no es una decisión operativa sino una desviación del marco.

## Requerimientos cubiertos

- [`RF-A-39`][rf-a-39]

---

## Forma común

Las nueve tablas comparten forma, además de las
[columnas estándar][convenciones-columnas].

- **Régimen:** [Mutable protegida][auditoria]
- **Origen:**
  > - [`RF-A-39`][rf-a-39]

### Columnas

|     Campo     |      Tipo      | Nulo | Predeterminado |                       Descripción                       |
| :-----------: | :------------: | :--: | :------------: | :-----------------------------------------------------: |
|   `codigo`    | `varchar(50)`  |  no  |                |                  Identificador estable                  |
|  `etiqueta`   | `varchar(150)` |  no  |                |             Denominación oficial del marco              |
| `descripcion` |     `text`     |  no  |      `''`      | Criterio de asignación tomado del glosario de la matriz |
|    `orden`    |   `smallint`   |  no  |      `0`       |         Posición en la escala o en el selector          |
|  `es_neutro`  |   `boolean`    |  no  |    `false`     |   Marca los valores de _por determinar_ y _no aplica_   |
|   `activo`    |   `boolean`    |  no  |     `true`     |                                                         |

### Unicidad

|        Nombre        | Definición |
| :------------------: | :--------: |
| `unq_<tabla>_codigo` | `(codigo)` |

### Triggers

|            Nombre             |       Evento       | Momento  | Nivel |               Regla                |     Origen     |
| :---------------------------: | :----------------: | :------: | :---: | :--------------------------------: | :------------: |
| `trg_<tabla>_codigo_readonly` | `UPDATE OF codigo` | `BEFORE` | `ROW` | Rechaza cualquier cambio de código | [`D-08`][d-08] |
|    `trg_<tabla>_no_borrar`    |      `DELETE`      | `BEFORE` | `ROW` |         Bloquea el borrado         | [`D-18`][d-18] |

---

## `es_neutro`, la columna que evita el peor indicador

Ocho de los nueve marcos incluyen valores como _por determinar_, _no aplica_ y
_sin alineación demostrada_. El glosario de la matriz insiste en la diferencia:
_no aplica_ significa que no hay componente evaluable; _por determinar_ significa
que lo hay pero todavía no se evaluó.

Sin `es_neutro`, todo reporte de distribución tendría que enumerar en cada
consulta qué códigos no son valores reales, y bastaría olvidarlo una vez para
publicar que _el nivel de madurez tecnológica más frecuente del portafolio es por
determinar_. Con la columna, el denominador de cualquier distribución se calcula
sobre lo efectivamente clasificado y el resto se informa aparte como cobertura de
la clasificación.

|    Marco    |   Valor neutro   |                       Significado                        |
| :---------: | :--------------: | :------------------------------------------------------: |
| `nivel_trl` |   `no_aplica`    |         No hay componente tecnológico evaluable          |
| `nivel_trl` | `por_determinar` |              Lo hay, pero no se ha evaluado              |
|    `ods`    | `sin_alineacion` |      El análisis no evidenció contribución directa       |
|    `ods`    |   `no_aplica`    | Solo para el ODS secundario: no hay segunda contribución |

---

## Inventario

|         Tabla         | Filas |                                          Marco de referencia                                           |
| :-------------------: | :---: | :----------------------------------------------------------------------------------------------------: |
| `nivel_formalizacion` |   3   |                   Idea, iniciativa y proyecto de innovación; grado de estructuración                   |
|  `etapa_desarrollo`   |   5   |                  Estructuración, preincubación, incubación, aceleración, escalamiento                  |
|    `ambito_helice`    |   5   |             Quíntuple hélice: academia, empresa, gobierno, sociedad civil, medio ambiente              |
|    `sector_cuaen`     |  24   | Secciones A-U del clasificador nacional de actividades económicas, más multisectorial y por determinar |
| `vertical_innovacion` |  23   |                 Verticales tecnológicas: EdTech, HealthTech, AgTech, FinTech, GovTech…                 |
|   `tipo_innovacion`   |  11   |                         Diez tipos de innovación de Doblin, más por determinar                         |
|      `nivel_trl`      |  11   |                   Escala de madurez tecnológica: TRL 1-9, no aplica, por determinar                    |
|      `nivel_mrl`      |  11   |                  Escala de preparación de mercado: MRL 1-9, no aplica, por determinar                  |
|         `ods`         |  20   |                Los 17 Objetivos de Desarrollo Sostenible, más los tres valores neutros                 |

---

## Notas de diseño

### Un solo `ods` para dos columnas

`propuesta` referencia esta tabla dos veces, como principal y como secundario, con
nombres de columna que declaran el papel: `ods_principal_id` y
`ods_secundario_id`. Un `CHECK` impide que sean iguales, tal como exige el
glosario de la matriz.

`no_aplica` solo tiene sentido en la columna secundaria. La distinción la impone
un trigger y no un `CHECK`, porque el atributo que la determina vive en la tabla
referenciada.

### `nivel_trl` y `nivel_mrl` como tablas separadas

Comparten forma y escala, y sería tentador unificarlas con un discriminador. No
se hace porque son marcos independientes con criterios de asignación distintos, y
el glosario de la matriz lo subraya: una solución puede estar tecnológicamente
avanzada y mantener una preparación de mercado baja. Unificarlas invitaría a
compararlas como si fueran la misma escala.

### `orden` como escala, no como preferencia

En siete de los nueve marcos `orden` es un simple criterio de presentación. En
`nivel_trl`, `nivel_mrl` y `etapa_desarrollo` es una **escala ordinal** y los
reportes de avance lo usan como tal.

Los valores neutros llevan `orden` alto y `es_neutro` verdadero, de modo que
queden al final del selector sin que ninguna consulta de progreso los interprete
como el nivel más avanzado.

### Lo que estas tablas no guardan

La matriz de portafolio documenta con detalle cómo asignar cada clasificación:
que se registre el nivel demostrado y no el planificado, que no se asigne un
Objetivo de Desarrollo Sostenible por afinidad temática, que la vertical se elija
por el problema resuelto y no por la herramienta empleada.

Ese criterio vive en `descripcion` como ayuda contextual del formulario. No hay
validación que lo imponga, y no la hay porque no puede haberla: ninguna
restricción de base de datos distingue un nivel demostrado de uno aspiracional.
Es una advertencia para quien lea los indicadores del portafolio, no un defecto
del modelo. Ver [`R-07`][r-07].

[auditoria]: ../convenciones.md#auditoria-por-tabla
[catalogos]: catalogos.md
[convenciones-columnas]: ../convenciones.md#columnas-estandar
[d-08]: ../decisiones.md#d-08
[d-18]: ../decisiones.md#d-18
[r-07]: ../riesgos.md#r-07
[rf-a-39]: ../../requerimientos/funcionales/administracion.md#rf-a-39
