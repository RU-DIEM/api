---
icon: lucide/git-branch
---

# Estados

Ningún estado del sistema se almacena como cadena de texto. Cada entidad con
ciclo de vida referencia por llave foránea una tabla de catálogo propia, que puede
ampliarse con filas nuevas sin migrar el esquema.

Esta página define el patrón, el reparto de responsabilidades entre el catálogo y
las marcas temporales de la entidad, y el catálogo completo de los ocho dominios
de estado del modelo. Vive en la app `rudi_estados`.

## Requerimientos cubiertos

- [`RF-A-17`][rf-a-17]
- [`RF-A-26`][rf-a-26]
- [`RF-A-29`][rf-a-29]
- [`RF-A-36`][rf-a-36]
- [`RF-A-41`][rf-a-41]
- [`RF-A-48`][rf-a-48]

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

    === "**Discriminador o lista cerrada**"

        - Distingue variantes de una fila, o clasifica según un marco externo.
        - No cambia durante la vida de la fila, o solo por corrección.
        - **Mecanismo:** `varchar` y `CHECK` contra un `TextChoices`.
        - **Ejemplos:** `actividad.modalidad`, `motivo.ambito`,
          `rudi_user.origen`, `rudi_user.genero`, las [taxonomías][taxonomias].

    === "**Catálogo administrable**"

        - Valor de negocio que la DIEM da de alta, edita y desactiva sin que el
          comportamiento del sistema cambie.
        - **Mecanismo:** tabla propia con `is_active`.
        - **Ejemplos:** `carrera`, `rol_participacion`, `tipo_actividad`,
          descritos en [`Catálogos`][catalogos].

La prueba para separar estado de discriminador: **si agregar un valor nuevo
obliga a agregar columnas que solo aplican a ese valor, es un discriminador.**

---

## Reparto de responsabilidades

El catálogo de estado y la entidad gobernada cubren necesidades distintas y no
compiten.

|             Responsabilidad             |           Dónde vive           |                          Por qué                          |
| :-------------------------------------: | :----------------------------: | :-------------------------------------------------------: |
| Etiqueta y descripción para la interfaz |       `estado_<entidad>`       |              Editable sin migrar el esquema               |
|     Semántica que consulta el motor     |       `estado_<entidad>`       | Agregar un estado es declarar sus atributos, no ramificar |
|          Transiciones legales           | `transicion_estado_<entidad>`  |                      [`D-10`][d-10]                       |
| Subconjunto vivo para índices parciales |  Marcas temporales de la fila  |                      [`D-09`][d-09]                       |
|         Coherencia entre ambos          | `trg_<tabla>_estado_coherente` |         Un `CHECK` no puede consultar otra tabla          |

Las reglas que imponen las dos últimas filas son una familia completa de
triggers, definida en [`Triggers`][triggers-estado]. Aquí se describe el
contrato que esa familia lee; allá, cómo lo impone.

La entidad gobernada lleva **marcas temporales** que registran sus transiciones
—`cancelada_at`, `validada_at`, `anulada_at`, `emitida_at`— y que existen de todos
modos por obligación de auditoría. Esas marcas son las que sostienen los índices
parciales, porque el predicado de un índice solo admite expresiones inmutables
sobre columnas de la propia fila.

```postgresql
CREATE UNIQUE INDEX unq_inscripcion_persona_activa
ON rudiparticipacion_inscripcion (user_id, actividad_id)
WHERE cerrada_at IS NULL;
```

Este índice es el que hace cumplir [`RN-05`][rn-05] bajo concurrencia. Una
comprobación previa en la aplicación dejaría pasar dos peticiones simultáneas del
mismo estudiante pulsando dos veces el botón, que es como se produce la mayoría
de los duplicados reales.

---

## `estado_<entidad>`

Forma base que comparten los ocho catálogos de estado (`RudiEstado`), heredada
de `ApiSoftDeleteModel`.

- **Régimen:** [Mutable rastreada][auditoria]
- **Volumen estimado:** 3-7 filas por dominio
- **Origen:**
  > - [`RF-A-17`][rf-a-17]
  > - [`RF-A-48`][rf-a-48]

