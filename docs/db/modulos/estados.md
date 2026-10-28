---
icon: lucide/git-branch
---

# Estados

Ningún estado del sistema se almacena como cadena de texto. Cada entidad con
ciclo de vida referencia por llave foránea una tabla de catálogo propia, que puede
ampliarse con filas nuevas sin migrar el esquema.

Esta página define el patrón, el reparto de responsabilidades entre el catálogo y
las marcas temporales de la entidad, y el catálogo completo de los ocho dominios
de estado del modelo.

## Requerimientos cubiertos

- [`RF-A-17`][rf-a-17]
- [`RF-A-26`][rf-a-26]
- [`RF-A-29`][rf-a-29]
- [`RF-A-36`][rf-a-36]
- [`RF-A-41`][rf-a-41]

---

## Taxonomía de enumeraciones

No toda enumeración cerrada es un estado. Convertirlas todas en tablas prometería
una extensibilidad que no existe, y dejarlas todas como texto perdería la que sí
existe. El modelo distingue tres clases y aplica un mecanismo distinto a cada una.

!!! example "Clases de enumeración y sus mecanismos"

    === "**Estado**"

        - Posición de una entidad en su ciclo de vida.
        - Cambia con el tiempo para una misma fila y gobierna qué operaciones se
          admiten.
        - Agregar un valor es una decisión operativa, no una migración.
        - **Mecanismo:** tabla `estado_<entidad>` y llave foránea.

    === "**Discriminador estructural**"

        - Distingue variantes de una fila que tienen columnas obligatorias
          distintas.
        - No cambia durante la vida de la fila.
        - **Mecanismo:** `varchar` y `CHECK` con la lista de valores.
        - **Ejemplos:** `actividad.modalidad`, `motivo.ambito`,
          `codigo_verificacion.proposito`, `importacion.matriz`.

    === "**Catálogo administrable**"

        - Valor de negocio que la DIEM da de alta, edita y desactiva sin que el
          comportamiento del sistema cambie.
        - **Mecanismo:** tabla propia con `activo`.
        - **Ejemplos:** `carrera`, `etnia`, `rol_participacion`, `tipo_actividad`,
          descritos en [`Catálogos`][catalogos].

La prueba para separar estado de discriminador: **si agregar un valor nuevo
obliga a agregar columnas que solo aplican a ese valor, es un discriminador.**

`actividad.modalidad` es el caso claro: presencial, virtual e híbrida. Añadir una
modalidad nueva no cambia nada del motor, pero tampoco cambia nunca para una
actividad dada una vez publicada, y no tiene ciclo. Es discriminador, no estado.

---

## Reparto de responsabilidades

El catálogo de estado y la entidad gobernada cubren necesidades distintas y no
compiten.

|             Responsabilidad             |           Dónde vive           |                          Por qué                          |
| :-------------------------------------: | :----------------------------: | :-------------------------------------------------------: |
| Etiqueta y descripción para la interfaz |       `estado_<entidad>`       |              Editable sin migrar el esquema               |
|     Semántica que consulta el motor     |       `estado_<entidad>`       | Agregar un estado es declarar sus atributos, no ramificar |
|          Transiciones legales           |     `transicion_<entidad>`     |                      [`D-10`][d-10]                       |
| Subconjunto vivo para índices parciales |  Marcas temporales de la fila  |                      [`D-09`][d-09]                       |
|         Coherencia entre ambos          | `trg_<tabla>_estado_coherente` |         Un `CHECK` no puede consultar otra tabla          |

La entidad gobernada lleva **marcas temporales** que registran sus transiciones
—`cancelada_at`, `validada_at`, `anulada_at`, `emitida_at`— y que existen de todos
modos por obligación de auditoría. Esas marcas son las que sostienen los índices
parciales, porque el predicado de un índice solo admite expresiones inmutables
sobre columnas de la propia fila.

```postgresql
CREATE UNIQUE INDEX unq_inscripcion_persona_activa
ON inscripcion (usuario_id, actividad_id)
WHERE cerrada_at IS NULL;
```

Este índice es el que hace cumplir [`RN-05`][rn-05] bajo concurrencia. Una
comprobación previa en la aplicación dejaría pasar dos peticiones simultáneas del
mismo estudiante pulsando dos veces el botón, que es como se produce la mayoría
de los duplicados reales.

---

## `estado_<entidad>`

Forma base que comparten los ocho catálogos de estado, además de las
[columnas estándar][convenciones-columnas].

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 3-7 filas por dominio
- **Origen:**
  > - [`RF-A-17`][rf-a-17]
  > - [`RF-A-48`][rf-a-48]

### Columnas

