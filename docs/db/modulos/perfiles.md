---
icon: lucide/id-card
---

# Perfiles y vinculación

Los cuatro perfiles que una persona puede acumular, la estructura académica que
los sostiene y los datos que cada uno agrega.

Ninguna de estas tablas es obligatoria y todas son acumulables. Una persona sin
ningún perfil no puede activarse; una con los cuatro es perfectamente legal y
existe en el listado de mentores real.

## Requerimientos cubiertos

- [`RF-P-08`][rf-p-08]
- [`RF-P-09`][rf-p-09]
- [`RF-P-10`][rf-p-10]
- [`RF-P-11`][rf-p-11]
- [`RF-P-12`][rf-p-12]
- [`RF-P-13`][rf-p-13]
- [`RF-A-10`][rf-a-10]
- [`RF-A-11`][rf-a-11]
- [`RF-A-12`][rf-a-12]
- [`RF-A-13`][rf-a-13]

---

## Estructura académica

Tres catálogos con estructura propia, separados de [`Catálogos`][catalogos]
porque tienen jerarquía y llaves foráneas entre sí.

### `facultad`

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 5-8 filas

|     Campo      |      Tipo      | Nulo | Predeterminado |      Descripción       |
| :------------: | :------------: | :--: | :------------: | :--------------------: |
|    `codigo`    | `varchar(50)`  |  no  |                | Identificador estable  |
|    `nombre`    | `varchar(150)` |  no  |                |  Denominación oficial  |
| `nombre_corto` | `varchar(40)`  |  no  |      `''`      | Para tablas y gráficos |
|    `activa`    |   `boolean`    |  no  |     `true`     |                        |

### `carrera`

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 25-50 filas

|      Campo       |      Tipo      | Nulo | Predeterminado |                Descripción                |
| :--------------: | :------------: | :--: | :------------: | :---------------------------------------: |
|     `codigo`     | `varchar(50)`  |  no  |                |           Identificador estable           |
|     `nombre`     | `varchar(150)` |  no  |                |           Denominación oficial            |
|  `facultad_id`   |     `uuid`     |  no  |                |               Llave foránea               |
| `duracion_anios` |   `smallint`   |  sí  |                | Sostiene la validación del año de carrera |
|     `activa`     |   `boolean`    |  no  |     `true`     |                                           |

#### Llaves foráneas

|    Columna    | Referencia | `ON DELETE` |                  Notas                  |
| :-----------: | :--------: | :---------: | :-------------------------------------: |
| `facultad_id` | `facultad` | `RESTRICT`  | Una facultad con carreras no se elimina |

#### Unicidad

|            Nombre             |           Definición           |
| :---------------------------: | :----------------------------: |
|     `unq_carrera_codigo`      |           `(codigo)`           |
| `unq_carrera_nombre_facultad` | `(facultad_id, lower(nombre))` |

### `institucion`

Universidades, centros educativos, empresas y organizaciones de procedencia de
los participantes externos.

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 50-200 filas

|       Campo       |      Tipo      | Nulo | Predeterminado |                    Descripción                    |
| :---------------: | :------------: | :--: | :------------: | :-----------------------------------------------: |
|     `nombre`      | `varchar(200)` |  no  |                |               Denominación oficial                |
|      `tipo`       | `varchar(30)`  |  no  |                |                    Ver `CHECK`                    |
|      `pais`       |  `varchar(2)`  |  no  |     `'NI'`     |             Código ISO de dos letras              |
| `normalizada_at`  | `timestamptz`  |  sí  |                | Nulo = capturada durante un registro, sin revisar |
| `fusionada_en_id` |     `uuid`     |  sí  |                |           Apunta a la variante canónica           |
|     `activa`      |   `boolean`    |  no  |     `true`     |                                                   |

#### Constraints

```postgresql
CONSTRAINT chk_institucion_tipo
CHECK (
  tipo IN (
    'universidad',
    'centro_tecnico',
    'colegio',
    'empresa',
    'organizacion',
    'gobierno',
    'otra'
  )
)

CONSTRAINT chk_institucion_fusion_no_reflexiva
CHECK (fusionada_en_id IS DISTINCT FROM id)
```

