---
icon: lucide/user
---

# Identidad y acceso

Cuentas, identificadores, verificación, sesiones, consentimiento y fusión de
duplicados. Una sola tabla `usuario` sostiene a estudiantes, externos, docentes,
mentores y administradores por [decisión transversal][d-03]; lo que los
diferencia son los perfiles de [`Perfiles`][perfiles] y el rol de sistema.

Es el módulo central del proyecto. El problema que motiva el sistema no es
registrar personas: es reconocer que dos registros son la misma persona.

## Requerimientos cubiertos

- [`RF-P-01`][rf-p-01]
- [`RF-P-02`][rf-p-02]
- [`RF-P-03`][rf-p-03]
- [`RF-P-04`][rf-p-04]
- [`RF-P-05`][rf-p-05]
- [`RF-P-06`][rf-p-06]
- [`RF-P-07`][rf-p-07]
- [`RF-A-01`][rf-a-01]
- [`RF-A-02`][rf-a-02]
- [`RF-A-03`][rf-a-03]
- [`RF-A-05`][rf-a-05]
- [`RF-A-06`][rf-a-06]
- [`RF-A-07`][rf-a-07]
- [`RF-A-08`][rf-a-08]
- [`RF-A-09`][rf-a-09]

---

## `usuario`

Cuenta única de toda persona del sistema.

- **Régimen:** [Mutable rastreada][auditoria]
- **Volumen estimado:** 2,000-8,000 filas
- **Origen:**
  > - [`RF-P-01`][rf-p-01]
  > - [`RF-P-06`][rf-p-06]
  > - [`RF-A-05`][rf-a-05]

### Columnas

|           Campo           |      Tipo      | Nulo |  Predeterminado  |                       Descripción                       |
| :-----------------------: | :------------: | :--: | :--------------: | :-----------------------------------------------------: |
|         `nombres`         | `varchar(100)` |  no  |                  |           Conforme al documento de identidad            |
|        `apellidos`        | `varchar(100)` |  no  |                  |                                                         |
|     `nombre_completo`     | `varchar(201)` |  no  |     generada     |     **Almacenada**. Sostiene el índice de búsqueda      |
|    `fecha_nacimiento`     |     `date`     |  sí  |                  |        Nulo en registros importados sin el dato         |
|          `email`          | `varchar(254)` |  no  |                  |          Único por índice sobre `lower(email)`          |
|   `email_verificado_at`   | `timestamptz`  |  sí  |                  |                  Nulo = no verificado                   |
|      `telefono_pais`      |  `varchar(4)`  |  no  |     `'+505'`     |                                                         |
|     `telefono_numero`     |  `varchar(8)`  |  no  |       `''`       | Ocho dígitos sin separadores; es el número de WhatsApp  |
|         `sexo_id`         |     `uuid`     |  sí  |                  |                 Llave foránea a `sexo`                  |
|        `etnia_id`         |     `uuid`     |  sí  |                  |                 Llave foránea a `etnia`                 |
|        `talla_id`         |     `uuid`     |  sí  |                  |            Llave foránea a `talla_camiseta`             |
|      `password_hash`      | `varchar(128)` |  no  |       `''`       | Vacío = cuenta creada desde administración, sin activar |
| `password_actualizado_at` | `timestamptz`  |  sí  |                  |            Invalida las sesiones anteriores             |
|        `estado_id`        |     `uuid`     |  no  |                  |            Llave foránea a `estado_usuario`             |
|         `origen`          | `varchar(20)`  |  no  | `'autoservicio'` |    `autoservicio` / `administracion` / `importacion`    |
|    `ultimo_ingreso_at`    | `timestamptz`  |  sí  |                  |                                                         |
|     `fusionado_en_id`     |     `uuid`     |  sí  |                  |   Apunta al registro conservado si este fue absorbido   |
|     `anonimizado_at`      | `timestamptz`  |  sí  |                  |              Marca de cierre de la cuenta               |

### Columna generada

```postgresql
nombre_completo varchar(201)
GENERATED ALWAYS AS (nombres || ' ' || apellidos) STORED
```

Almacenada porque sostiene el índice trigramático de búsqueda por nombre y el
componente de nombre de la detección de duplicados de [`RF-A-07`][rf-a-07]. Una
columna virtual no puede indexarse.

### Llaves foráneas