|     Campo     |     Tipo      | Nulo | Predeterminado |                   Descripción                   |
| :-----------: | :-----------: | :--: | :------------: | :---------------------------------------------: |
|   `codigo`    | `varchar(50)` |  no  |                |   Identificador estable citado por servicios    |
|  `etiqueta`   | `varchar(60)` |  no  |                |          Nombre visible en la interfaz          |
| `descripcion` |    `text`     |  no  |      `''`      |    Qué significa el estado para quien lo lee    |
| `es_inicial`  |   `boolean`   |  no  |    `false`     | El motor asigna este estado al crear la entidad |
| `es_terminal` |   `boolean`   |  no  |    `false`     |        No admite transiciones salientes         |
|    `orden`    |  `smallint`   |  no  |      `0`       |    Posición en los selectores de la interfaz    |
|   `activo`    |   `boolean`   |  no  |     `true`     |         Puede asignarse a filas nuevas          |

A estos campos comunes cada dominio agrega sus **atributos semánticos**: los
booleanos que el motor consulta en lugar de comparar contra `codigo`. Son el
contrato de la tabla y están catalogados más abajo, uno por dominio.

### Constraints

```postgresql
CONSTRAINT chk_estado_codigo_formato
CHECK (codigo ~ '^[a-z][a-z0-9_]*$')

CONSTRAINT chk_estado_terminal_no_inicial
CHECK (NOT (es_inicial AND es_terminal))

CONSTRAINT chk_estado_inicial_activo
CHECK (NOT es_inicial OR activo)
```

### Unicidad

|             Nombre             |         Definición          |                    Propósito                    |
| :----------------------------: | :-------------------------: | :---------------------------------------------: |
| `unq_estado_<entidad>_codigo`  |         `(codigo)`          | El código es la referencia estable del servicio |
| `unq_estado_<entidad>_inicial` | `((true)) WHERE es_inicial` |    Como máximo un estado inicial por dominio    |

### Triggers

|                 Nombre                 |       Evento       | Momento  | Nivel |                Regla                 |     Origen     |
| :------------------------------------: | :----------------: | :------: | :---: | :----------------------------------: | :------------: |
| `trg_estado_<entidad>_codigo_readonly` | `UPDATE OF codigo` | `BEFORE` | `ROW` | Rechaza cualquier cambio de `codigo` | [`D-08`][d-08] |
|    `trg_estado_<entidad>_no_borrar`    |      `DELETE`      | `BEFORE` | `ROW` |          Bloquea el borrado          | [`D-18`][d-18] |
|      `trg_estado_<entidad>_touch`      |      `UPDATE`      | `BEFORE` | `ROW` |        Actualiza `updated_at`        |   Convención   |

### Régimen de auditoría

> [**Mutable protegida**][mut-protegida]

`codigo` es de solo lectura: cambiarlo rompería todo servicio que lo mencione y
toda referencia en esta documentación. Las etiquetas, descripciones, atributos
semánticos y `activo` sí son editables. `DELETE` está bloqueado: un estado
referenciado por una sola fila histórica es parte del historial.

---

## `transicion_<entidad>`

Cuatro entidades llevan su máquina de estados como datos, en una tabla que
enumera los pares admitidos.

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 5-12 filas por dominio
- **Origen:**
  > - [`D-10`][d-10]

### Columnas

|       Campo       |     Tipo      | Nulo | Predeterminado |                      Descripción                      |
| :---------------: | :-----------: | :--: | :------------: | :---------------------------------------------------: |
|    `desde_id`     |    `uuid`     |  no  |                |           Llave foránea al estado de origen           |
|    `hasta_id`     |    `uuid`     |  no  |                |          Llave foránea al estado de destino           |
|   `actor_tipo`    | `varchar(20)` |  no  |                |     `participante` / `administracion` / `sistema`     |
| `requiere_motivo` |   `boolean`   |  no  |    `false`     |     Exige `motivo_id` en la fila que transiciona      |
|  `requiere_nota`  |   `boolean`   |  no  |    `false`     |          Exige texto libre además del motivo          |
|     `activa`      |   `boolean`   |  no  |     `true`     | Permite retirar una transición sin borrar su historia |

### Llaves foráneas

|  Columna   |     Referencia     | `ON DELETE` | Notas |
| :--------: | :----------------: | :---------: | :---: |
| `desde_id` | `estado_<entidad>` | `RESTRICT`  |       |
| `hasta_id` | `estado_<entidad>` | `RESTRICT`  |       |

### Constraints

```postgresql
CONSTRAINT chk_transicion_no_reflexiva
CHECK (desde_id <> hasta_id)

CONSTRAINT chk_transicion_actor
CHECK (actor_tipo IN ('participante', 'administracion', 'sistema'))
```

### Unicidad

|             Nombre             |             Definición             |             Propósito              |
| :----------------------------: | :--------------------------------: | :--------------------------------: |
| `unq_transicion_<entidad>_par` | `(desde_id, hasta_id, actor_tipo)` | Una transición por par y por actor |

### Notas de diseño

`actor_tipo` está en la transición y no en un permiso general porque la misma
transición es legal para un actor e ilegal para otro. Cancelar una inscripción lo
puede hacer la propia persona; anular una participación validada, solo la
administración. Declararlo como dato evita que esa diferencia viva repartida
entre la interfaz y el servicio.

