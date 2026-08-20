---
icon: lucide/ruler
---

# Convenciones

Reglas transversales del modelo físico.

---

## Tipos de dato canónicos

Un concepto del dominio tiene exactamente un tipo. No se admiten dos columnas que
representen lo mismo con tipos distintos.

|          Concepto          |      Tipo      |                      Regla                      |
| :------------------------: | :------------: | :---------------------------------------------: |
|       Llave primaria       |     `uuid`     |                 [`D-01`][d-01]                  |
|          Instante          | `timestamptz`  |                 [`D-02`][d-02]                  |
|      Fecha de negocio      |     `date`     |          Resuelta en `America/Managua`          |
|      Rango de fechas       |  `daterange`   |                 Vigencias, `[)`                 |
|       Año calendario       |   `smallint`   |            `CHECK` entre 2000 y 2100            |
|      Puntos otorgados      |   `smallint`   |      Con signo: los reversos son negativos      |
|     Contador acumulado     |   `integer`    |                                                 |
|       Texto acotado        |  `varchar(n)`  |    `n` proviene de un requerimiento citable     |
|        Texto libre         |     `text`     |         Sin cota, con `CHECK` de tamaño         |
| Código estable de catálogo | `varchar(50)`  |           Patrón `^[a-z][a-z0-9_]*$`            |
|       Código público       | `varchar(30)`  |   Folios y códigos de proyecto, en mayúsculas   |
|          Booleano          |   `boolean`    |       `NOT NULL` con `DEFAULT` explícito        |
|     Correo electrónico     | `varchar(254)` |      Único por índice sobre `lower(email)`      |
|     Número telefónico      |  `varchar(8)`  |    Ocho dígitos, con país en columna aparte     |
|  Identificador de persona  | `varchar(20)`  |      CIF, cédula, pasaporte; siempre texto      |
| Documento semiestructurado |    `jsonb`     | Solo donde el esquema es heterogéneo por diseño |
|        Dirección IP        |     `inet`     |                                                 |

### _¿Por qué el identificador es texto y no número?_

La cédula nicaragüense termina en letra y el CIF admite ceros a la izquierda.
Almacenarlos como número pierde ambos y convierte el identificador en un valor
que ya no se puede contrastar contra el documento físico. La matriz de
estudiantes lo advierte en su glosario y el modelo lo respeta.

La comparación para detectar duplicados se hace sobre un valor normalizado
—mayúsculas, sin guiones ni espacios— calculado como columna generada, para que
`001-150188-0001E` y `0011501880001E` sean el mismo identificador.

### _¿Por qué acotar además con `CHECK`?_

`varchar(n)` obliga a reescribir la tabla para ampliar el límite. Las longitudes
que provienen de un requerimiento se declaran **además** como restricción de
verificación con nombre propio, que puede agregarse `NOT VALID` y validarse
después sin bloquear escrituras. El nombre aparece en el error y permite
identificar cuál de las reglas de la tabla se violó. Ver
[tipos de carácter][pg-datatype-character].

---

## Columnas estándar

Toda tabla de dominio incluye estas columnas. No se repiten en las tablas de
campos de cada ficha.

|   Columna    |     Tipo      | Nulo | Predeterminado |             Propósito             |
| :----------: | :-----------: | :--: | :------------: | :-------------------------------: |
|     `id`     |    `uuid`     |  no  |   `uuidv7()`   |          Llave primaria           |
| `created_at` | `timestamptz` |  no  |    `now()`     |         Instante de alta          |
| `updated_at` | `timestamptz` |  no  |    `now()`     | Mantenido por `trg_<tabla>_touch` |

Las tablas `append-only` no llevan `updated_at`: una fila que nunca cambia no
puede tener fecha de última modificación, y tenerla sería afirmar algo falso
sobre la tabla.

Toda tabla lleva además dos protecciones: `trg_<tabla>_no_truncate`, que bloquea
`TRUNCATE` a nivel de sentencia, y `trg_<tabla>_readonly_id`, que rechaza
cualquier cambio de la llave primaria.

`id` se genera con `uuidv7()`, que es ordenable en el tiempo. Eso lo convierte en
el desempate natural de toda consulta paginada: una página sin `ORDER BY`
determinista puede repetir u omitir filas entre peticiones. Toda consulta
paginada del sistema termina su cláusula de orden con `id`.

### `actualizado_at` frente a `updated_at`

