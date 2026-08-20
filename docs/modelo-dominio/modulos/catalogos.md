---
icon: lucide/sliders-horizontal
---

# Catálogos y parámetros

Datos que la DIEM gobierna sin desplegar código: las listas desplegables de las
matrices, los parámetros del motor y las plantillas de mensaje.

Las tablas de estado siguen el mismo principio pero tienen su propia página:
[`Estados`][estados]. Las taxonomías de innovación también, porque no las
administra la DIEM sino marcos externos: [`Taxonomías`][taxonomias].

## Requerimientos cubiertos

- [`RF-A-12`][rf-a-12]
- [`RF-A-13`][rf-a-13]
- [`RF-A-14`][rf-a-14]
- [`RF-A-48`][rf-a-48]
- [`RF-P-06`][rf-p-06]

---

## `parametro_sistema`

Los valores que gobiernan el comportamiento del sistema. Es la tabla que hace
posible una [sola pantalla de configuración][rf-a-48] con cambio sin despliegue,
historial y reversión.

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** ~12 filas

### Columnas

|       Campo       |     Tipo      | Nulo |                                    Descripción                                    |
| :---------------: | :-----------: | :--: | :-------------------------------------------------------------------------------: |
|      `clave`      | `varchar(60)` |  no  |          Única, con espacio de nombres: `registro.dominio_institucional`          |
|      `grupo`      | `varchar(20)` |  no  |                                    Ver `CHECK`                                    |
|      `valor`      |    `jsonb`    |  no  |                                   Valor vigente                                   |
|    `tipo_dato`    | `varchar(16)` |  no  | `entero` / `duracion_min` / `duracion_dia` / `booleano` / `texto` / `lista_texto` |
|  `restricciones`  |    `jsonb`    |  no  |                        Mínimo, máximo y valores admitidos                         |
|   `descripcion`   |    `text`     |  no  |                             Qué cambia al modificarlo                             |
| `actualizado_por` |    `uuid`     |  sí  |                       Llave foránea `RESTRICT` a `usuario`                        |

### Constraints

```postgresql
CONSTRAINT chk_parametrosistema_clave_formato
CHECK (clave ~ '^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$')

CONSTRAINT chk_parametrosistema_grupo
CHECK (grupo IN ('registro', 'sesion', 'inscripcion', 'vigencia', 'importacion'))

CONSTRAINT chk_parametrosistema_tipo
CHECK (
  tipo_dato IN (
    'entero',
    'duracion_min',
    'duracion_dia',
    'booleano',
    'texto',
    'lista_texto'
  )
)

CONSTRAINT chk_parametrosistema_restricciones_objeto
CHECK (jsonb_typeof(restricciones) = 'object')
```

### Unicidad

|            Nombre            | Definición |
| :--------------------------: | :--------: |
| `unq_parametrosistema_clave` | `(clave)`  |

### Triggers

|                Nombre                 |      Evento       | Momento  | Nivel |                        Regla                         |        Origen        |
| :-----------------------------------: | :---------------: | :------: | :---: | :--------------------------------------------------: | :------------------: |
| `trg_parametrosistema_clave_readonly` | `UPDATE OF clave` | `BEFORE` | `ROW` |         Rechaza cualquier cambio de `clave`          |    [`D-08`][d-08]    |
|   `trg_parametrosistema_historial`    | `UPDATE OF valor` | `AFTER`  | `ROW` | Escribe el valor anterior en `bitacora` con el actor | [`RF-A-48`][rf-a-48] |
|   `trg_parametrosistema_no_borrar`    |     `DELETE`      | `BEFORE` | `ROW` |                  Bloquea el borrado                  |    [`D-18`][d-18]    |

### Parámetros previstos