---

## Catálogo de dominios de estado

Ocho dominios. La columna de atributos semánticos lista los booleanos propios de
cada uno, que se suman a los seis campos de la forma base.

|          Dominio           |                                   Estados                                    |                        Atributos semánticos                        |
| :------------------------: | :--------------------------------------------------------------------------: | :----------------------------------------------------------------: |
|      `estado_usuario`      |       `pendiente_verificacion`, `activa`, `suspendida`, `anonimizada`        |  `permite_ingreso`, `permite_inscripcion`, `visible_en_reportes`   |
|  `estado_consentimiento`   |        `otorgado`, `pendiente_verificar`, `no_autorizado`, `retirado`        |        `habilita_reporte_nominal`, `habilita_comunicacion`         |
|     `estado_actividad`     |        `borrador`, `publicada`, `en_curso`, `finalizada`, `cancelada`        |    `visible_publico`, `admite_inscripcion`, `admite_validacion`    |
|    `estado_inscripcion`    |       `pendiente`, `confirmada`, `en_espera`, `cancelada`, `rechazada`       |         `ocupa_cupo`, `es_cierre`, `admite_participacion`          |
|   `estado_participacion`   | `registrada`, `en_curso`, `finalizada`, `retirada`, `no_completo`, `anulada` | `es_efectiva`, `otorga_puntos`, `habilita_constancia`, `es_cierre` |
| `estado_asignacion_mentor` | `propuesta`, `confirmada`, `declinada`, `finalizada`, `cancelada`, `vencida` |           `es_acompañamiento_vigente`, `visible_publico`           |
|    `estado_constancia`     |                     `emitida`, `anulada`, `reemplazada`                      |                      `es_valida`, `es_cierre`                      |
|     `estado_propuesta`     |  `activa`, `en_pausa`, `finalizada`, `implementada`, `cerrada`, `integrada`  |         `es_vigente`, `cuenta_en_portafolio`, `es_cierre`          |

Los dominios con `transicion_<entidad>` son cuatro: `actividad`, `inscripcion`,
`participacion` y `propuesta`. Los otros cuatro cambian por caminos demasiado
simples para justificar una tabla de pares.

### Los tres atributos que evitan la mayor parte de los `CASE`

|       Atributo        |                                                             Qué resuelve                                                              |
| :-------------------: | :-----------------------------------------------------------------------------------------------------------------------------------: |
|     `ocupa_cupo`      |         El contador de inscritos suma solo los estados que lo declaran, de modo que cancelar libera cupo sin lógica adicional         |
|     `es_efectiva`     | El conteo de participantes reales de [`RN-13`][rn-13] filtra por este booleano y no por una lista de códigos escrita en cada consulta |
| `habilita_constancia` |                         [`RN-15`][rn-15] se comprueba leyendo el catálogo, no comparando contra `finalizada`                          |

El valor de esto se ve al añadir un estado. Cuando la DIEM decida distinguir
_finalizada con excelencia_ de _finalizada_, es una fila con `es_efectiva` y
`habilita_constancia` en verdadero. Sin los atributos, sería buscar en todo el
código dónde dice `= 'finalizada'`.

### Estados que el modelo se negó a crear

|          Estado descartado           |                                                  Por qué no existe                                                   |
| :----------------------------------: | :------------------------------------------------------------------------------------------------------------------: |
|       `inscripcion.no_asistio`       | La no asistencia es un desenlace de participación, no de inscripción; ponerlo aquí obligaría a validar en dos tablas |
|  `actividad.inscripciones_abiertas`  |                   Es una consecuencia de las fechas de la ventana, no un estado que alguien decida                   |
| `participacion.pendiente_validacion` |   Es la ausencia de `validada_at`, no un estado; tenerlo permitiría la contradicción de estar pendiente y validada   |

[auditoria]: ../convenciones.md#auditoria-por-tabla
[catalogos]: catalogos.md
[convenciones-columnas]: ../convenciones.md#columnas-estandar
[d-08]: ../decisiones.md#d-08
[d-09]: ../decisiones.md#d-09
[d-10]: ../decisiones.md#d-10
[d-18]: ../decisiones.md#d-18
[mut-protegida]: ../convenciones.md#auditoria-por-tabla
[rf-a-17]: ../../requerimientos/funcionales/administracion.md#rf-a-17
[rf-a-26]: ../../requerimientos/funcionales/administracion.md#rf-a-26
[rf-a-29]: ../../requerimientos/funcionales/administracion.md#rf-a-29
[rf-a-36]: ../../requerimientos/funcionales/administracion.md#rf-a-36
[rf-a-41]: ../../requerimientos/funcionales/administracion.md#rf-a-41
[rf-a-48]: ../../requerimientos/funcionales/administracion.md#rf-a-48
[rn-05]: ../../requerimientos/reglas-negocio.md#rn-05
[rn-13]: ../../requerimientos/reglas-negocio.md#rn-13
[rn-15]: ../../requerimientos/reglas-negocio.md#rn-15
