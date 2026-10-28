---
hide:
  - toc
icon: lucide/rotate-cw-fading-clock
---

# Procesos programados

Lo que el sistema hace sin que nadie lo pida. Cada proceso es una función de
servicio invocada por un comando de gestión programado, no un trigger, porque no
hay evento de escritura que lo dispare. Cada barrido se apoya en el índice que
declara la ficha de la tabla correspondiente, para no recorrerla completa en
cada corrida. El mecanismo de programación en sí (cron del sistema, Railway u
otro) no lo fija este documento.

Cada función vive en el `services.py` de su módulo y cada comando la envuelve
con un candado consultivo (`pglock.advisory`), para que dos corridas
solapadas no se pisen: la segunda se salta.

Ninguno de estos procesos valida nada por su cuenta. Cada uno fija el actor
(`set_actor('sistema')`), hace la escritura que le toca y los
[triggers][triggers] de la tabla imponen las reglas, igual que si la escritura
viniera de una petición: el cierre de una ventana mueve `estado_id` y
`trg_actividad_transicion_valida` comprueba que el par sea legal para el actor
`sistema`. Un proceso que tuviera que repetir esas comprobaciones sería un
segundo lugar donde la regla puede divergir.

|              Proceso               |  Frecuencia  |        Origen        |     Función de servicio      |         Comando          |         Índice de apoyo          |
| :--------------------------------: | :----------: | :------------------: | :--------------------------: | :----------------------: | :------------------------------: |
| Transicionar actividades por fecha |    Diaria    | [`RF-A-17`][rf-a-17] |  `transicionar_actividades`  | `transicionaractividades` |     `idx_actividad_catalogo`     |
|   Vencer propuestas de mentoría    |    Diaria    | [`RF-P-27`][rf-p-27] | `vencer_propuestas_mentoria` |    `vencerpropuestas`    | `idx_asignacionmentor_pendiente` |
|  Enviar notificaciones pendientes  |   Continua   | [`RF-P-06`][rf-p-06] |     `enviar_pendientes`      |  `enviarnotificaciones`  |   `idx_notificacion_pendiente`   |
|     Cerrar indicadores anuales     | A pedido[^1] | [`RF-A-45`][rf-a-45] |       `cerrar_periodo`       |  `cerrarperiodo <anio>`  |   `unq_indicadorperiodo_corte`   |
|   Limpiar la lista de revocación   |    Diaria    |       Template       |             n/a              |     `cleanblocklist`     |               n/a                |
|  Retener notificaciones antiguas   |   Mensual    | [`RF-A-50`][rf-a-50] |           n/a[^2]            |           n/a            |  `brin_notificacion_createdat`   |

[^1]:
    El cierre del año es una decisión de la Dirección, no una fecha. El
    comando existe para ejecutarla, no para programarla.

[^2]:
    La purga es un `DELETE` por lotes acotados sobre el rango que cubre el
    índice BRIN, no una función de dominio.

## Lo que no es un proceso programado

|                     Tentación                     |                                                Por qué no                                                 |
| :-----------------------------------------------: | :-------------------------------------------------------------------------------------------------------: |
| Validar participaciones al finalizar la actividad |      La validación es una afirmación de la DIEM; automatizarla vaciaría de sentido [`RN-07`][rn-07]       |
|      Fusionar duplicados por similitud alta       |           [`RF-A-07`][rf-a-07] los propone; fusionarlos es irreversible y lo decide una persona           |
|           Anonimizar cuentas inactivas            |                               La baja se solicita, no se deduce del desuso                                |
|       Promover la lista de espera por reloj       | Un lugar se libera por una escritura (cancelar, ampliar el cupo); la promueve el trigger de esa escritura |
|      Cerrar ventanas de inscripción por reloj     |  `trg_inscripcion_ventana_abierta` compara `inscripcion_cierra_at` al inscribir; no hay estado que mover  |
|    Expirar enlaces de verificación o sesiones     |          El template compara el vencimiento al leer el código o el token; no hay nada que barrer          |

[triggers]: triggers.md
[rf-a-07]: ../requerimientos/funcionales/administracion.md#rf-a-07
[rf-a-17]: ../requerimientos/funcionales/administracion.md#rf-a-17
[rf-a-45]: ../requerimientos/funcionales/administracion.md#rf-a-45
[rf-a-47]: ../requerimientos/funcionales/administracion.md#rf-a-47
[rf-a-50]: ../requerimientos/funcionales/administracion.md#rf-a-50
[rf-p-06]: ../requerimientos/funcionales/participantes.md#rf-p-06
[rf-p-27]: ../requerimientos/funcionales/participantes.md#rf-p-27
[rn-07]: ../requerimientos/reglas-negocio.md#rn-07