|      Columna      |    Referencia    | `ON DELETE` |                        Notas                        |
| :---------------: | :--------------: | :---------: | :-------------------------------------------------: |
|    `estado_id`    | `estado_usuario` | `RESTRICT`  |                                                     |
|     `sexo_id`     |      `sexo`      | `RESTRICT`  |                                                     |
|    `etnia_id`     |     `etnia`      | `RESTRICT`  |                                                     |
|    `talla_id`     | `talla_camiseta` | `RESTRICT`  |                                                     |
| `fusionado_en_id` |    `usuario`     | `RESTRICT`  | Autorreferencia; el conservado no puede desaparecer |

### Constraints

```postgresql
CONSTRAINT chk_usuario_origen
CHECK (origen IN ('autoservicio', 'administracion', 'importacion'))

CONSTRAINT chk_usuario_telefono_formato
CHECK (
  telefono_numero = ''
  OR
  telefono_numero ~ '^[0-9]{8}$'
)

CONSTRAINT chk_usuario_pais_formato
CHECK (telefono_pais ~ '^\+[0-9]{1,3}$')

CONSTRAINT chk_usuario_nombre_longitud
CHECK (
  length(nombres) BETWEEN 1 AND 100
  AND
  length(apellidos) BETWEEN 1 AND 100
)

CONSTRAINT chk_usuario_verificacion_coherente
CHECK (email_verificado_at IS NULL OR length(email) > 0)

CONSTRAINT chk_usuario_nacimiento_razonable
CHECK (
  fecha_nacimiento IS NULL
  OR
  fecha_nacimiento BETWEEN DATE '1930-01-01' AND CURRENT_DATE - INTERVAL '14 years'
)

CONSTRAINT chk_usuario_fusion_no_reflexiva
CHECK (fusionado_en_id IS DISTINCT FROM id)
```

`chk_usuario_nacimiento_razonable` no valida la edad: rechaza el error de captura.
La cota inferior de catorce años proviene de que la DIEM no organiza actividades
para menores de esa edad, y la superior descarta el año tecleado con dos dígitos.
No es una regla de negocio sino una defensa contra el dato imposible.

### Unicidad

|       Nombre        |                  Definición                   |             Propósito              |
| :-----------------: | :-------------------------------------------: | :--------------------------------: |
| `unq_usuario_email` | `(lower(email)) WHERE anonimizado_at IS NULL` | Un correo identifica a una persona |

Parcial sobre las cuentas vivas: la anonimización sustituye el correo por un valor
irrepetible y no debe competir por el índice.

### Triggers

|               Nombre                |                Evento                | Momento  | Nivel |                                         Regla                                         |        Origen        |
| :---------------------------------: | :----------------------------------: | :------: | :---: | :-----------------------------------------------------------------------------------: | :------------------: |
|   `trg_usuario_estado_coherente`    |   `INSERT`, `UPDATE OF estado_id`    | `BEFORE` | `ROW` |  Verifica que las marcas temporales correspondan a los atributos del estado destino   |    [`D-09`][d-09]    |
|     `trg_usuario_perfil_minimo`     |        `UPDATE OF estado_id`         | `AFTER`  | `ROW` |            Aborta si una cuenta pasa a activa sin ningún perfil declarado             |   [`RN-03`][rn-03]   |
| `trg_usuario_dominio_institucional` |     `INSERT`, `UPDATE OF email`      | `BEFORE` | `ROW` | Si la persona tiene perfil de estudiante UAM, exige el dominio de `parametro_sistema` | [`RF-P-03`][rf-p-03] |
|   `trg_usuario_revocar_sesiones`    | `UPDATE OF password_hash, estado_id` | `AFTER`  | `ROW` |            Revoca las sesiones abiertas al cambiar contraseña o suspender             | [`RF-P-05`][rf-p-05] |
|       `trg_usuario_no_borrar`       |               `DELETE`               | `BEFORE` | `ROW` |                     Bloquea el borrado; la baja es anonimización                      | [`RF-A-50`][rf-a-50] |

### Índices

|             Nombre              |                                Definición                                |                          Propósito                          |
| :-----------------------------: | :----------------------------------------------------------------------: | :---------------------------------------------------------: |
|  `gin_usuario_nombrecompleto`   |                     `(nombre_completo gin_trgm_ops)`                     | Búsqueda por nombre y detección de duplicados por similitud |
| `idx_usuario_nacimiento_nombre` | `(fecha_nacimiento, nombre_completo) WHERE fecha_nacimiento IS NOT NULL` |          Segundo criterio de [`RF-A-07`][rf-a-07]           |
|     `idx_usuario_fusionado`     |          `(fusionado_en_id) WHERE fusionado_en_id IS NOT NULL`           |     Resolver el registro vivo de una persona absorbida      |
|      `idx_usuario_estado`       |                              `(estado_id)`                               |                    Filtro del directorio                    |

