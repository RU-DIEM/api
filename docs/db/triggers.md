---
icon: lucide/shield-check
---

# Triggers `PL/pgSQL`

Las reglas que un `CHECK` no alcanza. Esta página define el contrato común que
todo trigger del modelo respeta, las **siete familias** de las que se derivan
casi todos, y el catálogo completo con el estado de implementación de cada uno.

## Requerimientos cubiertos

- [`RF-A-17`][rf-a-17]
- [`RF-A-18`][rf-a-18]
- [`RF-A-26`][rf-a-26]
- [`RF-A-29`][rf-a-29]
- [`RF-A-31`][rf-a-31]
- [`RF-A-33`][rf-a-33]
- [`RF-A-35`][rf-a-35]
- [`RF-A-48`][rf-a-48]
- [`RF-P-16`][rf-p-16]
- [`RF-P-18`][rf-p-18]

---

## Por qué tantas reglas viven aquí

El [criterio de invariantes][convenciones-criterios] ordena los mecanismos de
más barato a más evadible y manda usar el primero que sirva. `CHECK`, índice
único, `EXCLUDE` y llave foránea ya cubren todo lo que depende de una sola
fila. Lo que queda depende de **otra tabla**, de **otras filas de la misma
tabla**, de un **parámetro configurable** o de **la fecha de hoy**, y ninguno de
esos cuatro casos es expresable de forma declarativa en PostgreSQL.

La alternativa sería dejarlas en la capa de aplicación. El modelo no lo hace
por [`D-08`][d-08]: una regla que vive en un servicio se evade desde `psql`,
desde una migración de datos, desde un comando de gestión y desde el segundo
cliente que alguien escriba. Una que vive en el trigger, no.

!!! abstract "Tres consecuencias de esa elección"

    === "**La derivación también es trigger**"

        Una columna denormalizada que el servicio "se compromete" a copiar
        bien no es una garantía. El trigger la **sobrescribe** en el
        `BEFORE INSERT` con el valor de su origen, ignorando lo que haya
        mandado el llamador, y el trigger de solo lectura la congela después.
        Es lo que hace cierto a [`D-14`][d-14] y a [`D-16`][d-16].

    === "**El parámetro se lee, no se compila**"

        Un valor configurable no puede ser un `CHECK`: cambiarlo exigiría una
        migración, justo lo que [`RF-A-48`][rf-a-48] prohíbe. El trigger lee
        `rudi_parametro(...)` en cada escritura, sobre una tabla de una docena
        de filas que vive entera en caché.

    === "**El error tiene que nombrar la columna**"

        Todo trigger levanta `RAISE check_violation USING COLUMN = '<col>'`,
        que es la misma condición que dispara un `CHECK`. Django la clasifica
        como `IntegrityError` y la capa de errores del template construye una
        respuesta que apunta al campo culpable.

---

## Contrato común

