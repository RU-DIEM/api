---
icon: lucide/sliders-horizontal
---

# Catálogos y parámetros

Datos que la DIEM gobierna sin desplegar código: las listas administrables de
las matrices, los parámetros del motor, los motivos y las plantillas de mensaje.
Viven en la app `rudi_catalogos`.

Las tablas de estado siguen el mismo principio pero tienen su propia página:
[`Estados`][estados]. Las listas cerradas que no administra la DIEM (género,
etnia, talla, niveles y las taxonomías del portafolio) no son tablas sino
enumeraciones: [`Taxonomías`][taxonomias].

## Requerimientos cubiertos

- [`RF-A-12`][rf-a-12]
- [`RF-A-13`][rf-a-13]
- [`RF-A-14`][rf-a-14]
- [`RF-A-29`][rf-a-29]
- [`RF-A-48`][rf-a-48]
- [`RF-P-04`][rf-p-04]
- [`RF-P-06`][rf-p-06]

---

## Forma común

Todo catálogo de esta app hereda de `RudiCatalogo`, que a su vez hereda de
`ApiSoftDeleteModel`.

- **Régimen:** [Mutable rastreada][auditoria]
- **Origen:**
  > - [`RF-A-14`][rf-a-14]
  > - [`D-18`][d-18]

### Columnas

|     Campo     |      Tipo      | Nulo | Predeterminado |          Descripción           |
| :-----------: | :------------: | :--: | :------------: | :----------------------------: |
|   `codigo`    | `varchar(50)`  |  no  |                |     Identificador estable      |
|  `etiqueta`   | `varchar(100)` |  no  |      `''`      |  Texto visible en formularios  |
| `descripcion` |     `text`     |  no  |      `''`      |   Ayuda contextual del campo   |
|  `is_active`  |   `boolean`    |  no  |     `true`     | Puede elegirse en filas nuevas |

### Constraints

```postgresql
CONSTRAINT chk_<catalogo>_codigo_format
CHECK (codigo ~ '^[a-z][a-z0-9_]*$')

CONSTRAINT chk_<catalogo>_descripcion
CHECK (length(descripcion) <= 300)
```

### Unicidad

|         Nombre          | Definición |
| :---------------------: | :--------: |
| `unq_<catalogo>_codigo` | `(codigo)` |

### Triggers

Además de los de la [clase base][convenciones-columnas] y de
`trg_softdelete_isactive`:

|        Nombre         |       Evento       | Momento  | Nivel |                Regla                 |     Origen     |
| :-------------------: | :----------------: | :------: | :---: | :----------------------------------: | :------------: |
| `trg_readonly_codigo` | `UPDATE OF codigo` | `BEFORE` | `ROW` | Rechaza cualquier cambio de `codigo` | [`D-08`][d-08] |

Cada tabla lleva su tabla de eventos (`<Modelo>Event`), que es el historial de
cambios que pide [`RF-A-48`][rf-a-48]: quién cambió qué valor, cuándo y desde
qué petición.

---

## `parametro`

Los valores que gobiernan el comportamiento del sistema. Es la tabla que hace
posible una [sola pantalla de configuración][rf-a-48] con cambio sin despliegue,
historial y reversión.

- **Régimen:** [Mutable rastreada][auditoria]
- **Volumen estimado:** ~12 filas

### Columnas

Hereda `codigo` y `descripcion` de la forma común; no lleva `etiqueta`.

|      Campo      |     Tipo      | Nulo | Predeterminado |                       Descripción                        |
| :-------------: | :-----------: | :--: | :------------: | :------------------------------------------------------: |
|    `codigo`     | `varchar(50)` |  no  |                | Con espacio de nombres: `registro.dominio_institucional` |
|     `grupo`     | `varchar(20)` |  no  |                |                       Ver `CHECK`                        |
|     `tipo`      | `varchar(10)` |  no  |                |  `binario` / `entero` / `lista` / `texto` / `duracion`   |
|     `valor`     |    `jsonb`    |  no  |                |                      Valor vigente                       |
| `restricciones` |    `jsonb`    |  no  |      `{}`      |            Mínimo, máximo y valores admitidos            |
| `updated_by_id` |    `uuid`     |  sí  |                |    Llave foránea `RESTRICT` a la cuenta que lo cambió    |

### Constraints