### Notas de diseño

`usuario` **no** tiene columnas `cif`, `cedula`, `tipo_usuario`, `carrera_id` ni
`puntos`. Cada una de esas ausencias es deliberada y está justificada en
[`D-04`][d-04], [`D-05`][d-05], [`D-17`][d-17] y [`D-12`][d-12] respectivamente.

La anonimización de [`RF-A-50`][rf-a-50] sustituye nombres, correo y teléfono por
valores irreversibles, fija `anonimizado_at` y conserva la fila. Las
participaciones siguen apuntando a ella y siguen contando en los agregados de los
años en que ocurrieron. Borrar la fila haría que los reportes de 2024 cambiaran
en 2027, que es exactamente lo que [`RN-18`][rn-18] prohíbe.

---

## `tipo_identificador`

Catálogo de los documentos que reconocen a una persona, con su patrón de
validación.

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 5 filas
- **Origen:**
  > - [`RF-A-09`][rf-a-09]

### Columnas

|       Campo        |      Tipo      | Nulo | Predeterminado |                             Descripción                             |
| :----------------: | :------------: | :--: | :------------: | :-----------------------------------------------------------------: |
|      `codigo`      | `varchar(50)`  |  no  |                | `cif`, `cedula`, `pasaporte`, `carnet_residencia`, `codigo_persona` |
|     `etiqueta`     | `varchar(60)`  |  no  |                |                    Nombre visible del documento                     |
|      `patron`      | `varchar(200)` |  no  |      `''`      |         Expresión regular; vacío = sin validación de forma          |
| `es_institucional` |   `boolean`    |  no  |    `false`     |           Lo emite la UAM; solo el CIF lo tiene verdadero           |
|   `admite_letra`   |   `boolean`    |  no  |    `false`     |              Afecta la normalización para comparación               |
|      `activo`      |   `boolean`    |  no  |     `true`     |                                                                     |

### Contenido previsto

|       Código        |                Patrón                 |                                 Notas                                 |
| :-----------------: | :-----------------------------------: | :-------------------------------------------------------------------: |
|        `cif`        |            `^[0-9]{5,10}$`            |            Identificador institucional del estudiante UAM             |
|      `cedula`       | `^[0-9]{3}-?[0-9]{6}-?[0-9]{4}[A-Z]$` |                 Cédula nicaragüense, con letra final                  |
|     `pasaporte`     |          `^[A-Z0-9]{6,12}$`           |          Participantes extranjeros del Rally Latinoamericano          |
| `carnet_residencia` |          `^[A-Z0-9]{6,14}$`           |                   Residentes extranjeros en el país                   |
|  `codigo_persona`   |                 `''`                  | Código único de persona del listado de mentores, sin formato conocido |

### Notas de diseño

El patrón se guarda como dato y no en el código porque el formato del CIF puede
cambiar cuando la Universidad cambie su numeración, y ese cambio no debe ser un
despliegue. Un identificador que no cumple el patrón se admite marcándolo como no
verificado, nunca se rechaza: los registros históricos de las matrices contienen
valores que ningún patrón actual reconoce y perderlos sería peor que admitirlos
señalados.

---

## `identificador_persona`

Documento que reconoce a una persona. Es la tabla que hace cumplir
[`RN-01`][rn-01] y [`RN-02`][rn-02].

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 3,000-12,000 filas
- **Origen:**
  > - [`RF-P-02`][rf-p-02]
  > - [`RF-A-09`][rf-a-09]

### Columnas

|        Campo        |     Tipo      | Nulo | Predeterminado |                     Descripción                     |
| :-----------------: | :-----------: | :--: | :------------: | :-------------------------------------------------: |
|    `usuario_id`     |    `uuid`     |  no  |                |                    Llave foránea                    |
|      `tipo_id`      |    `uuid`     |  no  |                |        Llave foránea a `tipo_identificador`         |
|       `valor`       | `varchar(20)` |  no  |                |     Tal como lo declaró la persona, con formato     |
| `valor_normalizado` | `varchar(20)` |  no  |    generada    | **Almacenada**. Mayúsculas, sin guiones ni espacios |
|   `es_principal`    |   `boolean`   |  no  |    `false`     |      El que la persona usa para identificarse       |
|   `verificado_at`   | `timestamptz` |  sí  |                |          Nulo = pendiente de verificación           |
|  `verificado_por`   |    `uuid`     |  sí  |                |        Llave foránea `RESTRICT` a `usuario`         |

