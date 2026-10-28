---
icon: lucide/scaling
---

# Alcance

Detrás del discurso de plataforma de gestión, el sistema es un **registro de
identidad con historial de eventos**. Todo el modelo gira alrededor de una sola
pregunta que la DIEM hoy no puede responder: cuántas personas distintas
participaron este año. Las inscripciones, los puntos y las constancias son
consecuencias de haber resuelto esa pregunta.

Las cuatro fuerzas que dominan el diseño:

1. **La identidad es el problema, no un prerrequisito.**
   El sistema no existe porque falten formularios: existe porque los formularios
   no se hablan entre sí. Cada decisión sobre identificadores, detección de
   duplicados y fusión es la funcionalidad central, no infraestructura de
   soporte.
2. **Inscripción y participación son hechos distintos.**
   Toda la confusión estadística que motiva el proyecto nace de tratarlos como
   uno solo. El modelo los separa en dos tablas y ninguna consulta de reporte los
   mezcla sin decirlo.
3. **Nada se borra.**
   Participaciones, puntos, constancias e indicadores cerrados son inmutables o
   protegidos contra el borrado por [requerimiento explícito][rf-a-50]. La
   corrección es siempre una anulación con motivo.
4. **El dato histórico llega sucio y hay que admitirlo.**
   Las matrices existentes tienen filas sin autorización de datos, sin fecha de
   nacimiento y con instituciones escritas de tres maneras. El modelo admite
   estados de _pendiente de verificar_ en lugar de rechazar la migración o
   inventar valores.

## Restricciones del alcance

|                   Restricción                    |                  Origen                   |                                  Consecuencia en el modelo                                  |
| :----------------------------------------------: | :---------------------------------------: | :-----------------------------------------------------------------------------------------: |
|            Un solo rol administrativo            | Análisis preliminar, [`RF-A-03`][rf-a-03] |   Grupos de Django declarados desde el principio, poblados con un solo rol administrativo   |
| Asistencia validada por actividad, no por sesión |           [`RF-A-26`][rf-a-26]            | No hay tabla de sesiones ni de asistencia por día; un diplomado de ocho semanas es una fila |
|   Sin formularios de inscripción configurables   |           [`RF-P-16`][rf-p-16]            |    Toda actividad pide los mismos datos; no hay motor de campos dinámicos ni respuestas     |
|      Sin evaluación ni rúbricas de proyecto      |        Sin requerimiento asociado         |   El portafolio guarda clasificación y trayectoria, no calificaciones ni actas de jurado    |
|        Constancia como documento generado        |           [`RF-A-35`][rf-a-35]            | No hay firma electrónica avanzada; la verificación es por folio y código, no criptográfica  |

## Fuera de alcance

|                 Funcionalidad                  |                         Estado                         |
| :--------------------------------------------: | :----------------------------------------------------: |
|      Asistencia por sesión con código QR       |               Sin requerimiento asociado               |
|    Formularios de inscripción por actividad    |               Sin requerimiento asociado               |
|   Evaluación de proyectos y actas de jurado    |               Sin requerimiento asociado               |
| Integración con el sistema académico de la UAM |          Sin interfaz disponible del lado UAM          |
|         Canje de puntos por beneficios         |               Sin requerimiento asociado               |
|        Notificación por WhatsApp o SMS         | El sistema captura el número pero no lo usa como canal |
|     Carga masiva de matrices (importación)     |  Diferida hasta que exista la herramienta; ver abajo   |

!!! warning "Sobre el portafolio de innovación"

    Este modelo incluye el portafolio porque, sin él, la columna _código del
    proyecto_ de la matriz de participaciones queda apuntando a un vacío. Su
    alcance es el de la matriz: registro, clasificación y trayectoria. No incluye
    seguimiento de hitos, presupuesto, propiedad intelectual ni transferencia
    tecnológica, que la matriz tampoco cubre.

!!! note "Sobre la importación"

    `importacion`, `importacion_fila` y `exportacion` del diseño original no
    existen todavía. El origen `importacion` sí está en `rudi_user.origen`,
    `inscripcion.origen` y los estados con origen, de modo que la herramienta,
    cuando exista, escribe en las mismas tablas que la API. Quién descargó datos
    personales lo registra `acceso_dato_personal`.

---

## Invariantes críticos

Seis garantías que no pueden fallar. Todas son estructurales: si alguna se
implementa en la capa de aplicación, el requerimiento correspondiente deja de ser
una garantía y pasa a ser una aspiración.