#### Notas de diseño

`institucion` es el único catálogo que admite altas desde un formulario de
registro, y por eso es el único que lleva mecanismo de normalización. Un
participante externo que escribe _UNI_, otro que escribe _Universidad Nacional de
Ingeniería_ y otro que escribe _uni_ producen tres filas, y `fusionada_en_id`
permite unificarlas después sin perder lo que cada persona declaró.

El alternativa —exigir que el administrador dé de alta cada institución antes de
que alguien pueda registrarse— bloquea el registro en el momento exacto en que la
persona está dispuesta a completarlo, que en un hackathon con inscripción abierta
es un costo que no se recupera.

---

## `perfil_estudiante`

- **Régimen:** [Mutable rastreada][auditoria]
- **Volumen estimado:** 1,500-6,000 filas
- **Origen:**
  > - [`RF-P-08`][rf-p-08]
  > - [`RF-P-10`][rf-p-10]

### Columnas

|       Campo       |      Tipo      | Nulo | Predeterminado |                      Descripción                       |
| :---------------: | :------------: | :--: | :------------: | :----------------------------------------------------: |
|   `usuario_id`    |     `uuid`     |  no  |                |                  Llave foránea, único                  |
|     `origen`      | `varchar(20)`  |  no  |                |                   `uam` / `externo`                    |
| `institucion_id`  |     `uuid`     |  sí  |                |       Obligatoria en el externo; nula en el UAM        |
| `carrera_externa` | `varchar(150)` |  no  |      `''`      | Texto libre; solo para estudiantes de otra institución |
|    `ocupacion`    |     `text`     |  no  |      `''`      |     A qué se dedica, para el externo no estudiante     |
| `actualizado_at`  | `timestamptz`  |  no  |    `now()`     |      Última confirmación de vigencia de los datos      |

### Constraints

```postgresql
CONSTRAINT chk_perfilestudiante_origen
CHECK (origen IN ('uam', 'externo'))

CONSTRAINT chk_perfilestudiante_institucion_externa
CHECK (
  (origen = 'externo') = (institucion_id IS NOT NULL)
)

CONSTRAINT chk_perfilestudiante_carrera_externa
CHECK (
  origen = 'externo'
  OR
  length(carrera_externa) = 0
)
```

### Unicidad

|             Nombre             |   Definición   |
| :----------------------------: | :------------: |
| `unq_perfilestudiante_usuario` | `(usuario_id)` |

### Triggers

|               Nombre               |  Evento  | Momento | Nivel |                                Regla                                 |        Origen        |
| :--------------------------------: | :------: | :-----: | :---: | :------------------------------------------------------------------: | :------------------: |
| `trg_perfilestudiante_carrera_uam` | `INSERT` | `AFTER` | `ROW` | Si `origen = 'uam'`, exige al menos una fila en `estudiante_carrera` | [`RF-P-08`][rf-p-08] |

### Notas de diseño

Un solo perfil para el estudiante UAM y el estudiante externo, discriminados por
`origen`. La matriz de estudiantes ya los trata así: una hoja, una columna de tipo
de estudiante y campos que aplican a uno u otro.

Separarlos en dos tablas duplicaría la relación con `estudiante_carrera` y
obligaría a toda consulta de participación estudiantil a unir dos tablas. El
discriminador cumple su definición: no cambia durante la vida de la fila —un
estudiante externo que se matricula en la UAM es un caso de alta de perfil, no de
edición— y agregar un valor exigiría columnas nuevas.

---

## `estudiante_carrera`

Las carreras que cursa un estudiante UAM. Es la tabla que resuelve la doble
titulación por [`D-17`][d-17].

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 1,600-6,500 filas
- **Origen:**
  > - [`RF-P-09`][rf-p-09]
  > - [`RN-04`][rn-04]

### Columnas

