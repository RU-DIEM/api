---
icon: lucide/mail
---

# Notificaciones

Una tabla en la app `rudi_notificaciones`: la cola de correos que envía el
sistema. Es lo que sobrevive de `auditoria.notificacion` del diseño original;
`bitacora` desaparece en favor de las tablas de eventos ([`D-15`][d-15]) y de
[`acceso_dato_personal`][acceso].

## Requerimientos cubiertos

- [`RF-P-04`][rf-p-04]
- [`RF-P-06`][rf-p-06]

---

## `notificacion`

Un correo renderizado desde una [`plantilla_mensaje`][plantilla], pendiente o
entregado.

- **Régimen:** [Mutable protegida][auditoria], **alto volumen**; sin tabla de
  eventos, porque la cola es su propio historial
- **Volumen estimado:** proporcional al tráfico
- **Origen:**
  > - [`RF-P-06`][rf-p-06]

### Columnas

|       Campo       |      Tipo      | Nulo | Predeterminado |                Descripción                |
| :---------------: | :------------: | :--: | :------------: | :---------------------------------------: |
|  `plantilla_id`   |     `uuid`     |  no  |                |         Plantilla que la originó          |
|    `cuenta_id`    |     `uuid`     |  sí  |                | Cuenta destinataria, si existe una cuenta |
|  `destinatario`   | `varchar(254)` |  no  |                |             Correo de destino             |
|     `asunto`      | `varchar(200)` |  no  |                |               Ya sustituido               |
|     `cuerpo`      |     `text`     |  no  |                |               Ya sustituido               |
| `programada_para` | `timestamptz`  |  no  |    `now()`     |    No se envía antes de este instante     |
|    `intentos`     |   `smallint`   |  no  |      `0`       |                                           |
|  `ultimo_error`   |     `text`     |  no  |      `''`      | Mensaje del proveedor en el último fallo  |
|   `enviada_at`    | `timestamptz`  |  sí  |                |           Desenlace: entregada            |
|  `descartada_at`  | `timestamptz`  |  sí  |                |     Desenlace: se dejó de reintentar      |

### Constraints

```postgresql
CONSTRAINT chk_notificacion_cuerpo
CHECK (length(cuerpo) >= 1)

CONSTRAINT chk_notificacion_desenlace_unico
CHECK (NOT (enviada_at IS NOT NULL AND descartada_at IS NOT NULL))

CONSTRAINT chk_notificacion_descarte_error
CHECK (descartada_at IS NULL OR ultimo_error <> '')
```

### Índices

|            Nombre             |                               Definición                               |           Propósito            |
| :---------------------------: | :--------------------------------------------------------------------: | :----------------------------: |
| `idx_notificacion_pendiente`  | `(programada_para) WHERE enviada_at IS NULL AND descartada_at IS NULL` | Barrido de `enviar_pendientes` |
| `brin_notificacion_createdat` |                       `(created_at) USING BRIN`                        |      Purga por retención       |

### Triggers

|         Nombre         |                              Evento                               | Momento  | Nivel |                 Regla                  |     Origen     |
| :--------------------: | :---------------------------------------------------------------: | :------: | :---: | :------------------------------------: | :------------: |
| `trg_readonly_mensaje` | `UPDATE OF asunto, cuerpo, cuenta_id, destinatario, plantilla_id` | `BEFORE` | `ROW` | Lo que se envió es lo que se renderizó | [`D-08`][d-08] |

### Notas de diseño

El correo no participa de la transacción ([`Triggers`][triggers-no]). El
servicio que hoy envía directamente (`send_plantilla`) pasará a encolar la fila
dentro de la transacción y enviarla al confirmarse (`on_commit`), dejando a
`enviar_pendientes` los reintentos. Así un fallo del proveedor nunca revierte la
escritura que pidió el correo, y ningún correo sale por una escritura que se
revirtió.

El mensaje se guarda ya sustituido y de solo lectura. Si la plantilla cambia
mañana, el registro sigue diciendo qué recibió la persona.

[acceso]: perfiles.md#acceso_dato_personal
[auditoria]: ../convenciones.md#auditoria-por-tabla
[plantilla]: catalogos.md#plantilla_mensaje
[triggers-no]: ../triggers.md#lo-que-no-es-trigger
[d-08]: ../decisiones.md#d-08
[d-15]: ../decisiones.md#d-15
[rf-p-04]: ../../requerimientos/funcionales/participantes.md#rf-p-04
[rf-p-06]: ../../requerimientos/funcionales/participantes.md#rf-p-06