```postgresql
CONSTRAINT chk_parametro_codigo_format
CHECK (codigo ~ '^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$')

CONSTRAINT chk_parametro_grupo
CHECK (grupo IN ('registro', 'sesion', 'inscripcion', 'vigencia', 'importacion'))

CONSTRAINT chk_parametro_tipo
CHECK (tipo IN ('binario', 'entero', 'lista', 'texto', 'duracion'))

CONSTRAINT chk_parametro_restricciones
CHECK (jsonb_typeof(restricciones) = 'object')
```

### Triggers

|           Nombre           |        Evento         | Momento  | Nivel |                                 Regla                                  |        Origen        |
| :------------------------: | :-------------------: | :------: | :---: | :--------------------------------------------------------------------: | :------------------: |
| `trg_parametro_valor_tipo` | `INSERT`<br/>`UPDATE` | `BEFORE` | `ROW` | `valor` debe tener la forma de `tipo`; una duración es ISO 8601 válida | [`RF-A-48`][rf-a-48] |

### Parámetros sembrados

|              Código              |   Grupo    | Valor inicial |                           Efecto                            |
| :------------------------------: | :--------: | :-----------: | :---------------------------------------------------------: |
| `registro.dominio_institucional` | `registro` | `uamv.edu.ni` | Dominio exigido al estudiante UAM, por [`RF-P-03`][rf-p-03] |
|     `vigencia.verificacion`      | `vigencia` |    `PT24H`    |        Vigencia del enlace de confirmación de correo        |
|     `vigencia.recuperacion`      | `vigencia` |    `PT2H`     |      Vigencia del enlace de recuperación de contraseña      |
|      `vigencia.invitacion`       | `vigencia` |     `P7D`     |      Vigencia del enlace de invitación administrativa       |

Los triggers leen un parámetro con `rudi_parametro('<codigo>')`, que devuelve el
`valor` como `jsonb` o `NULL` si el parámetro no existe o está desactivado; cada
trigger decide qué significa un parámetro ausente
(ver [`Triggers`][triggers-funciones]).

### Notas de diseño

`valor` es `jsonb` y no una columna por tipo porque los parámetros tienen cinco
tipos distintos y una tabla con una columna nulable por tipo sería peor. El tipo
declarado y las restricciones permiten que la interfaz construya el control
adecuado —número, interruptor, texto— sin conocer cada código, y
`trg_parametro_valor_tipo` garantiza que el valor tenga la forma que el tipo
promete.

El historial es la tabla de eventos de pghistory, no una tabla propia de
versiones ([`D-15`][d-15]).

---

## `motivo`

Catálogo único de motivos para todo el sistema, discriminado por ámbito.
Cancelaciones, rechazos y anulaciones citan aquí en lugar de guardar texto libre.

- **Régimen:** [Mutable rastreada][auditoria]
- **Volumen estimado:** 25-40 filas
- **Origen:**
  > - [`RF-A-29`][rf-a-29]
  > - [`RF-P-19`][rf-p-19]

### Columnas

No lleva `descripcion`.

|         Campo         |     Tipo      | Nulo |   Predeterminado   |                 Descripción                  |
| :-------------------: | :-----------: | :--: | :----------------: | :------------------------------------------: |
|       `ambito`        | `varchar(30)` |  no  |                    |                 Ver `CHECK`                  |
|     `visibilidad`     | `varchar(20)` |  no  | `'administracion'` | `participante` / `administracion` / `global` |
| `require_descripcion` |   `boolean`   |  no  |      `false`       |  Obliga a escribir texto además de elegirlo  |

### Constraints

```postgresql
CONSTRAINT chk_motivo_ambito
CHECK (
  ambito IN (
    'ajuste_puntos',
    'anulacion_constancia',
    'anulacion_participacion',
    'cancelacion_actividad',
    'cancelacion_inscripcion',
    'cierre_propuesta',
    'rechazo_mentoria',
    'rechazo_importacion',
    'revocar_consentimiento'
  )
)

CONSTRAINT chk_motivo_visibilidad
CHECK (visibilidad IN ('administracion', 'global', 'participante'))
```

### Unicidad

|       Nombre        |     Definición     |
| :-----------------: | :----------------: |
| `unq_motivo_ambito` | `(ambito, codigo)` |

`unq_motivo_ambito` reemplaza al `unq_motivo_codigo` de la forma común: dos
ámbitos pueden usar el mismo código (`duplicado`).

### Triggers

