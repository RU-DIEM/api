---
icon: lucide/id-card
---

# Personas y perfiles

La persona, sus identificadores, su consentimiento y los perfiles que declara.
Viven en las apps `rudi_auth` (persona, identificadores, consentimiento) y
`rudi_profiles` (estructura académica y perfiles).

Es el módulo central del proyecto. El problema que motiva el sistema no es
registrar personas: es reconocer que dos registros son la misma persona.

Las credenciales, los roles, las sesiones y la verificación de correo **no**
son de este módulo: son del subsistema de autenticación del template
(`api_auth`), que el dominio solo referencia por llave foránea. Ver
[Cuenta y persona](#cuenta-y-persona).

## Requerimientos cubiertos

- [`RF-P-01`][rf-p-01]
- [`RF-P-02`][rf-p-02]
- [`RF-P-03`][rf-p-03]
- [`RF-P-06`][rf-p-06]
- [`RF-P-07`][rf-p-07]
- [`RF-P-08`][rf-p-08]
- [`RF-P-09`][rf-p-09]
- [`RF-P-10`][rf-p-10]
- [`RF-P-11`][rf-p-11]
- [`RF-P-12`][rf-p-12]
- [`RF-P-13`][rf-p-13]
- [`RF-A-05`][rf-a-05]
- [`RF-A-07`][rf-a-07]
- [`RF-A-09`][rf-a-09]
- [`RF-A-10`][rf-a-10]
- [`RF-A-11`][rf-a-11]
- [`RF-A-12`][rf-a-12]
- [`RF-A-13`][rf-a-13]

---

## Cuenta y persona

Por [`D-03`][d-03], cada persona es una fila de `ApiUser` y una de `RudiUser`,
unidas 1:1.

|                 Concepto                  |                                       Dónde vive                                        |
| :---------------------------------------: | :-------------------------------------------------------------------------------------: |
|    Correo, nombres, contraseña, login     |                                 `ApiUser` (`api_auth`)                                  |
|      Verificación de correo, enlaces      | `VerificationCode` (`api_auth`), con propósitos `email`, `invitation`, `password_reset` |
|             Roles y permisos              |                               Grupos y permisos de Django                               |
|            Sesiones y bloqueo             |             JWT, lista de revocación y _throttling_ del template; sin tabla             |
| Estado, origen, demografía, anonimización |                                `RudiUser` (`rudi_auth`)                                 |

`ApiUser.is_active` no se escribe a mano: lo sincroniza
`trg_rudiuser_sync_active` con `estado_rudiuser.allow_ingreso`, de modo que
suspender a la persona impide su login sin que el servicio tenga que recordar
hacerlo.

---

## `rudi_user`

La persona. Toda tabla del dominio que nombra a alguien apunta aquí.

- **Régimen:** [Mutable protegida][auditoria], rastreada
- **Volumen estimado:** 2,000-8,000 filas
- **Origen:**
  > - [`RF-P-01`][rf-p-01]
  > - [`RF-P-06`][rf-p-06]
  > - [`RF-A-05`][rf-a-05]

### Columnas

|       Campo        |      Tipo      | Nulo | Predeterminado |               Descripción                |
| :----------------: | :------------: | :--: | :------------: | :--------------------------------------: |
|     `user_id`      |     `uuid`     |  no  |                |         Cuenta (`ApiUser`), 1:1          |
|    `estado_id`     |     `uuid`     |  no  |                |    Llave foránea a `estado_rudiuser`     |
|      `origen`      | `varchar(20)`  |  no  |                |  `usuario` / `sistema` / `importacion`   |
| `fecha_nacimiento` |     `date`     |  sí  |                | Nulo en registros importados sin el dato |
|     `telefono`     | `varchar(128)` |  no  |      `''`      |     E.164; es el número de WhatsApp      |
|      `genero`      | `varchar(20)`  |  no  |      `''`      |        `Generos`, [`D-19`][d-19]         |
|      `etnia`       | `varchar(20)`  |  no  |      `''`      |         `Etnias`, [`D-19`][d-19]         |
|      `talla`       | `varchar(10)`  |  no  |      `''`      |              `TallasCamisa`              |
|  `anonimizado_at`  | `timestamptz`  |  sí  |                |      Marca de cierre de la persona       |

### Llaves foráneas

|   Columna   |    Referencia     | `ON DELETE` |
| :---------: | :---------------: | :---------: |
|  `user_id`  |     `ApiUser`     | `RESTRICT`  |
| `estado_id` | `estado_rudiuser` | `RESTRICT`  |

### Constraints

```postgresql
CONSTRAINT chk_rudiuser_origen
CHECK (origen IN ('importacion', 'sistema', 'usuario'))

CONSTRAINT chk_rudiuser_genero      -- Generos o ''
CONSTRAINT chk_rudiuser_etnia       -- Etnias o ''
CONSTRAINT chk_rudiuser_talla       -- TallasCamisa o ''

CONSTRAINT chk_rudiuser_telefono_e164
CHECK (telefono = '' OR telefono ~ '^\+[1-9]\d{1,14}$')
```

### Unicidad

|         Nombre          |            Definición             |             Propósito              |
| :---------------------: | :-------------------------------: | :--------------------------------: |
| `rudiuser_user_id_key`  |            `(user_id)`            |       Una persona por cuenta       |
| `unq_rudiuser_telefono` | `(telefono) WHERE telefono <> ''` | Un número de WhatsApp, una persona |

### Triggers

|             Nombre             |            Evento             | Momento  | Nivel |                                           Regla                                            |        Origen        |
| :----------------------------: | :---------------------------: | :------: | :---: | :----------------------------------------------------------------------------------------: | :------------------: |
|   `trg_readonly_origen_user`   |  `UPDATE OF origen, user_id`  | `BEFORE` | `ROW` |                           El origen y la cuenta no cambian nunca                           |    [`D-08`][d-08]    |
|  `trg_rudiuser_estado_activo`  |     `INSERT`<br/>`UPDATE`     | `BEFORE` | `ROW` |                            El estado asignado debe estar activo                            | [Familia][t-estado]  |
| `trg_rudiuser_estado_terminal` | `UPDATE` con cambio de estado | `BEFORE` | `ROW` |                   Una persona anonimizada no vuelve a cambiar de estado                    | [Familia][t-estado]  |
|  `trg_rudiuser_anonimizacion`  |           `UPDATE`            | `BEFORE` | `ROW` |                     Una persona con `anonimizado_at` no admite cambios                     | [`RF-A-50`][rf-a-50] |
|     `trg_rudiuser_estado`      |     `INSERT`<br/>`UPDATE`     | `BEFORE` | `ROW` | Un estado terminal fija `anonimizado_at`; con la marca puesta no se admite uno no terminal | [`RF-A-50`][rf-a-50] |
| `trg_rudiuser_fechanacimiento` |     `INSERT`<br/>`UPDATE`     | `BEFORE` | `ROW` |                            Fecha entre 1930 y hace catorce años                            |  Defensa de captura  |
|   `trg_rudiuser_sync_active`   |     `INSERT`<br/>`UPDATE`     | `AFTER`  | `ROW` |                     Copia `estado.allow_ingreso` a `ApiUser.is_active`                     | [`RF-P-05`][rf-p-05] |
|     `trg_rudiuser_profile`     |      `UPDATE`, diferido       | `AFTER`  | `ROW` |            Un estado con `allow_inscripcion` exige al menos un perfil declarado            |   [`RN-03`][rn-03]   |

`trg_rudiuser_profile` se declara en `rudi_profiles` y se registra sobre
`RudiUser` con `pgtrigger.register(...)`: conoce las tablas de perfil, que
`rudi_auth` no debe importar.

### Notas de diseño

`RudiUser` **no** tiene columnas `cif`, `cedula`, `tipo_usuario`, `carrera_id` ni
`puntos`. Cada una de esas ausencias es deliberada y está justificada en
[`D-04`][d-04], [`D-05`][d-05], [`D-17`][d-17] y [`D-12`][d-12] respectivamente.

La anonimización de [`RF-A-50`][rf-a-50] mueve la persona a un estado terminal,
lo que fija `anonimizado_at` y congela la fila. Las participaciones siguen
apuntando a ella y siguen contando en los agregados de los años en que
ocurrieron. Borrar la fila haría que los reportes de 2024 cambiaran en 2027, que
es exactamente lo que [`RN-18`][rn-18] prohíbe.

La **fusión de duplicados** ([`RF-A-07`][rf-a-07]) está **pendiente**. Exige
reescribir las llaves foráneas de todos los módulos hacia la persona conservada,
de modo que se hará al final, como un servicio que traslada filas y deja rastro
en las tablas de eventos.

---

## `identificador_user`

Documento que reconoce a una persona. Es la tabla que hace cumplir
[`RN-01`][rn-01] y [`RN-02`][rn-02].

- **Régimen:** [Mutable protegida][auditoria], rastreada
- **Volumen estimado:** 3,000-12,000 filas
- **Origen:**
  > - [`RF-P-02`][rf-p-02]
  > - [`RF-A-09`][rf-a-09]

### Columnas

|        Campo        |     Tipo      | Nulo | Predeterminado |                     Descripción                     |
| :-----------------: | :-----------: | :--: | :------------: | :-------------------------------------------------: |
|      `user_id`      |    `uuid`     |  no  |                |             Llave foránea a la persona              |
|      `tipo_id`      |    `uuid`     |  no  |                |        Llave foránea a `tipo_identificador`         |
|       `valor`       | `varchar(20)` |  no  |                |     Tal como lo declaró la persona, con formato     |
| `valor_normalizado` | `varchar(20)` |  no  |    generada    | **Almacenada**. Mayúsculas, sin guiones ni espacios |
|      `is_main`      |   `boolean`   |  no  |    `false`     |      El que la persona usa para identificarse       |
|   `verificado_at`   | `timestamptz` |  sí  |                |          Nulo = pendiente de verificación           |
| `verificado_por_id` |    `uuid`     |  sí  |                |  Llave foránea `RESTRICT` a la cuenta que verificó  |

### Columna generada

```postgresql
valor_normalizado varchar(20)
GENERATED ALWAYS AS (upper(regexp_replace(valor, '[^A-Za-z0-9]', '', 'g'))) STORED
```

Almacenada porque sostiene el índice único que garantiza la no duplicidad.
Sin ella, `001-150188-0001E` y `0011501880001E` serían dos personas distintas, y
las matrices existentes contienen ambas formas de escribir la misma cédula.

### Constraints

```postgresql
CONSTRAINT chk_identificadoruser_verificacion_coherente
CHECK ((verificado_at IS NULL) = (verificado_por_id IS NULL))

CONSTRAINT chk_identificadoruser_valor_longitud
CHECK (length(valor_normalizado) BETWEEN 4 AND 20)
```

### Unicidad

|              Nombre               |           Definición           |                    Propósito                     |
| :-------------------------------: | :----------------------------: | :----------------------------------------------: |
|   `unq_identificadoruser_valor`   | `(tipo_id, valor_normalizado)` |  Un identificador pertenece a una sola persona   |
| `unq_identificadoruser_tipo_user` |      `(user_id, tipo_id)`      | Una persona tiene un solo documento de cada tipo |
| `unq_identificadoruser_principal` |   `(user_id) WHERE is_main`    |         Como máximo uno es el principal          |

### Triggers

|                Nombre                |        Evento         | Momento  | Nivel |                                            Regla                                            |        Origen        |
| :----------------------------------: | :-------------------: | :------: | :---: | :-----------------------------------------------------------------------------------------: | :------------------: |
|    `trg_identificadoruser_regex`     | `INSERT`<br/>`UPDATE` | `BEFORE` | `ROW` | Si `valor` no cumple `tipo_identificador.regex`, anula la verificación en lugar de rechazar | [`RF-A-09`][rf-a-09] |
|  `trg_identificadoruser_first_main`  |       `INSERT`        | `BEFORE` | `ROW` |                   El primer identificador de una persona es el principal                    |   [`RN-01`][rn-01]   |
| `trg_identificadoruser_protect_main` |       `UPDATE`        | `AFTER`  | `ROW` |           Una persona no anonimizada no puede quedar sin identificador principal            |   [`RN-01`][rn-01]   |

### Notas de diseño

`unq_identificadoruser_valor` es el invariante más importante del sistema. Es la
traducción exacta de [`RN-02`][rn-02] a un mecanismo que el motor garantiza bajo
concurrencia, y la razón por la que dos formularios simultáneos no pueden crear
dos registros de la misma persona.

El índice se declara sobre `(tipo_id, valor_normalizado)` y no solo sobre el
valor porque nada impide que un CIF y un pasaporte coincidan como cadena. Son
espacios de numeración independientes.

`trg_identificadoruser_regex` **no rechaza** el valor que incumple el patrón: lo
admite sin verificar. Es una decisión consciente sobre la migración. Las matrices
existentes tienen cédulas incompletas y CIF con caracteres extraños, y un modelo
que las rechace obliga a limpiar tres mil filas antes de poder usar el sistema.

---

## `politica_privacidad`

Versiones del texto de la política de tratamiento de datos.

- **Régimen:** [Mutable protegida][auditoria], rastreada
- **Volumen estimado:** < 10 filas
- **Origen:**
  > - [`RF-P-07`][rf-p-07]

### Columnas

|      Campo      |      Tipo      | Nulo |                 Descripción                 |
| :-------------: | :------------: | :--: | :-----------------------------------------: |
|    `version`    | `varchar(20)`  |  no  |          `<mayor>.<menor>`, única           |
|    `titulo`     | `varchar(200)` |  no  |                                             |
|     `texto`     |     `text`     |  no  |                  No vacío                   |
| `vigente_desde` |     `date`     |  no  |                                             |
| `vigente_hasta` |     `date`     |  sí  | Nulo = vigente; posterior a `vigente_desde` |

### Unicidad

|              Nombre              |              Definición              |            Propósito             |
| :------------------------------: | :----------------------------------: | :------------------------------: |
| `unq_politicaprivacidad_version` |             `(version)`              |                                  |
| `unq_politicaprivacidad_vigente` | `(true) WHERE vigente_hasta IS NULL` | Exactamente una política vigente |

Publicar una versión nueva cierra la anterior en la misma transacción
(`PoliticaCreateOperation`).

---

## `consentimiento_datos`

La autorización de tratamiento de datos de cada persona. Tiene tres valores
reales —otorgado, pendiente de verificar, no autorizado— y por eso es un estado
y no un booleano.

- **Régimen:** [Mutable protegida][auditoria], rastreada
- **Volumen estimado:** una fila por persona
- **Origen:**
  > - [`RF-P-07`][rf-p-07]
  > - [`RF-A-06`][rf-a-06]

### Columnas

|      Campo      |      Tipo      | Nulo | Predeterminado |                  Descripción                   |
| :-------------: | :------------: | :--: | :------------: | :--------------------------------------------: |
|    `user_id`    |     `uuid`     |  no  |                |                 Persona, única                 |
|  `politica_id`  |     `uuid`     |  no  |                |        Versión de la política aceptada         |
|   `estado_id`   |     `uuid`     |  no  |                |    Llave foránea a `estado_consentimiento`     |
|     `canal`     | `varchar(20)`  |  no  |                | `portal` / `formulario_fisico` / `importacion` |
|  `otorgado_at`  | `timestamptz`  |  sí  |                |                                                |
|  `retirado_at`  | `timestamptz`  |  sí  |                |   Solo si antes se otorgó (`chk_..._retiro`)   |
| `evidencia_url` | `varchar(500)` |  no  |      `''`      |         Escaneo del formulario físico          |

### Triggers

|                  Nombre                   |            Evento             | Momento  | Nivel |                     Regla                      |       Origen        |
| :---------------------------------------: | :---------------------------: | :------: | :---: | :--------------------------------------------: | :-----------------: |
|  `trg_consentimientodatos_estado_activo`  |     `INSERT`<br/>`UPDATE`     | `BEFORE` | `ROW` |      El estado asignado debe estar activo      | [Familia][t-estado] |
| `trg_consentimientodatos_estado_terminal` | `UPDATE` con cambio de estado | `BEFORE` | `ROW` | Un consentimiento retirado no vuelve a cambiar | [Familia][t-estado] |

### Notas de diseño

El retiro exige un `motivo` del ámbito `revocar_consentimiento`, que hoy valida
el servicio (`retirar_consentimiento`) porque la tabla no guarda el motivo: queda
en el evento de la tabla rastreada. Si el motivo pasa a ser columna, la
validación pasa a la familia [motivo de lista cerrada][t-motivo].

---

## Estructura académica

Facultades y carreras de la UAM, e instituciones externas.

### `facultad` y `carrera`

Catálogos con la [forma común][catalogos-forma] (`RudiCatalogo`), rastreados.
`facultad` agrega `abreviacion`; `carrera` agrega `facultad_id` (`RESTRICT`) y
`duracion` (años, entre 1 y 8), y es única por
`(facultad_id, upper(unaccent(etiqueta)))`.

- **Régimen:** [Mutable rastreada][auditoria]
- **Volumen estimado:** 5-8 facultades, 25-50 carreras

### `institucion`

- **Régimen:** [Mutable rastreada][auditoria]
- **Volumen estimado:** 50-200 filas

|      Campo       |      Tipo      | Nulo |                                           Descripción                                           |
| :--------------: | :------------: | :--: | :---------------------------------------------------------------------------------------------: |
|     `nombre`     | `varchar(200)` |  no  |                  Único sobre `upper(unaccent(nombre))`, al menos 2 caracteres                   |
|      `tipo`      | `varchar(30)`  |  no  | `universidad` / `centro_tecnico` / `colegio` / `empresa` / `gobierno` / `organizacion` / `otra` |
| `normalizada_at` | `timestamptz`  |  sí  |                      Nulo = alta desde un formulario, sin revisar todavía                       |

|           Nombre            |                 Definición                  |          Propósito          |
| :-------------------------: | :-----------------------------------------: | :-------------------------: |
| `idx_institucion_pendiente` | `(created_at) WHERE normalizada_at IS NULL` | Cola de revisión de la DIEM |

`institucion` es el único catálogo que admite altas desde un formulario de
registro, y por eso es el único que lleva marca de normalización. Exigir que el
administrador dé de alta cada institución antes de que alguien pueda registrarse
bloquea el registro en el momento exacto en que la persona está dispuesta a
completarlo.

---

## Perfiles

Cuatro perfiles acumulables ([`D-05`][d-05]). Todos heredan de `RudiProfile`:

|      Campo      |     Tipo      | Nulo | Predeterminado |                              Descripción                               |
| :-------------: | :-----------: | :--: | :------------: | :--------------------------------------------------------------------: |
|    `user_id`    |    `uuid`     |  no  |                |                        Persona, 1:1 por perfil                         |
| `verificado_at` | `timestamptz` |  no  |    `now()`     | Última vez que la persona confirmó sus datos, por [`RF-P-13`][rf-p-13] |

- **Régimen:** [Mutable protegida][auditoria], rastreada
- **Índice común:** `idx_<perfil>_verificadoat`, para la revisión de perfiles
  desactualizados

`verificado_at` es de negocio y `updated_at` es técnico: el primero registra
cuándo la persona **confirmó** que sus datos siguen siendo correctos, con o sin
cambios; el segundo, cualquier escritura. Las matrices llevan la primera y la
DIEM la usa para saber qué expedientes revisar.

### `estudiante_profile`

El estudiante **de la UAM**. Un estudiante de otra institución es un
[`externo_profile`](#externo_profile) con ocupación `estudiante`.

|             Trigger              |              Evento               | Momento  | Nivel |                                Regla                                |        Origen        |
| :------------------------------: | :-------------------------------: | :------: | :---: | :-----------------------------------------------------------------: | :------------------: |
| `trg_estudianteprofile_dominio`  |       `INSERT`<br/>`UPDATE`       | `BEFORE` | `ROW` | El correo de la cuenta pertenece a `registro.dominio_institucional` | [`RF-P-03`][rf-p-03] |
| `trg_estudianteprofile_carrera`  |        `INSERT`, diferido         | `AFTER`  | `ROW` |           Exige al menos una fila en `estudiante_carrera`           | [`RF-P-08`][rf-p-08] |
| `trg_apiuser_email_domain_check` | `UPDATE OF email` sobre `ApiUser` | `BEFORE` | `ROW` |     Cambiar el correo de un estudiante UAM conserva el dominio      | [`RF-P-03`][rf-p-03] |

`trg_apiuser_email_domain_check` se declara en `rudi_profiles` y se registra
sobre la cuenta del template; su migración vive por eso en `api_auth`.

### `estudiante_carrera`

- **Volumen estimado:** 1,600-6,500 filas

|     Campo     |     Tipo      | Nulo | Predeterminado |                    Descripción                    |
| :-----------: | :-----------: | :--: | :------------: | :-----------------------------------------------: |
| `profile_id`  |    `uuid`     |  no  |                |          Perfil de estudiante, `CASCADE`          |
| `carrera_id`  |    `uuid`     |  no  |                |                    `RESTRICT`                     |
|    `nivel`    | `varchar(20)` |  no  |      `''`      |     `NivelesCarrera`: `primero` … `egresado`      |
|   `is_main`   |   `boolean`   |  no  |    `false`     |                                                   |
| `iniciada_en` |  `smallint`   |  sí  |                |                  Año de ingreso                   |
| `cerrada_at`  | `timestamptz` |  sí  |                | Nulo = la cursa; marca de cierre ([`D-09`][d-09]) |

|              Nombre               |                     Definición                      |             Propósito              |
| :-------------------------------: | :-------------------------------------------------: | :--------------------------------: |
|    `unq_estudiantecarrera_par`    |             `(profile_id, carrera_id)`              |                                    |
| `unq_estudiantecarrera_principal` | `(profile_id) WHERE cerrada_at IS NULL AND is_main` | Una sola carrera principal vigente |
|  `idx_estudiantecarrera_carrera`  |       `(carrera_id) WHERE cerrada_at IS NULL`       |    Reportes por carrera vigente    |

|             Trigger             |             Evento              | Momento  | Nivel |                      Regla                       |        Origen        |
| :-----------------------------: | :-----------------------------: | :------: | :---: | :----------------------------------------------: | :------------------: |
|  `trg_estudiantecarrera_nivel`  |      `INSERT`<br/>`UPDATE`      | `BEFORE` | `ROW` |   El nivel no supera la duración de la carrera   | [`RF-P-08`][rf-p-08] |
| `trg_estudiantecarrera_carrera` | `INSERT`<br/>`UPDATE`, diferido | `AFTER`  | `ROW` | El perfil conserva una carrera principal vigente | [`RF-P-09`][rf-p-09] |

`cerrada_at` distingue la carrera que el estudiante abandonó de la que sigue
cursando. Los reportes de participación por carrera usan la vigente al momento de
la participación, no la actual, y por eso la marca es temporal y no un booleano
([`D-17`][d-17]).

### `docente_profile`

`facultad_id` (opcional, `RESTRICT`), `nivel_academico` (`NivelesAcademicos` o
`''`) y `cargo`.

### `externo_profile`

|        Campo        |      Tipo      | Nulo | Predeterminado |                       Descripción                        |
| :-----------------: | :------------: | :--: | :------------: | :------------------------------------------------------: |
|  `institucion_id`   |     `uuid`     |  no  |                |                        `RESTRICT`                        |
|     `ocupacion`     | `varchar(30)`  |  no  |                | `estudiante` / `emprendedor` / `colaborador_empresa` / … |
| `ocupacion_detalle` |     `text`     |  no  |      `''`      |                   Hasta 500 caracteres                   |
|  `carrera_externa`  | `varchar(150)` |  no  |      `''`      |            Solo si `ocupacion = 'estudiante'`            |

El catálogo de carreras es institucional: la carrera de un estudiante de otra
universidad es texto libre.

### `mentor_profile`

|           Campo           |     Tipo      | Nulo | Predeterminado |                     Descripción                     |
| :-----------------------: | :-----------: | :--: | :------------: | :-------------------------------------------------: |
|     `tipo_mentor_id`      |    `uuid`     |  sí  |                |                     `RESTRICT`                      |
|      `municipio_id`       |    `uuid`     |  sí  |                |                     `RESTRICT`                      |
|     `nivel_academico`     | `varchar(20)` |  no  |      `''`      |                                                     |
|        `direccion`        |    `text`     |  no  |      `''`      |                                                     |
| `descripcion_profesional` |    `text`     |  no  |      `''`      |               Hasta 4,000 caracteres                |
|  `necesidades_formacion`  |    `text`     |  no  |      `''`      |               Hasta 2,000 caracteres                |
|      `confirmado_at`      | `timestamptz` |  sí  |                | Nulo = aspirante; coherente con `confirmado_por_id` |
|    `confirmado_por_id`    |    `uuid`     |  sí  |                |         Cuenta que lo confirmó, `RESTRICT`          |

|                   Índice                   |                            Definición                             |              Propósito               |
| :----------------------------------------: | :---------------------------------------------------------------: | :----------------------------------: |
|      `idx_mentorprofile_confirmadoat`      |         `(confirmado_at) WHERE confirmado_at IS NOT NULL`         |        Directorio de mentores        |
| `gin_mentorprofile_descripcionprofesional` | `(upper(unaccent(descripcion_profesional)) gin_trgm_ops)` parcial | Búsqueda por texto en la experiencia |

`confirmado_at` implementa la parte de [`RF-P-12`][rf-p-12] que impide
autonombrarse mentor. El perfil existe desde que la persona lo solicita, pero no
aparece como mentor disponible hasta que la DIEM lo confirma.

`mentor_area_experiencia` (`area_id`, `is_main`; una principal por mentor) y
`mentor_certificacion` (`nombre`, `institucion`, `year`, `enlace_url`;
`trg_mentorcertificacion_year` acota el año entre 1960 y el próximo) cuelgan del
perfil con `CASCADE`.

---

## Pendiente en este módulo

|             Tabla             |                                                 Para qué                                                  |
| :---------------------------: | :-------------------------------------------------------------------------------------------------------: |
|    `acceso_dato_personal`     | `append-only`: quién leyó o exportó datos personales de otra persona, en lugar de una `bitacora` genérica |
| Fusión de personas duplicadas |                        Servicio que traslada filas; ver [`rudi_user`](#rudi_user)                         |

[auditoria]: ../convenciones.md#auditoria-por-tabla
[catalogos-forma]: catalogos.md#forma-comun
[t-estado]: ../triggers.md#ciclo-de-vida-del-estado
[t-motivo]: ../triggers.md#motivo-de-lista-cerrada
[d-03]: ../decisiones.md#d-03
[d-04]: ../decisiones.md#d-04
[d-05]: ../decisiones.md#d-05
[d-08]: ../decisiones.md#d-08
[d-09]: ../decisiones.md#d-09
[d-12]: ../decisiones.md#d-12
[d-17]: ../decisiones.md#d-17
[d-19]: ../decisiones.md#d-19
[rf-a-05]: ../../requerimientos/funcionales/administracion.md#rf-a-05
[rf-a-06]: ../../requerimientos/funcionales/administracion.md#rf-a-06
[rf-a-07]: ../../requerimientos/funcionales/administracion.md#rf-a-07
[rf-a-09]: ../../requerimientos/funcionales/administracion.md#rf-a-09
[rf-a-10]: ../../requerimientos/funcionales/administracion.md#rf-a-10
[rf-a-11]: ../../requerimientos/funcionales/administracion.md#rf-a-11
[rf-a-12]: ../../requerimientos/funcionales/administracion.md#rf-a-12
[rf-a-13]: ../../requerimientos/funcionales/administracion.md#rf-a-13
[rf-a-50]: ../../requerimientos/funcionales/administracion.md#rf-a-50
[rf-p-01]: ../../requerimientos/funcionales/participantes.md#rf-p-01
[rf-p-02]: ../../requerimientos/funcionales/participantes.md#rf-p-02
[rf-p-03]: ../../requerimientos/funcionales/participantes.md#rf-p-03
[rf-p-05]: ../../requerimientos/funcionales/participantes.md#rf-p-05
[rf-p-06]: ../../requerimientos/funcionales/participantes.md#rf-p-06
[rf-p-07]: ../../requerimientos/funcionales/participantes.md#rf-p-07
[rf-p-08]: ../../requerimientos/funcionales/participantes.md#rf-p-08
[rf-p-09]: ../../requerimientos/funcionales/participantes.md#rf-p-09
[rf-p-10]: ../../requerimientos/funcionales/participantes.md#rf-p-10
[rf-p-11]: ../../requerimientos/funcionales/participantes.md#rf-p-11
[rf-p-12]: ../../requerimientos/funcionales/participantes.md#rf-p-12
[rf-p-13]: ../../requerimientos/funcionales/participantes.md#rf-p-13
[rn-01]: ../../requerimientos/reglas-negocio.md#rn-01
[rn-02]: ../../requerimientos/reglas-negocio.md#rn-02
[rn-03]: ../../requerimientos/reglas-negocio.md#rn-03
[rn-18]: ../../requerimientos/reglas-negocio.md#rn-18