|                 Clave                  |     Grupo     | Valor inicial |                                   Efecto                                   |
| :------------------------------------: | :-----------: | :-----------: | :------------------------------------------------------------------------: |
|    `registro.dominio_institucional`    |  `registro`   | `uamv.edu.ni` |   Dominio exigido al perfil de estudiante UAM, por [`RF-P-03`][rf-p-03]    |
| `registro.umbral_similitud_duplicado`  |  `registro`   |    `0.85`     |            Sensibilidad de la detección de [`RF-A-07`][rf-a-07]            |
|    `registro.vigencia_verificacion`    |  `registro`   |  `2880 min`   |               Vigencia del enlace de verificación de correo                |
|      `registro.reenvios_por_hora`      |  `registro`   |      `3`      |                       Límite de reenvíos del enlace                        |
|       `sesion.expiracion_admin`        |   `sesion`    |   `30 min`    |                    Inactividad del panel administrativo                    |
|    `sesion.expiracion_participante`    |   `sesion`    |  `10080 min`  |                  Inactividad del portal del participante                   |
|       `sesion.intentos_bloqueo`        |   `sesion`    |      `5`      |                Intentos fallidos antes del bloqueo temporal                |
| `inscripcion.lista_espera_por_defecto` | `inscripcion` |    `true`     |              Si una actividad nueva habilita lista de espera               |
|    `vigencia.perfil_desactualizado`    |  `vigencia`   |   `365 día`   | Antigüedad tras la que se pide revisar el perfil, por [`RF-P-13`][rf-p-13] |
|  `vigencia.invitacion_administrativa`  |  `vigencia`   |    `72 h`     |                     Vigencia de la invitación al panel                     |
|       `importacion.filas_maximo`       | `importacion` |    `2000`     |                     Tamaño máximo de una carga masiva                      |
|    `importacion.tolerancia_rechazo`    | `importacion` |     `20%`     |      Proporción de rechazos por encima de la cual el resumen advierte      |

### Notas de diseño

`valor` es `jsonb` y no una columna por tipo porque los doce parámetros tienen
seis tipos distintos y una tabla con doce columnas nulables sería peor. El tipo
declarado y las restricciones permiten que la interfaz construya el control
adecuado —número, interruptor, texto— sin conocer cada clave.

El historial vive en `bitacora` y no en una tabla propia de cambios porque el
volumen no lo justifica: doce parámetros que cambian unas pocas veces al año no
merecen su propia tabla de versiones.

---

## `motivo`

Catálogo único de motivos para todo el sistema, discriminado por ámbito.
Cancelaciones, rechazos y anulaciones citan aquí en lugar de guardar texto libre.

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 25-40 filas
- **Origen:**
  > - [`RF-A-29`][rf-a-29]
  > - [`RF-P-19`][rf-p-19]

### Columnas

|     Campo      |      Tipo      | Nulo |   Predeterminado   |                 Descripción                 |
| :------------: | :------------: | :--: | :----------------: | :-----------------------------------------: |
|    `codigo`    | `varchar(50)`  |  no  |                    |            Identificador estable            |
|   `etiqueta`   | `varchar(120)` |  no  |                    |          Texto visible al elegirlo          |
|    `ambito`    | `varchar(30)`  |  no  |                    |                 Ver `CHECK`                 |
| `visible_para` | `varchar(20)`  |  no  | `'administracion'` | `participante` / `administracion` / `ambos` |
|  `exige_nota`  |   `boolean`    |  no  |      `false`       | Obliga a escribir texto además de elegirlo  |
|    `activo`    |   `boolean`    |  no  |       `true`       |                                             |

### Constraints

```postgresql
CONSTRAINT chk_motivo_ambito
CHECK (
  ambito IN (
    'cancelacion_inscripcion',
    'cancelacion_actividad',
    'anulacion_participacion',
    'anulacion_constancia',
    'declinacion_mentoria',
    'fusion_usuario',
    'rechazo_importacion',
    'retiro_consentimiento'
  )
)

CONSTRAINT chk_motivo_visible
CHECK (visible_para IN ('participante', 'administracion', 'ambos'))
```