|       Campo       |     Tipo      | Nulo | Predeterminado |              Descripción               |
| :---------------: | :-----------: | :--: | :------------: | :------------------------------------: |
|    `perfil_id`    |    `uuid`     |  no  |                |  Llave foránea a `perfil_estudiante`   |
|   `carrera_id`    |    `uuid`     |  no  |                |             Llave foránea              |
| `anio_carrera_id` |    `uuid`     |  sí  |                |     Llave foránea a `anio_carrera`     |
|  `es_principal`   |   `boolean`   |  no  |    `false`     |                                        |
|   `iniciada_en`   |  `smallint`   |  sí  |                |      Año de inicio, si se conoce       |
|   `cerrada_at`    | `timestamptz` |  sí  |                | Marca de cierre: abandono o titulación |

### Llaves foráneas

|      Columna      |     Referencia      | `ON DELETE` |                   Notas                    |
| :---------------: | :-----------------: | :---------: | :----------------------------------------: |
|    `perfil_id`    | `perfil_estudiante` |  `CASCADE`  | Fragmento del perfil, sin identidad propia |
|   `carrera_id`    |      `carrera`      | `RESTRICT`  |      Una carrera citada no se elimina      |
| `anio_carrera_id` |   `anio_carrera`    | `RESTRICT`  |                                            |

### Unicidad

|              Nombre               |                       Definición                        |                Propósito                 |
| :-------------------------------: | :-----------------------------------------------------: | :--------------------------------------: |
|    `unq_estudiantecarrera_par`    |                `(perfil_id, carrera_id)`                | No se declara dos veces la misma carrera |
| `unq_estudiantecarrera_principal` | `(perfil_id) WHERE es_principal AND cerrada_at IS NULL` |     Exactamente una es la principal      |

### Triggers

|                  Nombre                  |                Evento                 | Momento  |    Nivel    |                               Regla                               |        Origen        |
| :--------------------------------------: | :-----------------------------------: | :------: | :---------: | :---------------------------------------------------------------: | :------------------: |
| `trg_estudiantecarrera_principal_minimo` |          `UPDATE`, `DELETE`           | `AFTER`  | `STATEMENT` |     Aborta si algún perfil activo queda sin carrera principal     | [`RF-P-09`][rf-p-09] |
|  `trg_estudiantecarrera_anio_coherente`  | `INSERT`, `UPDATE OF anio_carrera_id` | `BEFORE` |    `ROW`    | Rechaza un año mayor que `carrera.duracion_anios`, salvo egresado | [`RF-P-08`][rf-p-08] |

### Índices

|             Nombre              |               Definición                |                  Propósito                   |
| :-----------------------------: | :-------------------------------------: | :------------------------------------------: |
| `idx_estudiantecarrera_carrera` | `(carrera_id) WHERE cerrada_at IS NULL` | Reportes por carrera de [`RF-A-44`][rf-a-44] |

### Notas de diseño

El índice único parcial sobre `es_principal` es lo que impide el estado más
molesto de esta tabla: un estudiante con dos carreras y ninguna marcada como
principal, que desaparecería de todo reporte que agrupe por carrera principal.

`cerrada_at` distingue la carrera que el estudiante abandonó de la que sigue
cursando. Los reportes de participación por carrera usan la vigente al momento de
la participación, no la actual, y por eso la marca es temporal y no un booleano.

Nada de esto aplica al estudiante externo, que declara su carrera como texto libre
en el perfil. El catálogo de carreras es institucional y modelar las carreras de
las otras veinte universidades del país está fuera de alcance por completo.

---

## `perfil_docente`

- **Régimen:** [Mutable rastreada][auditoria]
- **Volumen estimado:** 50-300 filas
- **Origen:**
  > - [`RF-P-11`][rf-p-11]

### Columnas

|        Campo         |      Tipo      | Nulo | Predeterminado |            Descripción            |
| :------------------: | :------------: | :--: | :------------: | :-------------------------------: |
|     `usuario_id`     |     `uuid`     |  no  |                |       Llave foránea, único        |
|    `facultad_id`     |     `uuid`     |  sí  |                |       Adscripción principal       |
| `nivel_academico_id` |     `uuid`     |  sí  |                | Llave foránea a `nivel_academico` |
|       `cargo`        | `varchar(120)` |  no  |      `''`      |                                   |
|   `actualizado_at`   | `timestamptz`  |  no  |    `now()`     |  Última confirmación de vigencia  |