### Columna generada

```postgresql
valor_normalizado varchar(20)
GENERATED ALWAYS AS (upper(regexp_replace(valor, '[^A-Za-z0-9]', '', 'g'))) STORED
```

Almacenada porque sostiene el índice único que garantiza la no duplicidad.
Sin ella, `001-150188-0001E` y `0011501880001E` serían dos personas distintas, y
las matrices existentes contienen ambas formas de escribir la misma cédula.

### Llaves foráneas

|     Columna      |      Referencia      | `ON DELETE` |                       Notas                        |
| :--------------: | :------------------: | :---------: | :------------------------------------------------: |
|   `usuario_id`   |      `usuario`       | `RESTRICT`  |            La fusión traslada, no borra            |
|    `tipo_id`     | `tipo_identificador` | `RESTRICT`  |                                                    |
| `verificado_por` |      `usuario`       | `RESTRICT`  | La bitácora debe seguir nombrando a quien verificó |

### Constraints

```postgresql
CONSTRAINT chk_identificadorpersona_verificacion_coherente
CHECK ((verificado_at IS NULL) = (verificado_por IS NULL))

CONSTRAINT chk_identificadorpersona_valor_longitud
CHECK (length(valor_normalizado) BETWEEN 4 AND 20)
```

### Unicidad

|                 Nombre                  |            Definición             |                    Propósito                     |
| :-------------------------------------: | :-------------------------------: | :----------------------------------------------: |
|    `unq_identificadorpersona_valor`     |  `(tipo_id, valor_normalizado)`   |  Un identificador pertenece a una sola persona   |
| `unq_identificadorpersona_tipo_persona` |      `(usuario_id, tipo_id)`      | Una persona tiene un solo documento de cada tipo |
|  `unq_identificadorpersona_principal`   | `(usuario_id) WHERE es_principal` |         Exactamente uno es el principal          |

### Triggers

|                   Nombre                    |           Evento            | Momento  |    Nivel    |                                                Regla                                                |        Origen        |
| :-----------------------------------------: | :-------------------------: | :------: | :---------: | :-------------------------------------------------------------------------------------------------: | :------------------: |
|      `trg_identificadorpersona_patron`      | `INSERT`, `UPDATE OF valor` | `BEFORE` |    `ROW`    | Lee `tipo_identificador.patron`; si no coincide, fuerza `verificado_at` a nulo en lugar de rechazar | [`RF-A-09`][rf-a-09] |
| `trg_identificadorpersona_principal_minimo` |     `UPDATE`, `DELETE`      | `AFTER`  | `STATEMENT` |                  Aborta si alguna persona activa queda sin identificador principal                  |   [`RN-01`][rn-01]   |
|    `trg_identificadorpersona_no_borrar`     |          `DELETE`           | `BEFORE` |    `ROW`    |                      Bloquea el borrado salvo desde el procedimiento de fusión                      | [`RF-A-50`][rf-a-50] |

### Notas de diseño

`unq_identificadorpersona_valor` es el invariante más importante del sistema. Es
la traducción exacta de [`RN-02`][rn-02] a un mecanismo que el motor garantiza
bajo concurrencia, y la razón por la que dos formularios simultáneos no pueden
crear dos registros de la misma persona.

El índice se declara sobre `(tipo_id, valor_normalizado)` y no solo sobre el
valor porque nada impide que un CIF y un pasaporte coincidan como cadena. Son
espacios de numeración independientes.

`trg_identificadorpersona_patron` **no rechaza** el valor que incumple el patrón:
lo admite sin verificar. Es una decisión consciente sobre la migración. Las
matrices existentes tienen cédulas incompletas y CIF con caracteres extraños, y
un modelo que las rechace obliga a limpiar tres mil filas antes de poder usar el
sistema, lo que en la práctica significa que el sistema no se usa.

---

## `codigo_verificacion`

Enlaces de un solo uso para verificar correo, recuperar acceso e invitar cuentas
administrativas.

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 5,000-20,000 filas
- **Origen:**
  > - [`RF-P-04`][rf-p-04]
  > - [`RF-P-05`][rf-p-05]
  > - [`RF-A-01`][rf-a-01]

### Columnas

