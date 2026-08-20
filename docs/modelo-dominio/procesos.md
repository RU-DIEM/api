---
icon: lucide/timer
---

# Procesos programados

Lo que el sistema hace sin que nadie lo pida. Ocho procesos, cada uno con la
frecuencia con que corre, el requerimiento que lo obliga y el índice que lo
sostiene.

Ninguno inventa información: todos aplican una consecuencia que ya estaba
declarada en los datos y que solo esperaba a que pasara el tiempo.

---

## Inventario

|                Proceso                 |          Frecuencia          |                                          Qué hace                                           |        Origen        |           Índice de apoyo           |
| :------------------------------------: | :--------------------------: | :-----------------------------------------------------------------------------------------: | :------------------: | :---------------------------------: |
|   **Cerrar ventana de inscripción**    |         Cada 15 min          |     Marca las actividades cuya `inscripcion_cierra_at` ya pasó y deja de admitir altas      | [`RF-A-18`][rf-a-18] |   `idx_actividad_ventana_cierre`    |
| **Transicionar actividades por fecha** |            Diaria            | Publicada => en curso al llegar `fecha_inicio`; en curso => finalizada al pasar `fecha_fin` | [`RF-A-17`][rf-a-17] |      `idx_actividad_catalogo`       |
|      **Promover lista de espera**      |         Cada 15 min          |          Ocupa los lugares liberados por cancelaciones y notifica a quien asciende          | [`RF-P-18`][rf-p-18] |      `idx_inscripcion_espera`       |
|   **Vencer propuestas de mentoría**    |            Diaria            |             Marca como vencidas las asignaciones sin respuesta pasado el plazo              | [`RF-P-27`][rf-p-27] |  `idx_asignacionmentor_pendiente`   |
|          **Expirar enlaces**           |           Horaria            |                Invalida los códigos de verificación e invitaciones caducados                | [`RF-P-04`][rf-p-04] | `idx_codigoverificacion_expiracion` |
|     **Cerrar sesiones inactivas**      |           Horaria            |                  Revoca las sesiones que superaron el plazo de inactividad                  | [`RF-P-05`][rf-p-05] |       `idx_sesion_expiracion`       |
|  **Marcar perfiles desactualizados**   |           Semanal            |      Señala los perfiles sin confirmar vigencia más allá del parámetro correspondiente      | [`RF-P-13`][rf-p-13] |      `idx_perfil_actualizado`       |
|    **Despachar la cola de correo**     |          Cada 5 min          |                Envía las notificaciones pendientes y reintenta las fallidas                 | [`RF-P-06`][rf-p-06] |    `idx_notificacion_pendiente`     |
|  **Refrescar vistas materializadas**   | Ver [`Analítica`][analitica] |                     `REFRESH ... CONCURRENTLY` sobre las cuatro vistas                      | [`RF-A-47`][rf-a-47] |     Índice único de cada vista      |
|        **Purgar por retención**        |           Mensual            |  Elimina intentos de acceso, sesiones revocadas y notificaciones más antiguas que el plazo  | [`RF-A-50`][rf-a-50] |     Índices BRIN de cada tabla      |

---

## Reglas comunes

Todos los procesos comparten cinco condiciones.

!!! example "**Contrato de los procesos programados**"

    === "**Actor**"

        Escriben en `bitacora` con `actor_tipo = 'sistema'` y `actor_id` nulo. Lo
        que hace el reloj se distingue de lo que hace una persona, y esa
        distinción es la que permite responder si una participación se cerró
        sola o alguien la cerró.

    === "**Idempotencia**"

        Correr dos veces produce el mismo resultado que correr una. Todos filtran
        por la marca temporal que ellos mismos fijan, de modo que la segunda
        pasada no encuentra nada que hacer.

    === "**Transiciones legales**"

        Ninguno escribe un estado directamente: pasan por el mismo trigger de
        coherencia que la interfaz, contra `transicion_<entidad>` con
        `actor_tipo = 'sistema'`. Un proceso no puede hacer lo que un
        administrador no podría hacer.

    === "**Fallo parcial**"

        Procesan por lotes con transacción por lote. Una actividad que falla no
        detiene a las demás; el fallo queda en `bitacora` con
        `resultado = 'error'`.

    === "**Sin borrado del dominio**"

        La purga solo toca tablas operativas: intentos de acceso, sesiones
        revocadas y notificaciones enviadas. Participaciones, puntos,
        constancias, bitácora e indicadores cerrados están fuera de su alcance
        por [`RF-A-50`][rf-a-50].

---

## El único proceso que decide

Siete de los ocho aplican el paso del tiempo. **Promover lista de espera** es el
único que toma una decisión con consecuencias para una persona: elige a quién le
toca el lugar liberado.

El criterio es `posicion_espera` y solo `posicion_espera`. No hay ponderación por
perfil, por facultad ni por historial, y el índice único
`unq_inscripcion_posicion_espera` impide los empates que obligarían a desempatar
con un criterio no declarado.

La promoción notifica y **no confirma**: la persona que asciende pasa a
`pendiente` y dispone de un plazo para confirmar. Ascender a alguien directamente
a confirmada llenaría los cupos con personas que ya no pueden asistir, que es el
modo en que las listas de espera dejan de servir.

---

## Lo que no es un proceso programado

|                     Tentación                     |                                           Por qué no                                           |
| :-----------------------------------------------: | :--------------------------------------------------------------------------------------------: |
|           Cerrar el año automáticamente           |        El cierre de [`RF-A-45`][rf-a-45] es una decisión de la Dirección, no una fecha         |
| Validar participaciones al finalizar la actividad | La validación es una afirmación de la DIEM; automatizarla vaciaría de sentido [`RN-07`][rn-07] |
|      Fusionar duplicados por similitud alta       |     [`RF-A-07`][rf-a-07] los propone; fusionarlos es irreversible y lo decide una persona      |
|           Anonimizar cuentas inactivas            |                          La baja se solicita, no se deduce del desuso                          |

[analitica]: modulos/analitica.md#regimen-de-refresco
[rf-a-07]: ../requerimientos/funcionales/administracion.md#rf-a-07
[rf-a-17]: ../requerimientos/funcionales/administracion.md#rf-a-17
[rf-a-18]: ../requerimientos/funcionales/administracion.md#rf-a-18
[rf-a-45]: ../requerimientos/funcionales/administracion.md#rf-a-45
[rf-a-47]: ../requerimientos/funcionales/administracion.md#rf-a-47
[rf-a-50]: ../requerimientos/funcionales/administracion.md#rf-a-50
[rf-p-04]: ../requerimientos/funcionales/participantes.md#rf-p-04
[rf-p-05]: ../requerimientos/funcionales/participantes.md#rf-p-05
[rf-p-06]: ../requerimientos/funcionales/participantes.md#rf-p-06
[rf-p-13]: ../requerimientos/funcionales/participantes.md#rf-p-13
[rf-p-18]: ../requerimientos/funcionales/participantes.md#rf-p-18
[rf-p-27]: ../requerimientos/funcionales/participantes.md#rf-p-27
[rn-07]: ../requerimientos/reglas-negocio.md#rn-07