### Unicidad

|           Nombre            |   Definición   |
| :-------------------------: | :------------: |
| `unq_perfildocente_usuario` | `(usuario_id)` |

El modelo admite una sola facultad de adscripción. Los casos de docentes
adscritos a dos facultades existen pero son pocos y la DIEM no reporta por ellos;
si la necesidad aparece, la extensión es una tabla puente y no un cambio
estructural.

---

## `perfil_mentor`

Expediente profesional de quien acompaña equipos. Es la tabla que recoge el
listado de mentores.

- **Régimen:** [Mutable rastreada][auditoria]
- **Volumen estimado:** 40-200 filas
- **Origen:**
  > - [`RF-P-12`][rf-p-12]
  > - [`RF-A-11`][rf-a-11]

### Columnas

|           Campo           |     Tipo      | Nulo | Predeterminado |                    Descripción                     |
| :-----------------------: | :-----------: | :--: | :------------: | :------------------------------------------------: |
|       `usuario_id`        |    `uuid`     |  no  |                |                Llave foránea, único                |
|     `tipo_mentor_id`      |    `uuid`     |  sí  |                |           Llave foránea a `tipo_mentor`            |
|   `nivel_academico_id`    |    `uuid`     |  sí  |                |         Llave foránea a `nivel_academico`          |
|      `municipio_id`       |    `uuid`     |  sí  |                |            Llave foránea a `municipio`             |
|        `direccion`        |    `text`     |  no  |      `''`      |          Dirección declarada, texto libre          |
| `descripcion_profesional` |    `text`     |  no  |      `''`      | Trayectoria en prosa, tal como la matriz la guarda |
|  `necesidades_formacion`  |    `text`     |  no  |      `''`      |      Formación que el mentor declara requerir      |
|      `confirmado_at`      | `timestamptz` |  sí  |                |   Nulo = solicitado y no confirmado por la DIEM    |
|     `confirmado_por`      |    `uuid`     |  sí  |                |        Llave foránea `RESTRICT` a `usuario`        |
|     `actualizado_at`      | `timestamptz` |  no  |    `now()`     |          Última confirmación de vigencia           |

### Constraints

```postgresql
CONSTRAINT chk_perfilmentor_confirmacion_coherente
CHECK ((confirmado_at IS NULL) = (confirmado_por IS NULL))

CONSTRAINT chk_perfilmentor_descripcion_longitud
CHECK (length(descripcion_profesional) <= 4000)
```

### Unicidad

|           Nombre           |   Definición   |
| :------------------------: | :------------: |
| `unq_perfilmentor_usuario` | `(usuario_id)` |

### Índices

|             Nombre             |                    Definición                     |              Propósito              |
| :----------------------------: | :-----------------------------------------------: | :---------------------------------: |
| `idx_perfilmentor_confirmado`  | `(confirmado_at) WHERE confirmado_at IS NOT NULL` |   Listado de mentores disponibles   |
| `gin_perfilmentor_descripcion` |     `(descripcion_profesional gin_trgm_ops)`      | Búsqueda en la trayectoria en prosa |

### Notas de diseño

`confirmado_at` implementa la parte de [`RF-P-12`][rf-p-12] que impide autonombrarse
mentor. El perfil existe desde que la persona lo solicita —con sus áreas y sus
certificaciones ya cargadas— pero no aparece como mentor disponible hasta que la
DIEM lo confirma. Sin esa distinción, la lista de mentores de la Dirección sería
una lista de aspirantes.

`descripcion_profesional` se conserva en prosa además de las áreas
estructuradas. Los párrafos del listado real dicen cosas que ningún catálogo
captura —cuántos años de experiencia, en qué combinación de disciplinas— y
perderlos al normalizar sería un retroceso frente a la hoja de cálculo.

