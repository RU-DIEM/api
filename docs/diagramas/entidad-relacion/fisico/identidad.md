---
icon: lucide/fingerprint
---

# Identidad

Once tablas. Es el módulo más denso del modelo y el que sostiene la regla que
motivó el proyecto.

```mermaid
---
config:
  elk:
    nodePlacementStrategy: NETWORK_SIMPLEX
  fontFamily: monospace
  layout: elk
---
erDiagram
  usuario {
    uuid         id                  PK
    varchar      nombres
    varchar      apellidos
    varchar      nombre_completo     UK
    date         fecha_nacimiento
    varchar      email               UK
    timestamptz  email_verificado_at
    varchar      telefono_numero
    uuid         sexo_id             FK
    uuid         etnia_id            FK
    uuid         talla_id            FK
    varchar      password_hash
    uuid         estado_id           FK
    varchar      origen
    uuid         fusionado_en_id     FK
    timestamptz  anonimizado_at
  }
  tipo_identificador {
    uuid         id                PK
    varchar      codigo            UK
    varchar      etiqueta
    varchar      patron
    boolean      es_institucional
    boolean      admite_letra
  }
  identificador_persona {
    uuid         id                 PK
    uuid         usuario_id         FK
    uuid         tipo_id            FK
    varchar      valor
    varchar      valor_normalizado  UK
    boolean      es_principal
    timestamptz  verificado_at
    uuid         verificado_por     FK
  }
  codigo_verificacion {
    uuid         id             PK
    uuid         usuario_id     FK
    varchar      email
    varchar      proposito
    varchar      token_hash     UK
    timestamptz  expira_at
    timestamptz  consumido_at
    uuid         emitido_por    FK
  }
  sesion {
    uuid         id             PK
    uuid         usuario_id     FK
    varchar      token_hash     UK
    varchar      ambito
    timestamptz  expira_at
    timestamptz  ultimo_uso_at
    timestamptz  revocada_at
    inet         ip
  }
  intento_acceso {
    uuid         id             PK
    varchar      identificador
    uuid         usuario_id     FK
    boolean      exitoso
    varchar      motivo
    inet         ip
  }
  politica_privacidad {
    uuid         id             PK
    varchar      version        UK
    varchar      titulo
    text         texto
    date         vigente_desde
    date         vigente_hasta
  }
  consentimiento_datos {
    uuid         id             PK
    uuid         usuario_id     UK
    uuid         politica_id    FK
    uuid         estado_id      FK
    timestamptz  otorgado_at
    timestamptz  retirado_at
    varchar      canal
  }
  rol_sistema {
    uuid         id          PK
    varchar      codigo      UK
    varchar      etiqueta
    boolean      es_interno
  }
  usuario_rol {
    uuid         id            PK
    uuid         usuario_id    UK
    uuid         rol_id        UK
    uuid         otorgado_por  FK
    timestamptz  revocado_at
  }
  fusion_usuario {
    uuid         id                     PK
    uuid         usuario_conservado_id  FK
    uuid         usuario_absorbido_id   FK
    uuid         motivo_id              FK
    uuid         ejecutada_por          FK
    jsonb        resumen
  }

  usuario              ||--|{ identificador_persona : ""
  tipo_identificador   ||--o{ identificador_persona : ""
  usuario              ||--o{ codigo_verificacion   : ""
  usuario              ||--o{ sesion                : ""
  usuario              ||--o{ intento_acceso        : ""
  usuario              ||--o| consentimiento_datos  : ""
  politica_privacidad  ||--o{ consentimiento_datos  : ""
  usuario              ||--o{ usuario_rol           : ""
  rol_sistema          ||--o{ usuario_rol           : ""
  usuario              ||--o| usuario               : "fusionado_en_id"
  usuario              ||--o{ fusion_usuario        : ""
```

---

## Las restricciones que el diagrama no muestra

|             Restricción              |                                         Qué garantiza                                          |
| :----------------------------------: | :--------------------------------------------------------------------------------------------: |
|   `unq_identificadorpersona_valor`   | Sobre `(tipo_id, valor_normalizado)`. Un CIF pertenece a una sola persona: es [`RN-02`][rn-02] |
| `unq_identificadorpersona_principal` |                      Índice parcial `WHERE es_principal`. Uno y solo uno                       |
|         `unq_usuario_email`          |                  Sobre `lower(email)`, parcial `WHERE anonimizado_at IS NULL`                  |
|   `unq_politicaprivacidad_vigente`   |                  `((true)) WHERE vigente_hasta IS NULL`. Una versión vigente                   |
|       `unq_usuariorol_vigente`       |                              Parcial `WHERE revocado_at IS NULL`                               |

---

## Notas del nivel físico

**`valor_normalizado` es columna generada y almacenada.** Convierte a mayúsculas
y elimina guiones y espacios, de modo que `001-120500-1000X` y `0011205001000X`
colisionen en el índice único. Sin la normalización, la regla de no duplicados se
esquivaría con un guion.

**`nombre_completo` también es generada**, y sostiene el índice trigram que
permite la detección de duplicados por similitud. Concatenar en la consulta
impediría usar índice.

**`fusionado_en_id` es autorreferencia con `RESTRICT`.** El registro conservado
nunca puede desaparecer mientras alguien lo apunte, que es lo que mantiene
resolubles los enlaces antiguos.

**`intento_acceso.identificador` guarda lo tecleado y no solo el `usuario_id`
resuelto.** El caso que interesa vigilar es precisamente aquel en que no
resuelve: alguien probando identificadores contra el panel.

**`fusion_usuario` tiene dos llaves foráneas a `usuario`** y ambas con
`RESTRICT`. El par es ordenado: invertirlo cambiaría quién absorbió a quién.

[rn-02]: ../../../requerimientos/reglas-negocio.md#rn-02