|        Nombre         |       Evento       | Momento  | Nivel |                Regla                 |     Origen     |
| :-------------------: | :----------------: | :------: | :---: | :----------------------------------: | :------------: |
| `trg_readonly_ambito` | `UPDATE OF ambito` | `BEFORE` | `ROW` | Rechaza cualquier cambio de `ambito` | [`D-08`][d-08] |

### Notas de diseño

Un catálogo único con discriminador, en lugar de una tabla de motivos por
acción, porque la forma es idéntica y la única diferencia es dónde aparece cada
fila. `ambito` es discriminador y no estado: no cambia nunca para una fila dada.

Que la tabla que cita un motivo apunte a uno de **su** ámbito lo garantiza la
familia [motivo de lista cerrada][triggers-motivo] en la tabla que lo
referencia, junto con `require_descripcion`.

`visibilidad` existe porque los motivos de cancelación que ve el estudiante
—_conflicto de horario_, _ya no me interesa_— no son los mismos que registra la
administración —_no cumple requisitos_, _duplicado_—, y mezclarlos en un solo
selector produciría datos inservibles para los reportes.

---

## `plantilla_mensaje`

Textos de los correos que envía el sistema, editables sin desplegar.

- **Régimen:** [Mutable rastreada][auditoria]
- **Volumen estimado:** ~10 filas
- **Origen:**
  > - [`RF-P-04`][rf-p-04]
  > - [`RF-A-35`][rf-a-35]

### Columnas

No lleva `descripcion`.

|    Campo    |      Tipo       | Nulo | Predeterminado |              Descripción               |
| :---------: | :-------------: | :--: | :------------: | :------------------------------------: |
|  `asunto`   | `varchar(200)`  |  no  |                |          Admite sustituciones          |
|  `cuerpo`   |     `text`      |  no  |                |    Cuerpo con marcadores `{campo}`     |
| `variables` | `varchar(50)[]` |  no  |      `{}`      | Marcadores admitidos en esta plantilla |

### Constraints

```postgresql
CONSTRAINT chk_plantillamensaje_cuerpo
CHECK (length(cuerpo) BETWEEN 1 AND 8000)
```

### Triggers

|                      Nombre                       |                    Evento                    | Momento  | Nivel |                                         Regla                                         |        Origen        |
| :-----------------------------------------------: | :------------------------------------------: | :------: | :---: | :-----------------------------------------------------------------------------------: | :------------------: |
| `trg_plantillamensaje_variables_insert_integrity` |                   `INSERT`                   | `BEFORE` | `ROW` | Toda variable declarada aparece en el texto, y todo marcador del texto está declarado | [`RF-P-04`][rf-p-04] |
| `trg_plantillamensaje_variables_update_integrity` | `UPDATE` de `asunto`, `cuerpo` o `variables` | `BEFORE` | `ROW` |                                    La misma regla                                     | [`RF-P-04`][rf-p-04] |

El trigger evita el fallo más silencioso de este tipo de tabla: una plantilla
guardada con `{nombre_completo}` donde el sistema envía `{nombre}` no falla al
guardarse, falla al enviarse, y el correo sale con el marcador literal en el
cuerpo.

### Plantillas sembradas

`verificacion_email`, `recuperacion_password` e `invitacion_administrativa`,
las tres que usa hoy el flujo de cuentas.

---

## `tipo_identificador`

Catálogo de los documentos que reconocen a una persona, con su patrón de
validación. Lo usa [`identificador_user`][perfiles-identificador].

- **Régimen:** [Mutable rastreada][auditoria]
- **Volumen estimado:** 5 filas
- **Origen:**
  > - [`RF-A-09`][rf-a-09]

### Columnas

No lleva `descripcion`.

|       Campo        |      Tipo      | Nulo | Predeterminado |                   Descripción                   |
| :----------------: | :------------: | :--: | :------------: | :---------------------------------------------: |
|      `regex`       | `varchar(100)` |  no  |      `''`      | Expresión regular POSIX; vacío = sin validación |
| `is_institucional` |   `boolean`    |  no  |    `false`     |       Lo emite la UAM (el carné, el CIF)        |

### Triggers