|                           Invariante                           |                          Mecanismo                          |               Requerimientos               |
| :------------------------------------------------------------: | :---------------------------------------------------------: | :----------------------------------------: |
|         Un identificador pertenece a una sola persona          |                `unq_identificadoruser_valor`                | [`RF-P-02`][rf-p-02], [`RF-A-07`][rf-a-07] |
|   Una persona tiene una sola inscripción viva por actividad    |              `unq_inscripcion_persona_activa`               |            [`RF-P-17`][rf-p-17]            |
|         Los inscritos nunca superan el cupo declarado          | `chk_actividad_cupo_coherente` + `trg_inscripcion_contador` | [`RF-A-18`][rf-a-18], [`RF-P-18`][rf-p-18] |
|       Un folio de constancia es único y no se reutiliza        |                   `unq_constancia_folio`                    | [`RF-A-35`][rf-a-35], [`RF-P-24`][rf-p-24] |
| Como máximo una carrera vigente del estudiante es la principal |              `unq_estudiantecarrera_principal`              |            [`RF-P-09`][rf-p-09]            |
|  Ninguna persona, participación, punto ni constancia se borra  |          `trg_protect_delete` / `trg_append_only`           |            [`RF-A-50`][rf-a-50]            |

> El invariante del cupo es el único que compite bajo concurrencia. Dos personas
> pulsando _inscribirme_ en el mismo instante sobre el último lugar es el caso
> real de todo hackathon con inscripción abierta. `CHECK (inscritos_activos <= cupo)`
> sobre `actividad`, combinado con el trigger que incrementa el contador dentro
> de la misma transacción que crea la inscripción, convierte el sobrecupo en un
> error de transacción sin `SELECT ... FOR UPDATE` explícito en la aplicación.

---

## Mapa de módulos

Las flechas indican dependencia por llave foránea: el origen referencia al
destino. Cada módulo es una app de Django.

|               Módulo               |             App              |                        Depende de                        |
| :--------------------------------: | :--------------------------: | :------------------------------------------------------: |
|           **`Estados`**            |        `rudi_estados`        |                            —                             |
| **`Catálogos`** y **`Taxonomías`** |       `rudi_catalogos`       |                            —                             |
|           **`Perfiles`**           | `rudi_auth`, `rudi_profiles` |         Estados, Catálogos; cuenta del template          |
|         **`Actividades`**          |      `rudi_actividades`      |               Estados, Catálogos, Perfiles               |
|        **`Participación`**         |     `rudi_participacion`     |        Estados, Catálogos, Perfiles, Actividades         |
|            **`Puntos`**            |        `rudi_puntos`         | Estados, Catálogos, Perfiles, Actividades, Participación |
|         **`Constancias`**          |      `rudi_constancias`      |       Estados, Catálogos, Perfiles, Participación        |
|          **`Portafolio`**          |      `rudi_portafolio`       |        Estados, Catálogos, Perfiles, Actividades         |
|        **`Notificaciones`**        |    `rudi_notificaciones`     |                   Catálogos, Perfiles                    |
|          **`Analítica`**           |       `rudi_analitica`       |                         Perfiles                         |

**`Estados`** y **`Catálogos`** son hojas del grafo: no referencian a nadie y
todos los referencian.

`asignacion_mentor` vive en **`Participación`** y no en **`Actividades`**,
como decía el diseño original: referencia a `equipo`, que es de participación,
y dejarla en actividades haría que las dos apps se referenciaran mutuamente.

Ningún módulo referencia a **`Participación`** salvo **`Puntos`** y
**`Constancias`**. Los triggers con los que la validación de una participación
otorga puntos o la anulación invalida constancias se registran desde esos
módulos sobre `participacion` ([Efecto en otra tabla][triggers-efecto]), de modo
que la tabla que más crece no conoce a quien reacciona a ella.

**`Portafolio`** no referencia a **`Participación`**: una propuesta sobrevive a
la actividad que la originó y su equipo cambia con el tiempo, de modo que se
vincula a personas y a actividades, nunca a participaciones concretas.

[triggers-efecto]: triggers.md#efecto-en-otra-tabla
[rf-a-03]: ../requerimientos/funcionales/administracion.md#rf-a-03
[rf-a-07]: ../requerimientos/funcionales/administracion.md#rf-a-07
[rf-a-18]: ../requerimientos/funcionales/administracion.md#rf-a-18
[rf-a-26]: ../requerimientos/funcionales/administracion.md#rf-a-26
[rf-a-35]: ../requerimientos/funcionales/administracion.md#rf-a-35
[rf-a-50]: ../requerimientos/funcionales/administracion.md#rf-a-50
[rf-p-02]: ../requerimientos/funcionales/participantes.md#rf-p-02
[rf-p-09]: ../requerimientos/funcionales/participantes.md#rf-p-09
[rf-p-16]: ../requerimientos/funcionales/participantes.md#rf-p-16
[rf-p-17]: ../requerimientos/funcionales/participantes.md#rf-p-17
[rf-p-18]: ../requerimientos/funcionales/participantes.md#rf-p-18
[rf-p-24]: ../requerimientos/funcionales/participantes.md#rf-p-24