### Columnas

Además de las [columnas estándar][convenciones-columnas] y de `is_active`:

|     Campo     |     Tipo      | Nulo | Predeterminado |                   Descripción                   |
| :-----------: | :-----------: | :--: | :------------: | :---------------------------------------------: |
|   `codigo`    | `varchar(50)` |  no  |                |   Identificador estable citado por servicios    |
|  `etiqueta`   | `varchar(50)` |  no  |                |          Nombre visible en la interfaz          |
| `descripcion` |    `text`     |  no  |      `''`      |    Qué significa el estado para quien lo lee    |
|   `initial`   |   `boolean`   |  no  |    `false`     | El motor asigna este estado al crear la entidad |
|  `terminal`   |   `boolean`   |  no  |    `false`     |        No admite transiciones salientes         |

A estos campos comunes cada dominio agrega sus **atributos semánticos**: los
booleanos que el motor consulta en lugar de comparar contra `codigo`. Se
componen a partir de cinco mixins compartidos (`allow_inscripcion`, `public`,
`require_motivo`, `source`, `vigente`) más, en cada dominio, columnas propias.

Los prefijos fijan la dirección en que se lee el atributo:

|   Prefijo   |                     Se lee                      |                               Ejemplo                                |
| :---------: | :---------------------------------------------: | :------------------------------------------------------------------: |
|  `allow_*`  | Estando **en** este estado, la acción se admite | `allow_inscripcion` en `activa`: una cuenta activa puede inscribirse |
|  `public`   | Estando **en** este estado, la fila es visible  |       `public` en `publicada`: la actividad aparece al público       |
| `require_*` |    Para **llegar a** este estado hace falta     |   `require_motivo` en `suspendida`: suspender exige elegir motivo    |

### Constraints

```postgresql
CONSTRAINT chk_<estado>_codigo_format
CHECK (codigo ~ '^[a-z][a-z0-9_]*$')

CONSTRAINT chk_<estado>_initial_isactive
CHECK (NOT initial OR is_active)

CONSTRAINT chk_<estado>_initial_terminal
CHECK (NOT (initial AND terminal))
```

### Unicidad

|         Nombre         |       Definición       |                    Propósito                    |
| :--------------------: | :--------------------: | :---------------------------------------------: |
| `unq_<estado>_codigo`  |       `(codigo)`       | El código es la referencia estable del servicio |
| `unq_<estado>_initial` | `(true) WHERE initial` |    Como máximo un estado inicial por dominio    |

### Triggers

Los cuatro primeros los heredan todas las tablas del modelo con borrado lógico
(ver [Columnas estándar][convenciones-columnas]); el último es propio de la
forma base.

|          Nombre           |       Evento       | Momento  |    Nivel    |                                 Regla                                 |     Origen     |
| :-----------------------: | :----------------: | :------: | :---------: | :-------------------------------------------------------------------: | :------------: |
|  `trg_protect_truncate`   |     `TRUNCATE`     | `BEFORE` | `STATEMENT` |                          Bloquea el truncado                          |   Convención   |
| `trg_readonly_primarykey` |   `UPDATE OF id`   | `BEFORE` |    `ROW`    |                   Rechaza cualquier cambio de `id`                    |   Convención   |
|   `trg_touch_updatedat`   |      `UPDATE`      | `BEFORE` |    `ROW`    |                        Actualiza `updated_at`                         |   Convención   |
| `trg_softdelete_isactive` |      `DELETE`      | `BEFORE` |    `ROW`    | Reescribe el borrado en `is_active = false`, la fila nunca desaparece | [`D-18`][d-18] |
|   `trg_readonly_codigo`   | `UPDATE OF codigo` | `BEFORE` |    `ROW`    |                 Rechaza cualquier cambio de `codigo`                  | [`D-08`][d-08] |

### Variante con origen