|      Campo      |      Tipo      | Nulo |                           Descripción                           |
| :-------------: | :------------: | :--: | :-------------------------------------------------------------: |
|  `usuario_id`   |     `uuid`     |  sí  | Nulo en la invitación administrativa a un correo aún sin cuenta |
|     `email`     | `varchar(254)` |  no  |                     Destinatario del enlace                     |
|   `proposito`   | `varchar(30)`  |  no  |                           Ver `CHECK`                           |
|  `token_hash`   | `varchar(128)` |  no  |        Único. El token en claro solo viaja en el correo         |
|   `expira_at`   | `timestamptz`  |  no  |               Según el parámetro correspondiente                |
| `consumido_at`  | `timestamptz`  |  sí  |                      Marca de un solo uso                       |
| `invalidado_at` | `timestamptz`  |  sí  |    Lo fija la emisión de un enlace nuevo del mismo propósito    |
|  `emitido_por`  |     `uuid`     |  sí  |         Con valor solo en la invitación administrativa          |

### Constraints

```postgresql
CONSTRAINT chk_codigoverificacion_proposito
CHECK (
  proposito IN (
    'verificacion_email',
    'recuperacion_password',
    'invitacion_administrativa'
  )
)

CONSTRAINT chk_codigoverificacion_vigencia
CHECK (expira_at > created_at)

CONSTRAINT chk_codigoverificacion_desenlace_unico
CHECK (num_nonnulls(consumido_at, invalidado_at) <= 1)

CONSTRAINT chk_codigoverificacion_invitacion
CHECK (
  proposito <> 'invitacion_administrativa'
  OR
  emitido_por IS NOT NULL
)
```

### Unicidad

|             Nombre             |                                    Definición                                    |                  Propósito                   |
| :----------------------------: | :------------------------------------------------------------------------------: | :------------------------------------------: |
| `unq_codigoverificacion_token` |                                  `(token_hash)`                                  |      Un token identifica un solo enlace      |
| `unq_codigoverificacion_vivo`  | `(lower(email), proposito) WHERE consumido_at IS NULL AND invalidado_at IS NULL` | No se acumulan enlaces vivos al mismo correo |

### Índices

|               Nombre                |                             Definición                             |       Propósito        |
| :---------------------------------: | :----------------------------------------------------------------: | :--------------------: |
| `idx_codigoverificacion_expiracion` | `(expira_at) WHERE consumido_at IS NULL AND invalidado_at IS NULL` | Barrido de vencimiento |

### Notas de diseño

`token_hash` y no `token`: si la base se filtra, quien tenga la tabla completa no
puede canjear ningún enlace pendiente.

`unq_codigoverificacion_vivo` implementa el reenvío correctamente. Pedir el
enlace tres veces no produce tres enlaces válidos: el segundo invalida al primero.
Sin esta restricción, un enlace antiguo interceptado seguiría sirviendo días
después.

---

## `sesion`

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 500-3,000 filas vivas
- **Origen:**
  > - [`RF-A-02`][rf-a-02]
  > - [`RF-P-05`][rf-p-05]

### Columnas

|      Campo      |      Tipo      | Nulo |              Descripción               |
| :-------------: | :------------: | :--: | :------------------------------------: |
|  `usuario_id`   |     `uuid`     |  no  |             Llave foránea              |
|  `token_hash`   | `varchar(128)` |  no  |                 Único                  |
|    `ambito`     | `varchar(20)`  |  no  |   `participante` / `administracion`    |
|   `expira_at`   | `timestamptz`  |  no  |     Según el parámetro del ámbito      |
| `ultimo_uso_at` | `timestamptz`  |  no  | Sostiene la expiración por inactividad |
|  `revocada_at`  | `timestamptz`  |  sí  |            Marca de cierre             |
|      `ip`       |     `inet`     |  sí  |                                        |
|  `user_agent`   | `varchar(300)` |  no  |                  `''`                  |

### Constraints

```postgresql
CONSTRAINT chk_sesion_ambito
CHECK (ambito IN ('participante', 'administracion'))

CONSTRAINT chk_sesion_vigencia
CHECK (expira_at > created_at)
```

### Índices

|          Nombre           |                    Definición                    |                Propósito                |
| :-----------------------: | :----------------------------------------------: | :-------------------------------------: |
|    `unq_sesion_token`     |                  `(token_hash)`                  |          Resolución de sesión           |
| `idx_sesion_usuario_viva` | `(usuario_id, ambito) WHERE revocada_at IS NULL` | Revocación masiva al cambiar contraseña |

