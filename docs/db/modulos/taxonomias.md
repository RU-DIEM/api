---
icon: lucide/tags
---

# Taxonomías y listas cerradas

Las listas que el modelo no deja administrar: los nueve marcos de clasificación
que la matriz de portafolio aplica a cada propuesta, y las listas demográficas y
académicas de las matrices. No son tablas sino enumeraciones (`TextChoices` en
`rudi_catalogos/enums.py`), por [`D-21`][d-21]: las definen normas externas —el
clasificador de actividades económicas, la escala de madurez tecnológica, los
Objetivos de Desarrollo Sostenible— y cambiar un valor no es una decisión
operativa sino una revisión del marco.

## Requerimientos cubiertos

- [`RF-A-39`][rf-a-39]

---

## Forma

Una columna que usa una lista cerrada es `varchar` con un `CHECK` contra los
valores de su enumeración, generado desde Python
(`Q(<columna>__in=<Enum>.values)`). La API valida el mismo `TextChoices`, de
modo que el valor rechazado por el motor nunca llega a él desde la interfaz.

```postgresql
CONSTRAINT chk_propuesta_trl
CHECK (trl IN ('trl_1', 'trl_2', …, 'no_aplica', 'por_determinar'))
```

Cambiar la lista es cambiar la enumeración y generar una migración que
reescribe el `CHECK`. Es deliberadamente más caro que insertar una fila: el
marco de referencia no cambia por decisión de la DIEM.

---

## Valores neutros

Ocho de los nueve marcos incluyen valores como _por determinar_, _no aplica_ y
_sin alineación demostrada_. El glosario de la matriz insiste en la diferencia:
_no aplica_ significa que no hay componente evaluable; _por determinar_ significa
que lo hay pero todavía no se evaluó.

Las taxonomías heredan de `RudiTaxonomia`, que declara `neutrals()` y
`classified()`. Sin esa distinción, todo reporte de distribución tendría que
enumerar en cada consulta qué códigos no son valores reales, y bastaría olvidarlo
una vez para publicar que _el nivel de madurez tecnológica más frecuente del
portafolio es por determinar_. Con ella, el denominador de cualquier distribución
se calcula sobre `classified()` y el resto se informa aparte como cobertura de
la clasificación.

|      Enumeración       |                     Neutros                     |
| :--------------------: | :---------------------------------------------: |
|   `EtapasDesarrollo`   |                `por_determinar`                 |
|  `SectoresAplicacion`  |                `por_determinar`                 |
|   `TiposInnovacion`    |                `por_determinar`                 |
| `VerticalesInnovacion` |                `por_determinar`                 |
|         `TRL`          |          `no_aplica`, `por_determinar`          |
|         `MRL`          |          `no_aplica`, `por_determinar`          |
|         `ODS`          | `no_aplica`, `por_determinar`, `sin_alineacion` |

---

## Inventario

### Taxonomías del portafolio

|      Enumeración       | Valores |                                        Marco de referencia                                         |
| :--------------------: | :-----: | :------------------------------------------------------------------------------------------------: |
| `NivelesFormalizacion` |    3    |                 Idea, iniciativa y proyecto de innovación; grado de estructuración                 |
|   `EtapasDesarrollo`   |    6    |        Estructuración, preincubación, incubación, aceleración, escalamiento, por determinar        |
|  `AmbitosAplicacion`   |    5    |           Quíntuple hélice: academia, empresa, gobierno, sociedad civil, medio ambiente            |
|  `SectoresAplicacion`  |   23    | Secciones A-U del clasificador nacional de actividades económicas, multisectorial y por determinar |
| `VerticalesInnovacion` |   23    |               Verticales tecnológicas: EdTech, HealthTech, AgTech, FinTech, GovTech…               |
|   `TiposInnovacion`    |   11    |                       Diez tipos de innovación de Doblin, más por determinar                       |
|         `TRL`          |   11    |                 Escala de madurez tecnológica: TRL 1-9, no aplica, por determinar                  |
|         `MRL`          |   11    |                Escala de preparación de mercado: MRL 1-9, no aplica, por determinar                |
|         `ODS`          |   20    |              Los 17 Objetivos de Desarrollo Sostenible, más los tres valores neutros               |

### Listas de las matrices

|     Enumeración     | Valores |                          Usada en                           |
| :-----------------: | :-----: | :---------------------------------------------------------: |
|      `Generos`      |    3    |             `rudi_user.genero`, [`D-19`][d-19]              |
|      `Etnias`       |   15    |     `rudi_user.etnia`: catorce pueblos y `sin_declara`      |
|   `TallasCamisa`    |    7    |                 `rudi_user.talla`: XS a 3XL                 |
| `NivelesAcademicos` |    6    | `docente_profile` y `mentor_profile`: bachiller a doctorado |
|  `NivelesCarrera`   |    8    | `estudiante_carrera.nivel`: 1.º a 6.º, egresado, no aplica  |

`Etnias` conserva las denominaciones exactas de la matriz de estudiantes.
Cambiarlas por una lista propia rompería la comparación con los reportes
históricos y con los formatos que la Universidad reporta a instancias externas.

---

## Notas de diseño

### Un solo `ODS` para dos columnas

`propuesta` usa la enumeración dos veces, como principal y como secundario, con
nombres de columna que declaran el papel: `ods_principal` y `ods_secundario`. Un
`CHECK` impide que sean iguales, tal como exige el glosario de la matriz, y otro
que `no_aplica` aparezca en la principal: solo tiene sentido como _no hay
segunda contribución_.

### `TRL` y `MRL` como enumeraciones separadas

Comparten forma y escala, y sería tentador unificarlas. No se hace porque son
marcos independientes con criterios de asignación distintos, y el glosario de la
matriz lo subraya: una solución puede estar tecnológicamente avanzada y mantener
una preparación de mercado baja.

### El orden es la escala

En `TRL`, `MRL` y `EtapasDesarrollo` el orden de declaración de la enumeración
es una **escala ordinal** y los reportes de avance lo usan como tal. Los valores
neutros van al final y quedan fuera de `classified()`, de modo que ninguna
consulta de progreso los interprete como el nivel más avanzado.

### Lo que estas listas no guardan

La matriz de portafolio documenta con detalle cómo asignar cada clasificación:
que se registre el nivel demostrado y no el planificado, que no se asigne un
Objetivo de Desarrollo Sostenible por afinidad temática, que la vertical se elija
por el problema resuelto y no por la herramienta empleada.

Ese criterio es ayuda contextual del formulario. No hay validación que lo
imponga, y no la hay porque no puede haberla: ninguna restricción de base de
datos distingue un nivel demostrado de uno aspiracional.

[d-19]: ../decisiones.md#d-19
[d-21]: ../decisiones.md#d-21
[rf-a-39]: ../../requerimientos/funcionales/administracion.md#rf-a-39