|            Regla             |                                                                                           Detalle                                                                                           |
| :--------------------------: | :-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| Nombre `trg_<tabla>_<regla>` |                                     Con las excepciones que fija [Nomenclatura][convenciones-nomenclatura]: los de la clase base y los de solo lectura                                      |
|      Cuerpo normalizado      |                                                 Se declara con `normalize_trigger`, que colapsa el texto a una sola línea antes de emitirlo                                                 |
|      Error con columna       |                                                         `RAISE check_violation USING COLUMN = ...`, nunca `RAISE EXCEPTION` a secas                                                         |
|   Existencia antes de leer   |                                    Un `BEFORE` corre antes de que se verifique la llave foránea diferida; ver [abajo](#dereferenciar-una-llave-foranea)                                     |
|  Idempotente bajo reintento  |                                                Un `AFTER` que escribe en otra tabla usa `ON CONFLICT DO NOTHING` o compara antes de escribir                                                |
|    Declarado en su módulo    | Un trigger sobre una tabla de otra app se registra con `pgtrigger.register(...)(Modelo)` desde la app que conoce la regla, para que el grafo de dependencias siga siendo de un solo sentido |

### Dereferenciar una llave foránea

Las llaves foráneas del modelo son `DEFERRABLE INITIALLY DEFERRED`, así que un
trigger `BEFORE` que lee la fila referenciada **no puede asumir que existe**:

```postgresql
SELECT ... INTO origen FROM <tabla_referenciada> WHERE id = NEW.<columna>_id;

IF NOT FOUND THEN
    RAISE foreign_key_violation USING COLUMN = '<columna>_id';
END IF;
```

### Funciones auxiliares

Viven en `rudi_core/migrations/0001_rudi_functions.py`, no en un modelo, porque
son infraestructura de esquema y no dominio.

|         Función          |                               Devuelve                               |                 Uso                  |
| :----------------------: | :------------------------------------------------------------------: | :----------------------------------: |
| `rudi_parametro(codigo)` |  `parametro.valor` como `jsonb`; `NULL` si falta o está desactivado  |       Toda regla parametrizada       |
|      `rudi_actor()`      | El actor de la transacción (`rudi.actor`), o `NULL` si nadie lo fijó |       Validación de transición       |
|       `rudi_hoy()`       |            `(now() AT TIME ZONE 'America/Managua')::date`            | Fecha de negocio, por [`D-02`][d-02] |

`rudi_parametro` devuelve `NULL` en lugar de lanzar porque los parámetros de
rudi son opcionales por diseño: `registro.dominio_institucional` vacío o ausente
significa _no exigir dominio_. Cada trigger decide qué significa un parámetro
ausente.

`rudi_actor()` es el único punto donde el trigger depende de que la API coopere:
el servicio llama a `set_actor('participante' | 'administracion' | 'sistema')`
dentro de la transacción. Si nadie lo fija, la validación de transición sigue
exigiendo que el par exista, pero **no** que exista para un actor concreto. Esa
degradación es deliberada: una migración de datos o una corrección desde `psql`
no tienen actor y no deben quedar bloqueadas; lo que no pueden es inventar una
transición que el catálogo no declara.

---

## Las siete familias

### Ciclo de vida del estado

Triggers genéricos por cada tabla con `estado_id`, instanciados por
`estado_lifecycle_triggers(entidad=..., model=..., transicion_model=...)`
(`rudi_estados/triggers.py`). La semántica se lee de las columnas del catálogo,
nunca se compara contra `codigo`.

|             Trigger             |                                      Impone                                      |                         Alcance                          |
| :-----------------------------: | :------------------------------------------------------------------------------: | :------------------------------------------------------: |
|   `trg_<tabla>_estado_activo`   |                    El estado asignado debe estar `is_active`                     |                 Las 8 tablas gobernadas                  |
|  `trg_<tabla>_estado_terminal`  |           Una fila en estado `terminal` no vuelve a cambiar de estado            |                 Las 8 tablas gobernadas                  |
| `trg_<tabla>_transicion_valida` | El par `(from, to)` existe activo en `transicion_estado_<entidad>` para el actor | `actividad`, `inscripcion`, `participacion`, `propuesta` |
| `trg_<tabla>_estado_coherente`  |     Los atributos semánticos del estado concuerdan con las marcas de la fila     |              Por tabla, con su propia regla              |

Los tres primeros son la misma plantilla instanciada con el nombre del
catálogo. El cuarto es específico: es donde cada tabla declara qué significa
para ella estar en un estado (una participación en un estado `efectiva` tiene
`validada_at`; una asignación en un estado `require_motivo` tiene `motivo_id`).

### Motivo de lista cerrada

`motivo` es una sola tabla discriminada por `ambito`, y sin esta familia **nada
impide que una cancelación de inscripción apunte a un motivo de anulación de
constancia**. La instancia `motivo_ambito_trigger(...)`:

```postgresql
-- trg_<tabla>_motivo, BEFORE INSERT OR UPDATE, ROW

IF NEW.motivo_id IS NOT NULL THEN
    SELECT ambito, require_descripcion, is_active INTO motivo
    FROM rudicatalogos_motivo WHERE id = NEW.motivo_id;

    IF NOT FOUND THEN
        RAISE foreign_key_violation USING COLUMN = 'motivo_id';
    END IF;
    IF NOT motivo.is_active THEN
        RAISE check_violation USING COLUMN = 'motivo_id', MESSAGE = 'El motivo está desactivado.';
    END IF;
    IF motivo.ambito <> '<ambito>' THEN
        RAISE check_violation USING COLUMN = 'motivo_id', MESSAGE = 'El motivo no pertenece al ámbito de esta acción.';
    END IF;
    IF motivo.require_descripcion AND length(NEW.<descripcion>) = 0 THEN
        RAISE check_violation USING COLUMN = '<descripcion>', MESSAGE = 'Este motivo exige una descripción.';
    END IF;
END IF;
```

|        Tabla        |         `ambito`          | Columna de descripción |
| :-----------------: | :-----------------------: | :--------------------: |
|     `actividad`     |  `cancelacion_actividad`  |  `motivo_descripcion`  |
|    `inscripcion`    | `cancelacion_inscripcion` |  `motivo_descripcion`  |
|   `participacion`   | `anulacion_participacion` |  `motivo_descripcion`  |
| `asignacion_mentor` |    `rechazo_mentoria`     |  `motivo_descripcion`  |
|    `constancia`     |  `anulacion_constancia`   |  `motivo_descripcion`  |
| `movimiento_punto`  |      `ajuste_puntos`      |     `descripcion`      |
|     `propuesta`     |    `cierre_propuesta`     |  `motivo_descripcion`  |

### Catálogo activo

[`D-18`][d-18] dice que los catálogos se desactivan y se referencian con
`RESTRICT`. La llave foránea impide borrar la fila referenciada, pero **nada
impide que una fila nueva estrene una referencia a un catálogo ya desactivado**.

`trg_<tabla>_catalogo_activo` corre `BEFORE INSERT` (no en `UPDATE`: una fila
histórica conserva su clasificación) y exige `is_active` en cada referencia a
catálogo de la tabla. Lo instancia `catalogo_activo_trigger(...)` sobre
`programa`, `actividad`, `participacion`, `reconocimiento` y
`regla_puntuacion`. Las taxonomías no lo necesitan: son enumeraciones
([`D-21`][d-21]) y su `CHECK` ya rechaza el valor retirado.

### Derivación de snapshot

La familia que hace cierto a [`D-14`][d-14] y a [`D-16`][d-16].
`trg_readonly_snapshot` congela una columna copiada **después** de la
inserción, pero no valida qué se escribió en ella: la copia quedaría inmutable,
pero falsa. `trg_<tabla>_snapshot` la **sobrescribe** en el `BEFORE INSERT`
desde su origen.

|       Tabla        |            Columnas             |                                  Origen                                   |
| :----------------: | :-----------------------------: | :-----------------------------------------------------------------------: |
|  `participacion`   |             `anio`              |                             `actividad.anio`                              |
| `movimiento_punto` |        `user_id`, `anio`        |                     `participacion` (cuando la cita)                      |
|    `constancia`    | `user_id` (congelado del resto) | Escrito por el servicio de emisión, congelado por `trg_readonly_snapshot` |

El texto de la constancia sale de sustituir la plantilla, que es trabajo del
servicio de emisión y no del motor; lo que sí garantiza el motor es que, una vez
emitida, no cambie.

### Contadores denormalizados

`actividad.inscritos_activos` es el único contador del modelo, y
`chk_actividad_cupo_coherente` (`inscritos_activos <= cupo`) es su red de
seguridad. `trg_inscripcion_contador`, `AFTER INSERT OR UPDATE`, suma cuando el
estado nuevo tiene `consume_cupo` y el viejo no, resta en el caso contrario, y no
hace nada si ninguno cambió. Al ejecutarse en la misma transacción que crea la
inscripción, el `CHECK` se evalúa con el valor ya incrementado y el sobrecupo
falla como error de transacción: dos personas sobre el último lugar no pueden
ganar ambas.

### Coherencia entre filas y tablas

Reglas por tabla que leen otra fila. Cada una tiene su ficha en el módulo de su
tabla; la lista completa está en el [catálogo](#catalogo).

### Efecto en otra tabla

`AFTER` que escriben en otra tabla como consecuencia de la escritura que los
dispara: otorgar puntos al validar, revertirlos al anular, invalidar las
constancias de una participación anulada, cerrar las inscripciones de una
actividad cancelada, promover la lista de espera. Viven en la app de la tabla
que **escriben**, registrados sobre la tabla que los dispara, de modo que
`participacion` no conoce a `puntos` ni a `constancias`. Todos son idempotentes:
la segunda ejecución no encuentra nada que hacer.

---

## Catálogo

Estado de cada trigger del modelo. **Vigente** es lo que ya está en
`src/rudi_*/`; **Pendiente** es diseño sin implementar. Los de la clase base y
los `trg_readonly_*` no se repiten aquí: están en
[Columnas estándar][convenciones-columnas] y en la ficha de cada tabla.

### Ciclo de vida, motivo y catálogo activo

|                     Trigger                     |                                           Tablas                                           |  Estado   |
| :---------------------------------------------: | :----------------------------------------------------------------------------------------: | :-------: |
|           `trg_<tabla>_estado_activo`           |                             `rudiuser`, `consentimientodatos`                              |  Vigente  |
|          `trg_<tabla>_estado_terminal`          |                             `rudiuser`, `consentimientodatos`                              |  Vigente  |
| `trg_<tabla>_estado_activo`, `_estado_terminal` | `actividad`, `inscripcion`, `participacion`, `asignacionmentor`, `constancia`, `propuesta` | Pendiente |
|         `trg_<tabla>_transicion_valida`         |                  `actividad`, `inscripcion`, `participacion`, `propuesta`                  | Pendiente |
|         `trg_<tabla>_estado_coherente`          | `actividad`, `inscripcion`, `participacion`, `asignacionmentor`, `constancia`, `propuesta` | Pendiente |
|              `trg_<tabla>_motivo`               |                                    7 tablas, ver arriba                                    | Pendiente |
|          `trg_<tabla>_catalogo_activo`          |       `programa`, `actividad`, `participacion`, `reconocimiento`, `reglapuntuacion`        | Pendiente |

### Persona y perfiles

|                   Trigger                    | Estado  |
| :------------------------------------------: | :-----: |
|         `trg_rudiuser_anonimizacion`         | Vigente |
|            `trg_rudiuser_estado`             | Vigente |
|        `trg_rudiuser_fechanacimiento`        | Vigente |
|          `trg_rudiuser_sync_active`          | Vigente |
|            `trg_rudiuser_profile`            | Vigente |
|        `trg_identificadoruser_regex`         | Vigente |
|      `trg_identificadoruser_first_main`      | Vigente |
|     `trg_identificadoruser_protect_main`     | Vigente |
|       `trg_estudianteprofile_dominio`        | Vigente |
|       `trg_estudianteprofile_carrera`        | Vigente |
|       `trg_apiuser_email_domain_check`       | Vigente |
|        `trg_estudiantecarrera_nivel`         | Vigente |
|       `trg_estudiantecarrera_carrera`        | Vigente |
|        `trg_mentorcertificacion_year`        | Vigente |
|          `trg_parametro_valor_tipo`          | Vigente |
| `trg_plantillamensaje_variables_*_integrity` | Vigente |
|      `trg_normalize_tipoidentificador`       | Vigente |
| `trg_tipoidentificador_test_posix_validity`  | Vigente |

### Actividades, participación, puntos, constancias, portafolio y analítica

|                      Trigger                       |       Familia        |  Estado   |
| :------------------------------------------------: | :------------------: | :-------: |
|        `trg_actividad_publicacion_completa`        |      Coherencia      | Pendiente |
|       `trg_actividad_cancelar_inscripciones`       | Efecto en otra tabla | Pendiente |
|          `trg_actividad_promover_espera`           | Efecto en otra tabla | Pendiente |
|      `trg_asignacionmentor_mentor_confirmado`      |      Coherencia      | Pendiente |
|      `trg_asignacionmentor_equipo_coherente`       |      Coherencia      | Pendiente |
|         `trg_inscripcion_ventana_abierta`          |      Coherencia      | Pendiente |
|         `trg_inscripcion_cierre_bloqueado`         |      Coherencia      | Pendiente |
|             `trg_inscripcion_contador`             |       Contador       | Pendiente |
|         `trg_inscripcion_promover_espera`          | Efecto en otra tabla | Pendiente |
|            `trg_participacion_snapshot`            |       Snapshot       | Pendiente |
|      `trg_participacion_actividad_coherente`       |      Coherencia      | Pendiente |
|      `trg_participacion_actividad_validable`       |      Coherencia      | Pendiente |
|         `trg_participacion_otorgar_puntos`         | Efecto en otra tabla | Pendiente |
|        `trg_participacion_revertir_puntos`         | Efecto en otra tabla | Pendiente |
|     `trg_participacion_invalidar_constancias`      | Efecto en otra tabla | Pendiente |
|           `trg_equipo_actividad_admite`            |      Coherencia      | Pendiente |
|      `trg_equipomiembro_un_equipo_actividad`       |      Coherencia      | Pendiente |
|           `trg_equipomiembro_tamano_max`           |      Coherencia      | Pendiente |
|           `trg_equipomiembro_congelado`            |      Coherencia      | Pendiente |
|           `trg_movimientopunto_snapshot`           |       Snapshot       | Pendiente |
|        `trg_movimientopunto_reverso_exacto`        |      Coherencia      | Pendiente |
|       `trg_movimientopunto_marcar_revertido`       | Efecto en otra tabla | Pendiente |
|      `trg_plantillaconstancia_version_nueva`       |      Coherencia      | Pendiente |
|           `trg_constancia_folio_asignar`           |      Derivación      | Pendiente |
|         `trg_constancia_reemplazo_anulado`         |      Coherencia      | Pendiente |
| `trg_constanciaparticipacion_participacion_valida` |      Coherencia      | Pendiente |
|           `trg_propuesta_codigo_asignar`           |      Derivación      | Pendiente |
|         `trg_propuesta_clasificada_marca`          |      Derivación      | Pendiente |
|          `trg_propuesta_actividad_origen`          | Efecto en otra tabla | Pendiente |
|        `trg_indicadorperiodo_anio_cerrado`         |      Coherencia      | Pendiente |

### Triggers del diseño original que no existen

|                                                Trigger                                                |                                      Por qué no                                      |
| :---------------------------------------------------------------------------------------------------: | :----------------------------------------------------------------------------------: |
|                                        `trg_<tabla>_no_borrar`                                        |      La clase base ya lo hace (`trg_protect_delete`, `trg_softdelete_isactive`)      |
|                            `trg_<tabla>_inmutable` en tablas `append-only`                            |                      `trg_append_only` de `ApiAppendOnlyModel`                       |
|                          `trg_participacion_evento`, `trg_propuesta_evento`                           |                   pghistory registra cada cambio ([`D-15`][d-15])                    |
|                                   `trg_parametrosistema_historial`                                    |                                Ídem: `ParametroEvent`                                |
| `trg_constancia_congelado_readonly`, `trg_propuesta_codigo_readonly`, `trg_movimientopunto_inmutable` | `ReadOnly` de pgtrigger (`trg_readonly_snapshot`, `trg_readonly_codigo_anioingreso`) |
|                                    `trg_usuario_revocar_sesiones`                                     |               El template invalida los JWT; las sesiones no son tabla                |

---

## Lo que no es trigger

!!! abstract "No todo invariante de negocio cabe en la base:"

    === "**Efecto externo a la transacción**"

        El correo no puede participar de un `COMMIT`. Un trigger que lo
        enviara convertiría un fallo del proveedor en un fallo de la
        escritura. La notificación se encola en la transacción y se envía
        después ([`Notificaciones`][notificaciones]).

    === "**Sin evento de escritura que lo dispare**"

        Cerrar una ventana de inscripción o vencer una propuesta de mentoría
        ocurren porque pasó el tiempo, no porque alguien escribió. Son los
        [procesos programados][procesos], y su contrato es que cada uno hace
        la escritura que **sí** dispara los triggers de esta página.

    === "**Autorización por rol**"

        Qué rol puede provocar qué tránsito es una decisión de permisos, no
        de integridad. La base valida que el par exista en el catálogo y, si
        la petición declaró su actor, que exista para ese actor; quién es esa
        petición lo resuelve la capa de API.

[convenciones-columnas]: convenciones.md#columnas-estandar
[convenciones-criterios]: convenciones.md#criterios-de-invariantes
[convenciones-nomenclatura]: convenciones.md#nomenclatura
[notificaciones]: modulos/notificaciones.md
[procesos]: procesos.md
[d-02]: decisiones.md#d-02
[d-08]: decisiones.md#d-08
[d-14]: decisiones.md#d-14
[d-15]: decisiones.md#d-15
[d-16]: decisiones.md#d-16
[d-18]: decisiones.md#d-18
[d-21]: decisiones.md#d-21
[rf-a-17]: ../requerimientos/funcionales/administracion.md#rf-a-17
[rf-a-18]: ../requerimientos/funcionales/administracion.md#rf-a-18
[rf-a-26]: ../requerimientos/funcionales/administracion.md#rf-a-26
[rf-a-29]: ../requerimientos/funcionales/administracion.md#rf-a-29
[rf-a-31]: ../requerimientos/funcionales/administracion.md#rf-a-31
[rf-a-33]: ../requerimientos/funcionales/administracion.md#rf-a-33
[rf-a-35]: ../requerimientos/funcionales/administracion.md#rf-a-35
[rf-a-48]: ../requerimientos/funcionales/administracion.md#rf-a-48
[rf-p-16]: ../requerimientos/funcionales/participantes.md#rf-p-16
[rf-p-18]: ../requerimientos/funcionales/participantes.md#rf-p-18
