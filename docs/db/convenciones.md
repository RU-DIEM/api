---
icon: lucide/ruler
---

# Convenciones

## Tipos de dato canónicos

Un concepto del dominio tiene exactamente un tipo. No se admiten dos columnas que
representen lo mismo con tipos distintos.

|          Concepto          |      Tipo      |                         Regla                          |
| :------------------------: | :------------: | :----------------------------------------------------: |
|       Llave primaria       |     `uuid`     |                     [`D-01`][d-01]                     |
|          Instante          | `timestamptz`  |                     [`D-02`][d-02]                     |
|      Fecha de negocio      |     `date`     |      Resuelta en `America/Managua` (`rudi_hoy()`)      |
|      Rango de fechas       |  `daterange`   |                    Vigencias, `[)`                     |
|       Año calendario       |   `smallint`   |               `CHECK` entre 2000 y 2100                |
|      Puntos otorgados      |   `smallint`   |         Con signo: los reversos son negativos          |
|     Contador acumulado     |   `integer`    |                                                        |
|       Texto acotado        |  `varchar(n)`  |        `n` proviene de un requerimiento citable        |
|        Texto libre         |     `text`     |            Sin cota, con `CHECK` de tamaño             |
| Código estable de catálogo | `varchar(50)`  |               Patrón `^[a-z][a-z0-9_]*$`               |
|   Lista cerrada externa    |  `varchar(n)`  |    `CHECK` contra un `TextChoices`, [`D-21`][d-21]     |
|       Código público       | `varchar(30)`  |      Folios y códigos de proyecto, en mayúsculas       |
|          Booleano          |   `boolean`    |           `NOT NULL` con `DEFAULT` explícito           |
|     Correo electrónico     | `varchar(254)` |     En `ApiUser`, único sobre las cuentas activas      |
|     Número telefónico      | `varchar(128)` | E.164 (`+50581234567`), `CHECK` de formato; `''` = sin |
|  Identificador de persona  | `varchar(20)`  |         CIF, cédula, pasaporte; siempre texto          |
| Documento semiestructurado |    `jsonb`     |    Solo donde el esquema es heterogéneo por diseño     |

### _¿Por qué el identificador es texto y no número?_

La cédula nicaragüense termina en letra y el CIF admite ceros a la izquierda.
Almacenarlos como número pierde ambos y convierte el identificador en un valor
que ya no se puede contrastar contra el documento físico. La matriz de
estudiantes lo advierte en su glosario y el modelo lo respeta.

La comparación para detectar duplicados se hace sobre un valor normalizado
—mayúsculas, sin guiones ni espacios— calculado como columna generada, para que
`001-150188-0001E` y `0011501880001E` sean el mismo identificador.

### _¿Por qué el teléfono en E.164?_

El campo es `PhoneNumberField(region="NI")`: la API acepta `8123 4567` o
`+505 8123 4567` y guarda siempre `+50581234567`. Un solo formato almacenado es
lo que permite el índice único parcial `unq_rudiuser_telefono`; con el número y
el país en columnas separadas, `+505 8123 4567` y `81234567` serían dos números.

### _¿Por qué acotar además con `CHECK`?_

`varchar(n)` obliga a reescribir la tabla para ampliar el límite. Las longitudes
que provienen de un requerimiento se declaran **además** como restricción de
verificación con nombre propio, que puede agregarse `NOT VALID` y validarse
después sin bloquear escrituras. El nombre aparece en el error y permite
identificar cuál de las reglas de la tabla se violó. Ver
[tipos de carácter][pg-datatype-character].

---

## Columnas estándar

Toda tabla de dominio incluye estas columnas, heredadas de la clase base del
template. No se repiten en las tablas de campos de cada ficha.

|   Columna    |     Tipo      | Nulo | Predeterminado |              Propósito              |
| :----------: | :-----------: | :--: | :------------: | :---------------------------------: |
|     `id`     |    `uuid`     |  no  |   `uuidv7()`   |           Llave primaria            |
| `created_at` | `timestamptz` |  no  |    `now()`     |          Instante de alta           |
| `updated_at` | `timestamptz` |  no  |    `now()`     | Mantenido por `trg_touch_updatedat` |