`estado_consentimiento` y `estado_inscripcion` tienen **un estado inicial por
origen** del registro (`usuario`, `sistema`, `importacion`): una inscripción
hecha por la persona nace `pendiente`, una importada de las matrices nace
`confirmada`. Heredan de `RudiSourceAwareEstado`, que agrega `source` y cambia
`unq_<estado>_initial` por estas reglas:

```postgresql
CONSTRAINT chk_<estado>_source_initial
CHECK (
  (initial AND source ~ '^[a-z][a-z0-9_]*$')
  OR
  (NOT initial AND source = '')
)

CONSTRAINT chk_<estado>_source
CHECK (source IN ('importacion', 'sistema', 'usuario', ''))

CREATE UNIQUE INDEX unq_<estado>_source
ON <estado> (source) WHERE source <> '';
```

---

## `transicion_estado_<entidad>`

Cuatro entidades llevan su máquina de estados como datos, en una tabla que
enumera los pares admitidos (`RudiTransicion`, construida por
`build_concrete_transicion`).

- **Régimen:** [Mutable rastreada][auditoria]
- **Volumen estimado:** 5-12 filas por dominio
- **Origen:**
  > - [`D-10`][d-10]

### Columnas

|         Campo         |     Tipo      | Nulo | Predeterminado |                  Descripción                  |
| :-------------------: | :-----------: | :--: | :------------: | :-------------------------------------------: |
|   `from_estado_id`    |    `uuid`     |  no  |                |       Llave foránea al estado de origen       |
|    `to_estado_id`     |    `uuid`     |  no  |                |      Llave foránea al estado de destino       |
|        `actor`        | `varchar(20)` |  no  |                | `participante` / `administracion` / `sistema` |
|   `require_motivo`    |   `boolean`   |  no  |    `false`     | Exige `motivo_id` en la fila que transiciona  |
| `require_descripcion` |   `boolean`   |  no  |    `false`     |      Exige texto libre además del motivo      |

### Llaves foráneas

|     Columna      |     Referencia     | `ON DELETE` |
| :--------------: | :----------------: | :---------: |
| `from_estado_id` | `estado_<entidad>` | `RESTRICT`  |
|  `to_estado_id`  | `estado_<entidad>` | `RESTRICT`  |

### Constraints

```postgresql
CONSTRAINT chk_<transicion>_noreflex
CHECK (from_estado_id <> to_estado_id)

CONSTRAINT chk_<transicion>_actor
CHECK (actor IN ('administracion', 'sistema', 'participante'))

CONSTRAINT chk_<transicion>_descripcion_motivo_mutex
CHECK (NOT require_descripcion OR require_motivo)
```

### Unicidad

|          Nombre          |               Definición                |             Propósito              |
| :----------------------: | :-------------------------------------: | :--------------------------------: |
| `unq_<transicion>_combo` | `(actor, from_estado_id, to_estado_id)` | Una transición por par y por actor |

### Notas de diseño

`actor` está en la transición y no en un permiso general porque la misma
transición es legal para un actor e ilegal para otro. Cancelar una inscripción lo
puede hacer la propia persona; anular una participación validada, solo la
administración. La API declara el actor de cada petición con
`set_actor(...)` (`rudi_estados/services/actor.py`), que fija `rudi.actor` para
la transacción, y `trg_<tabla>_transicion_valida` lo lee con `rudi_actor()`.

---

## Catálogo de dominios de estado

Ocho dominios. La columna de atributos semánticos lista los booleanos propios de
cada uno, que se suman a los de la forma base.