### Unicidad

|       Nombre        |     Definición     |
| :-----------------: | :----------------: |
| `unq_motivo_codigo` | `(ambito, codigo)` |

### Notas de diseño

Un catálogo único con discriminador, en lugar de ocho tablas de motivo, porque la
forma es idéntica y la única diferencia es dónde aparece cada fila. `ambito` es
discriminador y no estado: no cambia nunca para una fila dada.

`visible_para` existe porque los motivos de cancelación que ve el estudiante
—_conflicto de horario_, _ya no me interesa_— no son los mismos que registra la
administración —_no cumple requisitos_, _duplicado_—, y mezclarlos en un solo
selector produciría datos inservibles para los reportes.

---

## `plantilla_mensaje`

Textos de los correos que envía el sistema, editables sin desplegar.

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** ~10 filas
- **Origen:**
  > - [`RF-P-04`][rf-p-04]
  > - [`RF-A-35`][rf-a-35]

### Columnas

|    Campo    |      Tipo      | Nulo | Predeterminado |                   Descripción                   |
| :---------: | :------------: | :--: | :------------: | :---------------------------------------------: |
|  `codigo`   | `varchar(50)`  |  no  |                |   `verificacion_correo`, `constancia_emitida`   |
|  `asunto`   | `varchar(200)` |  no  |                |              Admite sustituciones               |
|  `cuerpo`   |     `text`     |  no  |                |         Cuerpo con marcadores `{campo}`         |
| `variables` |    `jsonb`     |  no  |     `'[]'`     | Lista de marcadores admitidos en esta plantilla |
|  `activo`   |   `boolean`    |  no  |     `true`     |                                                 |

### Constraints

```postgresql
CONSTRAINT chk_plantillamensaje_variables_arreglo
CHECK (jsonb_typeof(variables) = 'array')

CONSTRAINT chk_plantillamensaje_cuerpo_longitud
CHECK (length(cuerpo) BETWEEN 1 AND 8000)
```

### Triggers

|                  Nombre                   |                Evento                | Momento  | Nivel |                                Regla                                 |        Origen        |
| :---------------------------------------: | :----------------------------------: | :------: | :---: | :------------------------------------------------------------------: | :------------------: |
| `trg_plantillamensaje_marcadores_validos` | `INSERT`, `UPDATE OF cuerpo, asunto` | `BEFORE` | `ROW` | Rechaza la plantilla que use un marcador no declarado en `variables` | [`RF-P-04`][rf-p-04] |

El trigger evita el fallo más silencioso de este tipo de tabla: una plantilla
guardada con `{nombre_completo}` donde el sistema envía `{nombre}` no falla al
guardarse, falla al enviarse, y el correo sale con el marcador literal en el
cuerpo.

---

## Catálogos operativos

Doce tablas con la misma forma. Todas provienen de listas desplegables de las
matrices de soporte y ninguna tiene lógica propia.

- **Régimen:** [Mutable protegida][auditoria]
- **Origen:**
  > - [`RF-A-14`][rf-a-14]
  > - [`RF-P-06`][rf-p-06]

### Forma común

|     Campo     |      Tipo      | Nulo | Predeterminado |            Descripción             |
| :-----------: | :------------: | :--: | :------------: | :--------------------------------: |
|   `codigo`    | `varchar(50)`  |  no  |                |       Identificador estable        |
|  `etiqueta`   | `varchar(120)` |  no  |                |    Texto visible en formularios    |
| `descripcion` |     `text`     |  no  |      `''`      |     Ayuda contextual del campo     |
|    `orden`    |   `smallint`   |  no  |      `0`       |      Posición en el selector       |
|   `activo`    |   `boolean`    |  no  |     `true`     | Puede elegirse en registros nuevos |

Cada una lleva `unq_<tabla>_codigo` sobre `(codigo)`, `trg_<tabla>_no_borrar` y
`trg_<tabla>_codigo_readonly`.