### Notas de diseño

`ambito` es discriminador y no estado: una sesión nace con su ámbito y no cambia.
Es lo que impide que una sesión abierta en el portal del participante sirva para
el panel administrativo aunque la persona tenga ambos accesos, tal como exige
[`RF-A-01`][rf-a-01].

---

## `intento_acceso`

- **Régimen:** [`append-only`][auditoria], **alto volumen**
- **Volumen estimado:** crece con el tráfico
- **Origen:**
  > - [`RF-A-02`][rf-a-02]

### Columnas

|      Campo      |      Tipo      | Nulo |                   Descripción                    |
| :-------------: | :------------: | :--: | :----------------------------------------------: |
| `identificador` | `varchar(254)` |  no  |     Lo tecleado, sea correo o identificador      |
|  `usuario_id`   |     `uuid`     |  sí  |   Nulo si el identificador no resolvió a nadie   |
|    `ambito`     | `varchar(20)`  |  no  |        `participante` / `administracion`         |
|    `exitoso`    |   `boolean`    |  no  |                                                  |
|    `motivo`     | `varchar(40)`  |  no  | `''` si fue exitoso; si no, la causa del rechazo |
|      `ip`       |     `inet`     |  sí  |                                                  |

### Índices

|              Nombre               |                         Definición                          |            Propósito             |
| :-------------------------------: | :---------------------------------------------------------: | :------------------------------: |
| `idx_intentoacceso_identificador` | `(lower(identificador), created_at DESC) WHERE NOT exitoso` | Conteo de fallos para el bloqueo |
|   `brin_intentoacceso_created`    |                  `(created_at) USING BRIN`                  |       Barrido de retención       |

Se guarda el identificador tecleado y no solo el `usuario_id` resuelto, porque el
caso que interesa vigilar es precisamente aquel en el que no resuelve: alguien
probando identificadores contra el panel.

---

## `politica_privacidad`

Versiones del aviso de privacidad que la persona acepta.

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 2-5 filas
- **Origen:**
  > - [`RF-P-07`][rf-p-07]

### Columnas

|      Campo      |      Tipo      | Nulo |         Descripción         |
| :-------------: | :------------: | :--: | :-------------------------: |
|    `version`    | `varchar(20)`  |  no  |     Única. `1.0`, `1.1`     |
|    `titulo`     | `varchar(200)` |  no  |                             |
|     `texto`     |     `text`     |  no  | Contenido íntegro del aviso |
| `vigente_desde` |     `date`     |  no  |                             |
| `vigente_hasta` |     `date`     |  sí  |   Nulo = versión vigente    |

### Unicidad

|              Nombre              |               Definición               |             Propósito             |
| :------------------------------: | :------------------------------------: | :-------------------------------: |
| `unq_politicaprivacidad_version` |              `(version)`               |                                   |
| `unq_politicaprivacidad_vigente` | `((true)) WHERE vigente_hasta IS NULL` | Una sola versión vigente a la vez |

Guardar el texto completo y no solo la versión es lo que permite mostrar años
después qué aceptó exactamente una persona. Una referencia a un documento externo
que puede editarse no prueba nada.

---

## `consentimiento_datos`

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** una fila por persona
- **Origen:**
  > - [`RF-P-07`][rf-p-07]
  > - [`RN-17`][rn-17]

### Columnas

|      Campo      |      Tipo      | Nulo |                  Descripción                   |
| :-------------: | :------------: | :--: | :--------------------------------------------: |
|  `usuario_id`   |     `uuid`     |  no  |                 Llave foránea                  |
|  `politica_id`  |     `uuid`     |  no  |          Versión concreta que aceptó           |
|   `estado_id`   |     `uuid`     |  no  |    Llave foránea a `estado_consentimiento`     |
|  `otorgado_at`  | `timestamptz`  |  sí  |                                                |
|  `retirado_at`  | `timestamptz`  |  sí  |                                                |
|     `canal`     | `varchar(20)`  |  no  | `portal` / `formulario_fisico` / `importacion` |
| `evidencia_url` | `varchar(500)` |  no  |  `''`; enlace al formulario firmado si lo hay  |

### Constraints

```postgresql
CONSTRAINT chk_consentimientodatos_canal
CHECK (canal IN ('portal', 'formulario_fisico', 'importacion'))

CONSTRAINT chk_consentimientodatos_retiro
CHECK (retirado_at IS NULL OR otorgado_at IS NOT NULL)
```