|                   Nombre                    |        Evento         | Momento  | Nivel |                              Regla                              |        Origen        |
| :-----------------------------------------: | :-------------------: | :------: | :---: | :-------------------------------------------------------------: | :------------------: |
|      `trg_normalize_tipoidentificador`      | `INSERT`<br/>`UPDATE` | `BEFORE` | `ROW` | Normaliza `codigo`, `etiqueta` y `regex` (espacios, minúsculas) |      Convención      |
| `trg_tipoidentificador_test_posix_validity` | `INSERT`<br/>`UPDATE` | `BEFORE` | `ROW` |          Rechaza un `regex` que PostgreSQL no compila           | [`RF-A-09`][rf-a-09] |

### Notas de diseño

El patrón se guarda como dato y no en el código porque el formato del CIF puede
cambiar cuando la Universidad cambie su numeración, y ese cambio no debe ser un
despliegue. Un identificador que no cumple el patrón se admite marcándolo como no
verificado, nunca se rechaza: ver [`identificador_user`][perfiles-identificador].

---

## Catálogos operativos

Cinco tablas con exactamente la forma común. Todas provienen de listas
desplegables de las matrices de soporte y ninguna tiene lógica propia.

|        Modelo        | Filas |                            Origen del contenido                            |
| :------------------: | :---: | :------------------------------------------------------------------------: |
|  `RolParticipacion`  |  11   |    Matriz de participaciones: participante, líder, mentor estudiantil…     |
|   `TipoActividad`    |   7   |      Ambas matrices: formación, concurso, programa, evento, proyecto…      |
|     `TipoMentor`     |   4   |             Listado de mentores, columna _tipo de mentor UAM_              |
| `TipoReconocimiento` |   6   | Derivado del glosario: culminación, clasificación, premio, microcredencial |
|  `AreaExperiencia`   | 20-30 |    Derivado de las descripciones profesionales del listado de mentores     |

`area_experiencia` no existe en ninguna matriz: el listado de mentores guarda la
experiencia como un párrafo de descripción profesional. Extraerla a un catálogo
es lo que permite responder _qué mentores saben de tecnología financiera_, que
hoy exige leer treinta párrafos. La descripción en prosa se conserva igualmente
en el perfil, porque dice cosas que ningún catálogo captura.

---

## Ubicaciones

`departamento` (17 filas) y `municipio` (153 filas): la división
político-administrativa de Nicaragua. No son `RudiCatalogo`: no tienen `codigo`
sino `nombre`, y no llevan tabla de eventos porque no cambian.

- **Régimen:** [Mutable con borrado lógico][auditoria] (`ApiSoftDeleteModel`, sin `@track_table()`)

|                   Tabla                    |                                        Unicidad                                        |
| :----------------------------------------: | :------------------------------------------------------------------------------------: |
|               `departamento`               |               `unq_departamento_nombre` sobre `upper(unaccent(nombre))`                |
| `municipio` (`departamento_id` `RESTRICT`) | `unq_municipio_nombre_departamento` sobre `(departamento_id, upper(unaccent(nombre)))` |

[auditoria]: ../convenciones.md#auditoria-por-tabla
[convenciones-columnas]: ../convenciones.md#columnas-estandar
[d-08]: ../decisiones.md#d-08
[d-15]: ../decisiones.md#d-15
[d-18]: ../decisiones.md#d-18
[estados]: estados.md
[perfiles-identificador]: perfiles.md#identificador_user
[taxonomias]: taxonomias.md
[triggers-funciones]: ../triggers.md#funciones-auxiliares
[triggers-motivo]: ../triggers.md#motivo-de-lista-cerrada
[rf-a-09]: ../../requerimientos/funcionales/administracion.md#rf-a-09
[rf-a-12]: ../../requerimientos/funcionales/administracion.md#rf-a-12
[rf-a-13]: ../../requerimientos/funcionales/administracion.md#rf-a-13
[rf-a-14]: ../../requerimientos/funcionales/administracion.md#rf-a-14
[rf-a-29]: ../../requerimientos/funcionales/administracion.md#rf-a-29
[rf-a-35]: ../../requerimientos/funcionales/administracion.md#rf-a-35
[rf-a-48]: ../../requerimientos/funcionales/administracion.md#rf-a-48
[rf-p-03]: ../../requerimientos/funcionales/participantes.md#rf-p-03
[rf-p-04]: ../../requerimientos/funcionales/participantes.md#rf-p-04
[rf-p-06]: ../../requerimientos/funcionales/participantes.md#rf-p-06
[rf-p-19]: ../../requerimientos/funcionales/participantes.md#rf-p-19