|          Modelo          |  Transiciones   |                            Atributos semánticos                            |                         Reglas entre atributos                         |
| :----------------------: | :-------------: | :------------------------------------------------------------------------: | :--------------------------------------------------------------------: |
|     `EstadoRudiUser`     |       no        | `allow_ingreso`, `allow_inscripcion`, `visible_reportes`, `require_motivo` |                 `allow_inscripcion` ⇒ `allow_ingreso`                  |
|  `EstadoConsentimiento`  | no (con origen) |                   `allow_reporte`, `allow_comunicacion`                    |                                                                        |
|    `EstadoActividad`     |       sí        |             `public`, `allow_inscripcion`, `allow_validacion`              |    `allow_inscripcion` ⇒ `public`<br/>`allow_validacion` ⇒ `public`    |
|   `EstadoInscripcion`    | sí (con origen) |                   `consume_cupo`, `allow_participacion`                    | `consume_cupo` ⊥ `terminal`<br/>`allow_participacion` ⇒ `consume_cupo` |
|  `EstadoParticipacion`   |       sí        |               `efectiva`, `allow_puntos`, `allow_constancia`               |    `allow_puntos` ⇒ `efectiva`<br/>`allow_constancia` ⇒ `efectiva`     |
| `EstadoAsignacionMentor` |       no        |                   `vigente`, `public`, `require_motivo`                    |                          `vigente` ⇒ `public`                          |
|    `EstadoConstancia`    |       no        |                         `valid`, `require_motivo`                          |                          `valid` ⊥ `terminal`                          |
|    `EstadoPropuesta`     |       sí        |                       `vigente`, `allow_portafolio`                        |                     `vigente` ⇒ `allow_portafolio`                     |

Cada regla entre atributos es un `CHECK` del catálogo (`⇒` implica, `⊥`
excluye): un estado que cuenta para el portafolio sin estar vigente, o que
consume cupo siendo terminal, no puede ni declararse.

Los dominios sin tabla de transiciones cambian por caminos demasiado simples
para justificar una tabla de pares; su exigencia de motivo se declara en el
estado destino (`require_motivo`).

### Estados sembrados

Los códigos que usan los servicios. Son semillas estructurales
(`rudi_estados/seeders.py`): se crean al migrar si no existen, y la DIEM puede
editar sus etiquetas y atributos o añadir otros. Las transiciones se siembran
igual, por actor.

|          Dominio           |                                                                      Estados                                                                       |
| :------------------------: | :------------------------------------------------------------------------------------------------------------------------------------------------: |
|     `estado_rudiuser`      |                 `pendiente_verificacion` (inicial), `verificada`, `activa`, `suspendida` (exige motivo), `anonimizada` (terminal)                  |
|  `estado_consentimiento`   | `otorgado` (inicial de `usuario`), `pendiente_verificar` (inicial de `sistema`), `no_autorizado` (inicial de `importacion`), `retirado` (terminal) |
|     `estado_actividad`     |                                `borrador` (inicial), `publicada`, `en_curso`, `finalizada`, `cancelada` (terminal)                                 |
|    `estado_inscripcion`    |            `pendiente` (inicial de `usuario`), `confirmada` (inicial de `sistema`), `en_espera`, `cancelada` y `rechazada` (terminales)            |
|   `estado_participacion`   |                   `registrada` (inicial), `en_curso`, `finalizada` y `no_completo` (efectivas), `retirada`, `anulada` (terminal)                   |
| `estado_asignacion_mentor` |               `propuesta` (inicial), `confirmada`, `declinada`, `finalizada`, `cancelada`, `vencida` (las cuatro últimas terminales)               |
|    `estado_constancia`     |                                             `emitida` (inicial), `anulada`, `reemplazada` (terminales)                                             |
|     `estado_propuesta`     |                `activa` (inicial), `en_pausa`, `finalizada`, `implementada`, `integrada`, `cerrada` (las cuatro últimas terminales)                |

`verificada` y `activa` admiten el ingreso; solo `activa` admite inscribirse, y
por eso exige al menos un perfil (`trg_rudiuser_profile`). Confirmar el correo
lleva a la persona a `verificada`; declarar su primer perfil la lleva a `activa`.

La lista de espera promueve a `pendiente`, no a `confirmada`: la persona recibe
el aviso y la DIEM confirma, por la transición de `sistema` `en_espera` ⇒
`pendiente`.

`estado_rudiuser.anonimizada` es terminal, y entrar en ella fija
`rudi_user.anonimizado_at` (`trg_rudiuser_estado`).

### Los tres atributos que evitan la mayor parte de los `CASE`