Son cosas distintas y coexisten en las tablas de perfil.

- `updated_at` es técnico: lo escribe un trigger en cada `UPDATE`, incluido el que
  solo corrige un espacio en blanco.
- `actualizado_at` es de negocio: registra cuándo la persona **confirmó** que sus
  datos siguen siendo correctos, con o sin cambios, por [`RF-P-13`][rf-p-13].

Las tres matrices de soporte llevan una columna de fecha de última actualización
y su glosario aclara que se trata de la revisión más reciente, no de la última
modificación. Colapsarlas en una sola columna perdería el dato que la DIEM
realmente usa para saber qué expedientes revisar.

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
        - Los índices y restricciones parciales usan `length(col) > 0`, que es
          exacto y no requiere `COALESCE`.

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

|           Objeto            |          Patrón          |               Ejemplo                |
| :-------------------------: | :----------------------: | :----------------------------------: |
|       Llave primaria        |       `pk_<tabla>`       |          `pk_participacion`          |
|        Llave foránea        |  `fk_<tabla>_<columna>`  |     `fk_participacion_actividad`     |
|          Unicidad           | `unq_<tabla>_<columnas>` |        `unq_constancia_folio`        |
|        Verificación         |  `chk_<tabla>_<regla>`   |    `chk_actividad_cupo_coherente`    |
|          Exclusión          |  `exc_<tabla>_<regla>`   |    `exc_reglapuntuacion_vigencia`    |
|        Índice B-tree        | `idx_<tabla>_<columnas>` | `idx_participacion_actividad_estado` |
| Índice [`GIN`][pg-gin-gist] | `gin_<tabla>_<columna>`  |     `gin_usuario_nombrecompleto`     |
|           Trigger           |  `trg_<tabla>_<regla>`   |    `trg_participacion_no_borrar`     |
|     Vista materializada     |      `mv_<asunto>`       |     `mv_participante_unico_anio`     |

Las restricciones se nombran **siempre** de forma explícita. Un nombre generado
por PostgreSQL (`inscripcion_check1`) aparece en el mensaje de error que ve el
usuario final a través de la interfaz y no dice nada sobre la regla violada.

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
|          Actor de una acción registrada          | `RESTRICT`  |           La bitácora debe seguir nombrando a quien actuó            |
| Fila hija sin identidad propia fuera de la madre |  `CASCADE`  |        Su existencia carece de sentido si la madre desaparece        |

`ON UPDATE` no se declara en ninguna llave foránea: las llaves primarias son
inmutables por `trg_<tabla>_readonly_id`, de modo que no hay actualización que
propagar.

Las llaves foráneas se declaran `DEFERRABLE INITIALLY DEFERRED`. La verificación
ocurre al cerrar la transacción, lo que permite escribir padre e hijo en el orden
que imponga la lógica. El precio es que una violación referencial aparece en el
`COMMIT` y no en la sentencia que la causó; cuando eso importa, la transacción
adelanta la verificación con `SET CONSTRAINTS ALL IMMEDIATE`.

### Cascadas del modelo

Solo cinco relaciones son `CASCADE`, y todas comparten la misma forma: la fila
hija es un fragmento de la madre, carece de identidad de negocio propia y nadie
más la referencia.

- `estudiante_carrera` cuelga de `perfil_estudiante`
- `mentor_area_experiencia` cuelga de `perfil_mentor`
- `mentor_certificacion` cuelga de `perfil_mentor`
- `equipo_miembro` cuelga de `equipo`
- `importacion_fila` cuelga de `importacion`

En todos los demás casos la relación es entre entidades con vida propia, y el
borrado del padre debe fallar en lugar de arrastrar historia.

### Indexación

Toda llave foránea lleva un índice B-tree sobre su columna. PostgreSQL indexa
automáticamente el lado referenciado, nunca el referenciante, y sin ese índice
cada verificación de la restricción recorre la tabla hija completa. Las fichas
solo listan índices de llave foránea cuando tienen columnas adicionales o una
condición parcial.

---

## Criterios de invariantes

Criterio único aplicado en todo el modelo. Ante la duda, gana la fila más alta de
la tabla: el mecanismo más barato y más difícil de evadir.