Las tablas `append-only` no llevan `updated_at`: una fila que nunca cambia no
puede tener fecha de última modificación, y tenerla sería afirmar algo falso
sobre la tabla. Las tablas con borrado lógico llevan además `is_active`.

Toda tabla lleva además dos protecciones heredadas de su clase base, no
declaradas fila por fila: `trg_protect_truncate`, que bloquea `TRUNCATE` a
nivel de sentencia, y `trg_readonly_primarykey`, que rechaza cualquier cambio
de la llave primaria. Los tres triggers de esta sección son la única excepción
al patrón `trg_<tabla>_<regla>` de [Nomenclatura][nomenclatura]: al vivir en la
clase base de la que heredan todas las tablas, se declaran una sola vez con un
nombre fijo en vez de uno por tabla.

`trg_touch_updatedat` es `BEFORE UPDATE` y se dispara con una condición
`AnyChange` que excluye la propia `updated_at`. En las tablas que llevan
columnas generadas **almacenadas** (`identificador_user`) la condición excluye
además esas columnas: PostgreSQL rechaza una condición de trigger `BEFORE` que
lea una columna generada.

`id` se genera con `uuidv7()`, que es ordenable en el tiempo. Eso lo convierte
en el desempate natural de toda consulta paginada: una página sin `ORDER BY`
determinista puede repetir u omitir filas entre peticiones, y ordenar por `id`
descendente da orden cronológico inverso sin costo adicional porque recorre la
llave primaria. Toda consulta paginada del sistema termina su cláusula de orden
con `id`.

---

## Política de nulabilidad

La regla depende del tipo, porque el nulo no significa lo mismo en todos.

!!! abstract "El nulo se admite solo donde no existe un valor de ausencia honesto:"

    === "**Booleanos**"

        - **Nunca nulos.** Un booleano nulo es una enumeración de tres valores
          mal declarada.
        - Si hacen falta tres estados, es un estado y va a su tabla de catálogo.
          El caso real es la autorización de tratamiento de datos, que tiene tres
          valores y por eso no es un booleano.

    === "**Texto y colecciones**"

        - **Nunca nulos.** El valor de ausencia es `''`, `[]` o `{}`, declarado
          como `DEFAULT`.
        - Dos valores vacíos obligan a escribir `col IS NOT NULL AND col <> ''`
          en cada predicado, y basta olvidar una mitad para que la consulta
          mienta.
        - Los índices y restricciones parciales usan `length(col) > 0` o
          `col <> ''`, que son exactos y no requieren `COALESCE`.

    === "**Todo lo demás**"

        - **`NULL` es el valor de ausencia.**
        - Aplica a `timestamptz`, `date`, `uuid` y `smallint`.
        - No hay centinela honesto en el dominio: `0` no es _sin puntos_ y
          `1970-01-01` no es _sin fecha de nacimiento_.
        - La ficha de la tabla declara si el nulo significa _todavía no aplica_ o
          _no aplica en esta variante_.

---

## Nomenclatura

Prefijo por tipo de objeto, seguido del nombre de la tabla y de los segmentos que
lo identifican. Los segmentos colapsan los guiones bajos internos del nombre de
columna (`validada_at` => `validadaat`) y omiten el sufijo `_id` de las llaves
foráneas, para respetar el límite de 63 bytes de los identificadores de
PostgreSQL.

|           Objeto            |          Patrón          |                  Ejemplo                   |
| :-------------------------: | :----------------------: | :----------------------------------------: |
|          Unicidad           | `unq_<tabla>_<columnas>` |           `unq_constancia_folio`           |
|        Verificación         |  `chk_<tabla>_<regla>`   |       `chk_actividad_cupo_coherente`       |
|          Exclusión          |  `excl_<tabla>_<regla>`  |      `excl_reglapuntuacion_vigencia`       |
|        Índice B-tree        | `idx_<tabla>_<columnas>` |    `idx_participacion_actividad_estado`    |
| Índice [`GIN`][pg-gin-gist] | `gin_<tabla>_<columna>`  | `gin_mentorprofile_descripcionprofesional` |
|           Trigger           |  `trg_<tabla>_<regla>`   |    `trg_inscripcion_transicion_valida`     |