|      Atributo      |                                                             Qué resuelve                                                              |
| :----------------: | :-----------------------------------------------------------------------------------------------------------------------------------: |
|   `consume_cupo`   |         El contador de inscritos suma solo los estados que lo declaran, de modo que cancelar libera cupo sin lógica adicional         |
|     `efectiva`     | El conteo de participantes reales de [`RN-13`][rn-13] filtra por este booleano y no por una lista de códigos escrita en cada consulta |
| `allow_constancia` |                         [`RN-15`][rn-15] se comprueba leyendo el catálogo, no comparando contra `finalizada`                          |

El valor de esto se ve al añadir un estado. Cuando la DIEM decida distinguir
_finalizada con excelencia_ de _finalizada_, es una fila con `efectiva` y
`allow_constancia` en verdadero. Sin los atributos, sería buscar en todo el
código dónde dice `= 'finalizada'`.

### Estados que el modelo se negó a crear

|          Estado descartado           |                                                  Por qué no existe                                                   |
| :----------------------------------: | :------------------------------------------------------------------------------------------------------------------: |
|       `inscripcion.no_asistio`       | La no asistencia es un desenlace de participación, no de inscripción; ponerlo aquí obligaría a validar en dos tablas |
|  `actividad.inscripciones_abiertas`  |                   Es una consecuencia de las fechas de la ventana, no un estado que alguien decida                   |
| `participacion.pendiente_validacion` |   Es la ausencia de `validada_at`, no un estado; tenerlo permitiría la contradicción de estar pendiente y validada   |

---

## Triggers de la entidad gobernada

No viven en el catálogo sino en cada tabla que lo referencia, y son los que
convierten los atributos semánticos en garantías. Los instancia
`estado_lifecycle_triggers(...)` (`rudi_estados/triggers.py`); el detalle está
en [`Triggers`][triggers-estado].

|             Nombre              |            Evento             | Momento  | Nivel |                                          Regla                                          |     Origen     |
| :-----------------------------: | :---------------------------: | :------: | :---: | :-------------------------------------------------------------------------------------: | :------------: |
|   `trg_<tabla>_estado_activo`   |     `INSERT`<br/>`UPDATE`     | `BEFORE` | `ROW` | Un estado se asigna solo si está `is_active`; las filas que ya lo tienen no se bloquean | [`D-18`][d-18] |
|  `trg_<tabla>_estado_terminal`  | `UPDATE` con cambio de estado | `BEFORE` | `ROW` |              Una fila cuyo estado actual es `terminal` no cambia de estado              | [`D-08`][d-08] |
| `trg_<tabla>_transicion_valida` | `UPDATE` con cambio de estado | `BEFORE` | `ROW` |         El par debe existir activo para el actor de `rudi_actor()`, si hay uno          | [`D-10`][d-10] |

[auditoria]: ../convenciones.md#auditoria-por-tabla
[catalogos]: catalogos.md
[convenciones-columnas]: ../convenciones.md#columnas-estandar
[taxonomias]: taxonomias.md
[triggers-estado]: ../triggers.md#ciclo-de-vida-del-estado
[d-08]: ../decisiones.md#d-08
[d-09]: ../decisiones.md#d-09
[d-10]: ../decisiones.md#d-10
[d-18]: ../decisiones.md#d-18
[rf-a-17]: ../../requerimientos/funcionales/administracion.md#rf-a-17
[rf-a-26]: ../../requerimientos/funcionales/administracion.md#rf-a-26
[rf-a-29]: ../../requerimientos/funcionales/administracion.md#rf-a-29
[rf-a-36]: ../../requerimientos/funcionales/administracion.md#rf-a-36
[rf-a-41]: ../../requerimientos/funcionales/administracion.md#rf-a-41
[rf-a-48]: ../../requerimientos/funcionales/administracion.md#rf-a-48
[rn-05]: ../../requerimientos/reglas-negocio.md#rn-05
[rn-13]: ../../requerimientos/reglas-negocio.md#rn-13
[rn-15]: ../../requerimientos/reglas-negocio.md#rn-15