---

## `mentor_area_experiencia`

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 150-800 filas

|       Campo        |   Tipo    | Nulo | Predeterminado |            Descripción             |
| :----------------: | :-------: | :--: | :------------: | :--------------------------------: |
| `perfil_mentor_id` |  `uuid`   |  no  |                |      Llave foránea `CASCADE`       |
|     `area_id`      |  `uuid`   |  no  |                | Llave foránea a `area_experiencia` |
|   `es_principal`   | `boolean` |  no  |    `false`     |   Área de especialidad declarada   |

|           Nombre           |               Definición                |         Propósito         |
| :------------------------: | :-------------------------------------: | :-----------------------: |
|    `unq_mentorarea_par`    |      `(perfil_mentor_id, area_id)`      |   No se repite un área    |
| `unq_mentorarea_principal` | `(perfil_mentor_id) WHERE es_principal` | Como máximo una principal |

---

## `mentor_certificacion`

Certificaciones nacionales o internacionales del mentor. La matriz las guarda
como una lista numerada dentro de una celda; aquí es una fila cada una.

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 100-600 filas
- **Origen:**
  > - [`RF-A-11`][rf-a-11]

### Columnas

|       Campo        |      Tipo      | Nulo | Predeterminado |        Descripción        |
| :----------------: | :------------: | :--: | :------------: | :-----------------------: |
| `perfil_mentor_id` |     `uuid`     |  no  |                |  Llave foránea `CASCADE`  |
|      `nombre`      | `varchar(200)` |  no  |                | Denominación del programa |
|   `institucion`    | `varchar(200)` |  no  |      `''`      |   Entidad que la emitió   |
|       `pais`       |  `varchar(2)`  |  no  |      `''`      | Código ISO de dos letras  |
|       `anio`       |   `smallint`   |  sí  |                |     Año de obtención      |
|    `enlace_url`    | `varchar(500)` |  no  |      `''`      |  Verificación, si existe  |

### Constraints

```postgresql
CONSTRAINT chk_mentorcertificacion_anio
CHECK (anio IS NULL OR anio BETWEEN 1960 AND EXTRACT(year FROM CURRENT_DATE) + 1)
```

### Notas de diseño

Extraer las certificaciones de la celda de texto es lo que convierte _¿qué
mentores tienen certificación en marketing digital?_ de una lectura manual en una
consulta. El costo es que la importación de la matriz tiene que partir un párrafo
numerado, operación que [`RF-A-49`][rf-a-49] resuelve dejando el texto original
en la fila de importación cuando no logra separarlo, para que nada se pierda.

`anio` admite el año siguiente al actual porque las certificaciones en curso se
declaran con su año previsto de obtención.

[auditoria]: ../convenciones.md#auditoria-por-tabla
[catalogos]: catalogos.md
[d-17]: ../decisiones.md#d-17
[rf-a-10]: ../../requerimientos/funcionales/administracion.md#rf-a-10
[rf-a-11]: ../../requerimientos/funcionales/administracion.md#rf-a-11
[rf-a-12]: ../../requerimientos/funcionales/administracion.md#rf-a-12
[rf-a-13]: ../../requerimientos/funcionales/administracion.md#rf-a-13
[rf-a-44]: ../../requerimientos/funcionales/administracion.md#rf-a-44
[rf-a-49]: ../../requerimientos/funcionales/administracion.md#rf-a-49
[rf-p-08]: ../../requerimientos/funcionales/participantes.md#rf-p-08
[rf-p-09]: ../../requerimientos/funcionales/participantes.md#rf-p-09
[rf-p-10]: ../../requerimientos/funcionales/participantes.md#rf-p-10
[rf-p-11]: ../../requerimientos/funcionales/participantes.md#rf-p-11
[rf-p-12]: ../../requerimientos/funcionales/participantes.md#rf-p-12
[rf-p-13]: ../../requerimientos/funcionales/participantes.md#rf-p-13
[rn-04]: ../../requerimientos/reglas-negocio.md#rn-04