Las restricciones se nombran **siempre** de forma explícita. Un nombre generado
por PostgreSQL (`inscripcion_check1`) aparece en el mensaje de error que ve el
usuario final a través de la API y no dice nada sobre la regla violada.

Los triggers de solo lectura son la segunda excepción al patrón, además de los
de la clase base: `trg_readonly_<columnas>` (`trg_readonly_codigo`,
`trg_readonly_origen_user`) y `trg_readonly_snapshot` en las tablas que
congelan columnas copiadas de otra. No imponen una regla propia: aplican el
mismo régimen genérico con otra lista de columnas, y el nombre uniforme hace
evidente que son el mismo mecanismo. Los nombres de trigger son únicos por
tabla en PostgreSQL, así que repetirlos no colisiona.

### Nombres generados por Django

Las restricciones, índices y triggers se declaran con `%(class)s`, que Django
expande al nombre de la clase del modelo **en minúsculas y sin separadores**
(`EstudianteCarrera` => `estudiantecarrera`), no al nombre de la tabla
(`rudiprofiles_estudiantecarrera`). Por eso `<tabla>` en los patrones de arriba
es siempre el nombre de la clase en minúsculas.

---

## Llaves primarias

Toda tabla de dominio usa una llave primaria `uuid` sustituta, por
[decisión transversal][d-06].

|          Relación          |           Declaración           |           Restricción           |
| :------------------------: | :-----------------------------: | :-----------------------------: |
|            1:1             | Llave foránea con índice único  |    `unq_<tabla>_<relacion>`     |
| Par único de dos entidades | `UNIQUE (columna_a, columna_b)` |      `unq_<tabla>_<a>_<b>`      |
|   Unicidad condicionada    |      Índice único parcial       | `unq_<tabla>_<columnas>_<caso>` |

---

## Llaves foráneas

La acción referencial se elige por la naturaleza de la relación, no por
uniformidad.

|                    Situación                     | `ON DELETE` |                            Justificación                             |
| :----------------------------------------------: | :---------: | :------------------------------------------------------------------: |
|             Referencia a un catálogo             | `RESTRICT`  |                            [`D-18`][d-18]                            |
|              Referencia a un estado              | `RESTRICT`  | Un estado referenciado por una fila histórica es parte del historial |
|       Referencia a una entidad de negocio        | `RESTRICT`  |                            [`D-08`][d-08]                            |
|          Actor de una acción registrada          | `RESTRICT`  |           El historial debe seguir nombrando a quien actuó           |
| Fila hija sin identidad propia fuera de la madre |  `CASCADE`  |        Su existencia carece de sentido si la madre desaparece        |

`ON UPDATE` no se declara en ninguna llave foránea: las llaves primarias son
inmutables por `trg_readonly_primarykey`, de modo que no hay actualización que
propagar.

Las llaves foráneas se declaran `DEFERRABLE INITIALLY DEFERRED`. La verificación
ocurre al cerrar la transacción, lo que permite escribir padre e hijo en el orden
que imponga la lógica. El precio es que una violación referencial aparece en el
`COMMIT` y no en la sentencia que la causó; cuando eso importa, la transacción
adelanta la verificación con `SET CONSTRAINTS ALL IMMEDIATE`.

### Cascadas del modelo

Solo cuatro relaciones son `CASCADE`, y todas comparten la misma forma: la fila
hija es un fragmento de la madre, carece de identidad de negocio propia y nadie
más la referencia.

- `estudiante_carrera` cuelga de `estudiante_profile`
- `mentor_area_experiencia` cuelga de `mentor_profile`
- `mentor_certificacion` cuelga de `mentor_profile`
- `equipo_miembro` cuelga de `equipo`

Como las madres no se borran (régimen protegido), la cascada solo describe la
dependencia: en la práctica no se dispara nunca. En todos los demás casos la
relación es entre entidades con vida propia, y el borrado del padre debe fallar
en lugar de arrastrar historia.

### Indexación

Toda llave foránea lleva un índice B-tree sobre su columna; Django lo crea por
defecto. PostgreSQL indexa automáticamente el lado referenciado, nunca el
referenciante, y sin ese índice cada verificación de la restricción recorre la
tabla hija completa. Las fichas solo listan índices de llave foránea cuando
tienen columnas adicionales o una condición parcial.