|               Tipo de regla                |              Mecanismo              |                                _¿Por qué no el siguiente?_                                 |
| :----------------------------------------: | :---------------------------------: | :----------------------------------------------------------------------------------------: |
| Depende solo de columnas de la propia fila |               `CHECK`               |                        Costo nulo en escritura, imposible de evadir                        |
|       Unicidad, incluso condicional        |   Índice único, parcial si aplica   |                          El motor la garantiza bajo concurrencia                           |
|         No solapamiento de rangos          |       `EXCLUDE`, `btree_gist`       | Único mecanismo correcto bajo concurrencia; ver [restricciones de exclusión][pg-exclusion] |
|     Existencia de una fila relacionada     |            Llave foránea            |                                                                                            |
|  Depende de otras filas de la misma tabla  |               Trigger               |                           `CHECK` no puede consultar otras filas                           |
|    Depende de una columna de otra tabla    |               Trigger               |                                       [`D-08`][d-08]                                       |
|    Depende de un parámetro configurable    | Trigger que lee `parametro_sistema` |                                    [`RF-A-48`][rf-a-48]                                    |
|     Inmutabilidad de filas o columnas      |  Trigger `BEFORE` que lanza error   |                                       [`D-08`][d-08]                                       |

### Formato de las fichas de trigger

Cada trigger se documenta con seis campos, en este orden: **nombre**, **evento**,
**momento**, **nivel**, **regla que impone** y **requerimiento que la origina**.
Un trigger sin requerimiento asociado es un trigger que hay que justificar o
borrar.

---

## Auditoría por tabla

!!! abstract "Toda tabla se clasifica en exactamente uno de estos tres regímenes:"

    === "**`append-only`**"

        - Admite `INSERT`.
        - `UPDATE` y `DELETE` están bloqueados por trigger.
        - No lleva tabla de eventos: la tabla ya es su propio historial.
        - Es el régimen de `movimiento_punto`, `bitacora`, `participacion_evento`,
          `propuesta_evento`, `indicador_periodo` e `intento_acceso`.

    === "**Mutable protegida**"

        - Admite `INSERT` y `UPDATE` sobre un subconjunto declarado de columnas.
        - `DELETE` está bloqueado y las columnas fuera del subconjunto son de solo
          lectura.
        - Es el régimen de `participacion`, `constancia`, `inscripcion` y de todas
          las tablas de estado y catálogo.

    === "**Mutable rastreada**"

        - Admite `UPDATE` y `DELETE`.
        - Lleva una tabla de eventos gemela que registra inserción, actualización
          y borrado con el contexto de la petición.
        - Es el régimen de `usuario`, los perfiles y `actividad`.

La tabla de eventos del tercer régimen es `append-only`, replica las columnas de
la tabla rastreada y agrega el instante del evento, su etiqueta y el contexto de
la petición en `jsonb`.

!!! warning "Sobre el `DELETE` en el régimen rastreado"

    Que el régimen lo admita no significa que la interfaz lo ofrezca. Ninguna ruta
    del sistema borra un `usuario`: la baja es anonimización, por
    [`RF-A-50`][rf-a-50]. El régimen rastreado existe para que una corrección
    ejecutada por migración quede registrada, no para exponer un botón de
    eliminar.

---

## Volumetría y retención

Una tabla se declara **de alto volumen** en su ficha cuando su crecimiento es
proporcional al tráfico y no al número de entidades de negocio: `bitacora`,
`intento_acceso`, `notificacion`, `participacion_evento` y las tablas de eventos.

Todas son `append-only`, ninguna es referenciada por otra tabla, y todas llevan
una columna de retención indexada con [`BRIN`][pg-brin].

|         Tabla          | Columna de retención |
| :--------------------: | :------------------: |
|       `bitacora`       |     `created_at`     |
|    `intento_acceso`    |     `created_at`     |
|     `notificacion`     |     `created_at`     |
| `participacion_evento` |    `ocurrido_at`     |
|   Tablas de eventos    | Instante del evento  |

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
volumen no aprieta. Ver [`R-09`][r-09].

[d-01]: decisiones.md#d-01
[d-02]: decisiones.md#d-02
[d-06]: decisiones.md#d-06
[d-08]: decisiones.md#d-08
[d-18]: decisiones.md#d-18
[r-09]: riesgos.md#r-09
[rf-a-48]: ../requerimientos/funcionales/administracion.md#rf-a-48
[rf-a-50]: ../requerimientos/funcionales/administracion.md#rf-a-50
[rf-p-13]: ../requerimientos/funcionales/participantes.md#rf-p-13