### Unicidad

|              Nombre               |   Definición   |               Propósito               |
| :-------------------------------: | :------------: | :-----------------------------------: |
| `unq_consentimientodatos_usuario` | `(usuario_id)` | Un consentimiento vigente por persona |

### Notas de diseño

El campo _autorización para tratamiento de datos_ de la matriz de estudiantes
tiene tres valores y la propia matriz advierte que no sustituye al aviso de
privacidad. Este par de tablas es esa advertencia convertida en modelo: el estado
dice si hay autorización, `politica_id` dice a qué texto se autorizó.

Las filas importadas nacen con estado `pendiente_verificar` y canal
`importacion`, que es la verdad sobre ellas: la DIEM cree que esas personas
autorizaron, pero el sistema no tiene la evidencia.

El historial de cambios de consentimiento vive en la tabla de eventos gemela del
régimen protegido, no en filas adicionales aquí. Una persona tiene un
consentimiento vigente, no una colección.

---

## `rol_sistema` y `usuario_rol`

Autorización interna. Dos tablas mínimas que el piloto puebla con un solo rol.

- **Régimen:** [Mutable protegida][auditoria]
- **Volumen estimado:** 2 y ~5 filas
- **Origen:**
  > - [`RF-A-03`][rf-a-03]

### `rol_sistema`

|    Campo     |     Tipo      | Nulo | Predeterminado |            Descripción            |
| :----------: | :-----------: | :--: | :------------: | :-------------------------------: |
|   `codigo`   | `varchar(50)` |  no  |                |  `administrador`, `participante`  |
|  `etiqueta`  | `varchar(60)` |  no  |                |                                   |
| `es_interno` |   `boolean`   |  no  |    `false`     | Da acceso al panel administrativo |
|   `activo`   |   `boolean`   |  no  |     `true`     |                                   |

### `usuario_rol`

|     Campo      |     Tipo      | Nulo |                    Descripción                    |
| :------------: | :-----------: | :--: | :-----------------------------------------------: |
|  `usuario_id`  |    `uuid`     |  no  |                   Llave foránea                   |
|    `rol_id`    |    `uuid`     |  no  |                   Llave foránea                   |
| `otorgado_por` |    `uuid`     |  sí  | Nulo en el rol de participante, que es automático |
| `revocado_at`  | `timestamptz` |  sí  |                  Marca de cierre                  |

### Unicidad

|          Nombre          |                    Definición                    |           Propósito           |
| :----------------------: | :----------------------------------------------: | :---------------------------: |
| `unq_usuariorol_vigente` | `(usuario_id, rol_id) WHERE revocado_at IS NULL` | Un rol no se otorga dos veces |

### Triggers

|             Nombre              |       Evento       | Momento |    Nivel    |                                  Regla                                   |        Origen        |
| :-----------------------------: | :----------------: | :-----: | :---------: | :----------------------------------------------------------------------: | :------------------: |
| `trg_usuariorol_minimo_interno` | `UPDATE`, `DELETE` | `AFTER` | `STATEMENT` | Aborta si la operación dejaría el sistema sin ningún rol interno vigente | [`RF-A-03`][rf-a-03] |

### Notas de diseño

Dos tablas para dos roles parece desproporcionado y lo es hoy. Existen porque
[`RF-A-03`][rf-a-03] declara la separación de funciones como restricción del
piloto y no como propiedad del dominio, y porque la alternativa —un booleano
`es_admin` en `usuario`— convierte esa separación futura en una migración con
reescritura de toda la capa de autorización. El costo actual es de dos tablas de
menos de diez filas.

`trg_usuariorol_minimo_interno` es de nivel `STATEMENT` y no `ROW` porque la
operación peligrosa es la que revoca varias filas a la vez: comprobar fila por
fila dejaría pasar el `UPDATE` que revoca a los dos únicos administradores.

---

## `fusion_usuario`

Registro de las fusiones de duplicados. Es lo que hace que [`RN-02`][rn-02] sea
reparable y no solo prevenible.

- **Régimen:** [`append-only`][auditoria]
- **Volumen estimado:** decenas a cientos de filas
- **Origen:**
  > - [`RF-A-08`][rf-a-08]

### Columnas