### Inventario

|         Tabla         | Filas |                            Origen del contenido                            |
| :-------------------: | :---: | :------------------------------------------------------------------------: |
|        `sexo`         |   3   |    Matriz de estudiantes, más `prefiero_no_declarar` por [`D-19`][d-19]    |
|        `etnia`        |  13   |        Matriz de estudiantes: doce pueblos y `otra`, autodeclarada         |
|   `talla_camiseta`    |   7   |                      Matriz de estudiantes: XS a 3XL                       |
|   `nivel_academico`   |   6   |                  Listado de mentores: técnico a doctorado                  |
|    `anio_carrera`     |   8   |           Matriz de estudiantes: 1.º a 6.º, egresado, no aplica            |
|  `rol_participacion`  |  11   |    Matriz de participaciones: participante, líder, mentor estudiantil…     |
|   `tipo_actividad`    |   7   |      Ambas matrices: formación, concurso, programa, evento, proyecto…      |
|     `tipo_mentor`     |   4   |             Listado de mentores, columna _tipo de mentor UAM_              |
| `tipo_reconocimiento` |   6   | Derivado del glosario: culminación, clasificación, premio, microcredencial |
|  `area_experiencia`   | 20-30 |    Derivado de las descripciones profesionales del listado de mentores     |
|    `departamento`     |  17   |               División político-administrativa de Nicaragua                |
|      `municipio`      |  153  |   Listado de mentores, columna _municipio_; referencia a `departamento`    |

`municipio` es el único que se aparta de la forma común: agrega
`departamento_id` con llave foránea `RESTRICT`.

### Notas de diseño

`etnia` conserva las doce denominaciones exactas de la matriz de estudiantes.
Cambiarlas por una lista propia rompería la comparación con los reportes
históricos y con los formatos que la Universidad reporta a instancias externas.

`area_experiencia` no existe en ninguna matriz: el listado de mentores guarda la
experiencia como un párrafo de descripción profesional. Extraerla a un catálogo
es lo que permite responder _qué mentores saben de tecnología financiera_, que
hoy exige leer treinta párrafos. La descripción en prosa se conserva igualmente
en el perfil, porque dice cosas que ningún catálogo captura.

`sexo` incluye un tercer valor por [`D-19`][d-19]. La matriz solo tiene dos, pero
un campo obligatorio sin salida obliga a la persona a declarar algo o a abandonar
el formulario, y ninguna de las dos cosas produce un dato mejor.

[auditoria]: ../convenciones.md#auditoria-por-tabla
[d-08]: ../decisiones.md#d-08
[d-18]: ../decisiones.md#d-18
[d-19]: ../decisiones.md#d-19
[estados]: estados.md
[taxonomias]: taxonomias.md
[rf-a-07]: ../../requerimientos/funcionales/administracion.md#rf-a-07
[rf-a-12]: ../../requerimientos/funcionales/administracion.md#rf-a-12
[rf-a-13]: ../../requerimientos/funcionales/administracion.md#rf-a-13
[rf-a-14]: ../../requerimientos/funcionales/administracion.md#rf-a-14
[rf-a-29]: ../../requerimientos/funcionales/administracion.md#rf-a-29
[rf-a-35]: ../../requerimientos/funcionales/administracion.md#rf-a-35
[rf-a-48]: ../../requerimientos/funcionales/administracion.md#rf-a-48
[rf-p-03]: ../../requerimientos/funcionales/participantes.md#rf-p-03
[rf-p-04]: ../../requerimientos/funcionales/participantes.md#rf-p-04
[rf-p-06]: ../../requerimientos/funcionales/participantes.md#rf-p-06
[rf-p-13]: ../../requerimientos/funcionales/participantes.md#rf-p-13
[rf-p-19]: ../../requerimientos/funcionales/participantes.md#rf-p-19