---

## Criterios de invariantes

Criterio único aplicado en todo el modelo. Ante la duda, gana la fila más alta de
la tabla: el mecanismo más barato y más difícil de evadir.

|               Tipo de regla                |                Mecanismo                 |                                _¿Por qué no el siguiente?_                                 |
| :----------------------------------------: | :--------------------------------------: | :----------------------------------------------------------------------------------------: |
| Depende solo de columnas de la propia fila |                 `CHECK`                  |                        Costo nulo en escritura, imposible de evadir                        |
|       Unicidad, incluso condicional        |     Índice único, parcial si aplica      |                          El motor la garantiza bajo concurrencia                           |
|         No solapamiento de rangos          |         `EXCLUDE`, `btree_gist`          | Único mecanismo correcto bajo concurrencia; ver [restricciones de exclusión][pg-exclusion] |
|     Existencia de una fila relacionada     |              Llave foránea               |                                                                                            |
|  Depende de otras filas de la misma tabla  |                 Trigger                  |                           `CHECK` no puede consultar otras filas                           |
|    Depende de una columna de otra tabla    |                 Trigger                  |                                       [`D-08`][d-08]                                       |
|    Depende de un parámetro configurable    |    Trigger que lee `rudi_parametro()`    |                                    [`RF-A-48`][rf-a-48]                                    |
|     Inmutabilidad de filas o columnas      |     Trigger `BEFORE` que lanza error     |                                       [`D-08`][d-08]                                       |
|     Derivación a partir de otra tabla      | Trigger `BEFORE` que escribe la columna  |      Una columna generada no puede referirse a otra fila; ver [`Triggers`][triggers]       |
|     Orquestación con efectos externos      | Servicio de aplicación en la transacción |                      El correo no puede participar de la transacción                       |

Las filas de trigger son la razón por la que el modelo tiene una página propia
para ellos. El contrato común, las familias de las que se derivan y el catálogo
completo están en [`Triggers`][triggers].

### Triggers que dereferencian llaves foráneas

Un trigger `BEFORE` se ejecuta antes de que se verifique la llave foránea de la
fila que lo dispara, porque esa verificación está diferida al cierre de la
transacción. Un trigger que lee la fila referenciada para copiar datos o
validar coherencia no puede asumir que esa fila existe.

Todos ellos comprueban la existencia como primer paso y lanzan una violación
referencial con la columna explícita. Sin esa comprobación, un identificador
inexistente produce el error que devuelva la consulta interna del trigger, que
no nombra la columna y llega al cliente como un conflicto genérico.

### Formato de las fichas de trigger

Cada trigger se documenta con seis campos, en este orden: **nombre**, **evento**,
**momento**, **nivel**, **regla que impone** y **requerimiento que la origina**.
Un trigger sin requerimiento asociado es un trigger que hay que justificar o
borrar.

La ficha de cada trigger vive en la página del módulo al que pertenece su
tabla. [`Triggers`][triggers] define el contrato que todas respetan y clasifica
el catálogo completo, distinguiendo lo que ya está implementado de lo que está
diseñado y pendiente.

---

## Columnas generadas

Una columna generada es `STORED` (`GeneratedField(db_persist=True)`) cuando se
indexa o sostiene una restricción: `identificador_user.valor_normalizado`,
`regla_puntuacion.especificidad`. Se paga una vez por escritura, no una vez por
lectura.

La expresión debe ser inmutable y solo puede referirse a columnas de la propia
fila. Una derivación que necesite datos de otra tabla no es columna generada: es
una columna normal que escribe el trigger de inserción y protege un trigger de
solo lectura (`participacion.anio`, `movimiento_punto.anio`). Ver
[columnas generadas][pg-ddl-generated].

---

## Auditoría por tabla

Cada régimen corresponde a una clase base del template. Elegir la clase base
**es** declarar el régimen; la ficha de cada tabla lo nombra.