|          Campo          |  Tipo   | Nulo |                        Descripción                         |
| :---------------------: | :-----: | :--: | :--------------------------------------------------------: |
| `usuario_conservado_id` | `uuid`  |  no  |                 El registro que sigue vivo                 |
| `usuario_absorbido_id`  | `uuid`  |  no  |             El que queda apuntando al anterior             |
|       `motivo_id`       | `uuid`  |  no  |        Llave foránea a `motivo` de ámbito de fusión        |
|         `nota`          | `text`  |  no  |                            `''`                            |
|     `ejecutada_por`     | `uuid`  |  no  |            Llave foránea `RESTRICT` a `usuario`            |
|        `resumen`        | `jsonb` |  no  | Conteo por entidad de lo trasladado, congelado al ejecutar |

### Constraints

```postgresql
CONSTRAINT chk_fusionusuario_distintos
CHECK (usuario_conservado_id <> usuario_absorbido_id)

CONSTRAINT chk_fusionusuario_resumen_objeto
CHECK (jsonb_typeof(resumen) = 'object')
```

### Unicidad

|            Nombre             |        Definición        |              Propósito              |
| :---------------------------: | :----------------------: | :---------------------------------: |
| `unq_fusionusuario_absorbido` | `(usuario_absorbido_id)` | Un registro se absorbe una sola vez |

### Índices

|             Nombre             |        Definición         |              Propósito               |
| :----------------------------: | :-----------------------: | :----------------------------------: |
| `idx_fusionusuario_conservado` | `(usuario_conservado_id)` | Historial de fusiones de una persona |

### Notas de diseño

`resumen` congela cuántas inscripciones, participaciones, puntos y constancias se
trasladaron. Es la única prueba de qué contenía el registro absorbido, porque
después de la fusión su contenido ya está en el conservado y no hay forma de
distinguir qué vino de dónde.

No hay operación de deshacer. La fusión traslada llaves foráneas y revertirla
exige saber cuáles eran del absorbido, que es justo lo que `resumen` cuenta pero
no identifica. Guardar el detalle completo sería posible y se descartó por
proporción: las fusiones son decenas al año y una reversión es un incidente
manual documentado. Ver [`R-04`][r-04].

`unq_fusionusuario_absorbido` impide la cadena de fusiones sobre el mismo
registro. Fusionar A en B y luego B en C es válido; fusionar A en B dos veces, no.

[auditoria]: ../convenciones.md#auditoria-por-tabla
[d-03]: ../decisiones.md#d-03
[d-04]: ../decisiones.md#d-04
[d-05]: ../decisiones.md#d-05
[d-09]: ../decisiones.md#d-09
[d-12]: ../decisiones.md#d-12
[d-17]: ../decisiones.md#d-17
[perfiles]: perfiles.md
[r-04]: ../riesgos.md#r-04
[rf-a-01]: ../../requerimientos/funcionales/administracion.md#rf-a-01
[rf-a-02]: ../../requerimientos/funcionales/administracion.md#rf-a-02
[rf-a-03]: ../../requerimientos/funcionales/administracion.md#rf-a-03
[rf-a-05]: ../../requerimientos/funcionales/administracion.md#rf-a-05
[rf-a-06]: ../../requerimientos/funcionales/administracion.md#rf-a-06
[rf-a-07]: ../../requerimientos/funcionales/administracion.md#rf-a-07
[rf-a-08]: ../../requerimientos/funcionales/administracion.md#rf-a-08
[rf-a-09]: ../../requerimientos/funcionales/administracion.md#rf-a-09
[rf-a-50]: ../../requerimientos/funcionales/administracion.md#rf-a-50
[rf-p-01]: ../../requerimientos/funcionales/participantes.md#rf-p-01
[rf-p-02]: ../../requerimientos/funcionales/participantes.md#rf-p-02
[rf-p-03]: ../../requerimientos/funcionales/participantes.md#rf-p-03
[rf-p-04]: ../../requerimientos/funcionales/participantes.md#rf-p-04
[rf-p-05]: ../../requerimientos/funcionales/participantes.md#rf-p-05
[rf-p-06]: ../../requerimientos/funcionales/participantes.md#rf-p-06
[rf-p-07]: ../../requerimientos/funcionales/participantes.md#rf-p-07
[rn-01]: ../../requerimientos/reglas-negocio.md#rn-01
[rn-02]: ../../requerimientos/reglas-negocio.md#rn-02
[rn-03]: ../../requerimientos/reglas-negocio.md#rn-03
[rn-17]: ../../requerimientos/reglas-negocio.md#rn-17
[rn-18]: ../../requerimientos/reglas-negocio.md#rn-18