!!! abstract "Toda tabla se clasifica en exactamente uno de estos tres regímenes:"

    === "**`append-only`**"

        - Clase base: `ApiAppendOnlyModel`.
        - Admite `INSERT`.
        - `UPDATE` y `DELETE` están bloqueados por un único trigger
          (`trg_append_only`).
        - No lleva tabla de eventos: la tabla ya es su propio historial.
        - Es el régimen de `indicador_periodo` y `acceso_dato_personal`.

    === "**Mutable protegida**"

        - Clase base: `ApiProtectedModel`.
        - Admite `INSERT` y `UPDATE`; las columnas que no deben cambiar se
          declaran de solo lectura (`ReadOnly`).
        - `DELETE` está bloqueado por `trg_protect_delete`.
        - Con `@track_table()` lleva además tabla de eventos.
        - Es el régimen de la persona, los perfiles, la participación, los
          movimientos de puntos y las constancias.

    === "**Mutable rastreada**"

        - Clase base: `ApiSoftDeleteModel` con `@track_table()`.
        - Admite `INSERT` y `UPDATE` libres.
        - `DELETE` no borra la fila: `trg_softdelete_isactive` lo reescribe en
          un `UPDATE` de `is_active = false`, así que la fila nunca
          desaparece.
        - Lleva una tabla de eventos gemela que registra inserción,
          actualización y borrado con el contexto de la petición.
        - Es el régimen de los catálogos, los estados, los programas y las
          instituciones.

La tabla de eventos (`<Modelo>Event`, de [pghistory][pghistory]) es
`append-only`, replica las columnas de la tabla rastreada y agrega el instante
del evento, su etiqueta y el contexto de la petición (`ApiEvent`: usuario,
método, ruta). Es el historial del sistema: no hay `bitacora` ni tablas
`*_evento` escritas a mano ([`D-15`][d-15]).

!!! warning "Sobre el `DELETE` de la persona"

    Ninguna ruta del sistema borra una persona: la baja es anonimización, por
    [`RF-A-50`][rf-a-50], y `trg_protect_delete` la respalda en el motor.

---

## Volumetría y retención

Una tabla se declara **de alto volumen** en su ficha cuando su crecimiento es
proporcional al tráfico y no al número de entidades de negocio:
`notificacion`, `acceso_dato_personal` y las tablas de eventos.

Todas solo crecen y ninguna es referenciada por otra tabla. Las del dominio
llevan su columna de retención indexada con [`BRIN`][pg-brin]; las de eventos
traen del template un índice B-tree sobre `pgh_created_at`, que además sirve a
la consulta de historial por fecha.

|         Tabla          | Columna de retención | Índice |
| :--------------------: | :------------------: | :----: |
|     `notificacion`     |     `created_at`     | `BRIN` |
| `acceso_dato_personal` |     `created_at`     | `BRIN` |
|   Tablas de eventos    |   `pgh_created_at`   | B-tree |

### _¿Por qué BRIN y no B-tree?_

Una tabla `append-only` se escribe en orden de tiempo, de modo que la columna de
retención está físicamente correlacionada con el orden de las páginas. Es
[el caso para el que existe `BRIN`][pg-brin]: el índice guarda el valor mínimo y
máximo de cada bloque de páginas en lugar de una entrada por fila.

### Escala esperada

El sistema atiende a una dirección universitaria, no a un mercado. Con el volumen
histórico de las matrices —cientos de personas y de participaciones al año— la
mayor parte del modelo cabe holgadamente en índices B-tree convencionales y
ninguna tabla requiere particionado.

La consecuencia práctica es que ninguna decisión de este modelo se toma por
rendimiento. Se toman todas por corrección, que es lo que corresponde cuando el
volumen no aprieta.

[nomenclatura]: #nomenclatura
[triggers]: triggers.md
[d-01]: decisiones.md#d-01
[d-02]: decisiones.md#d-02
[d-06]: decisiones.md#d-06
[d-08]: decisiones.md#d-08
[d-15]: decisiones.md#d-15
[d-18]: decisiones.md#d-18
[d-21]: decisiones.md#d-21
[pghistory]: https://django-pghistory.readthedocs.io/
[rf-a-48]: ../requerimientos/funcionales/administracion.md#rf-a-48
[rf-a-50]: ../requerimientos/funcionales/administracion.md#rf-a-50
