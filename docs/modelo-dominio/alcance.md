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
   Participaciones, puntos, constancias, bitácora e indicadores cerrados son
   inmutables o `append-only` por [requerimiento explícito][rf-a-50]. La
   corrección es siempre una anulación con motivo.
4. **El dato histórico llega sucio y hay que admitirlo.**
   Las matrices existentes tienen filas sin autorización de datos, sin fecha de
   nacimiento y con instituciones escritas de tres maneras. El modelo admite
   estados de _pendiente de verificar_ en lugar de rechazar la migración o
   inventar valores.

## Restricciones del alcance

Cinco decisiones que simplifican el modelo de forma sustancial. Todas son
reversibles sin migración destructiva; los enganches están en
[`Extensiones`][extensiones].

|                   Restricción                    |                  Origen                   |                                  Consecuencia en el modelo                                  |
| :----------------------------------------------: | :---------------------------------------: | :-----------------------------------------------------------------------------------------: |
|            Un solo rol administrativo            | Análisis preliminar, [`RF-A-03`][rf-a-03] |        No hay matriz de permisos por recurso; el rol se declara pero no se ramifica         |
| Asistencia validada por actividad, no por sesión |           [`RF-A-26`][rf-a-26]            | No hay tabla de sesiones ni de asistencia por día; un diplomado de ocho semanas es una fila |
|   Sin formularios de inscripción configurables   |           [`RF-P-16`][rf-p-16]            |    Toda actividad pide los mismos datos; no hay motor de campos dinámicos ni respuestas     |
|      Sin evaluación ni rúbricas de proyecto      |        Sin requerimiento asociado         |   El portafolio guarda clasificación y trayectoria, no calificaciones ni actas de jurado    |
|        Constancia como documento generado        |           [`RF-A-35`][rf-a-35]            | No hay firma electrónica avanzada; la verificación es por folio y código, no criptográfica  |

## Fuera de alcance

|                 Funcionalidad                  |                         Estado                         |    Enganche    |
| :--------------------------------------------: | :----------------------------------------------------: | :------------: |
|      Asistencia por sesión con código QR       |               Sin requerimiento asociado               | [`E-01`][e-01] |
|    Formularios de inscripción por actividad    |               Sin requerimiento asociado               | [`E-02`][e-02] |
|   Evaluación de proyectos y actas de jurado    |               Sin requerimiento asociado               | [`E-03`][e-03] |
| Integración con el sistema académico de la UAM |                 [Riesgo abierto][r-01]                 | [`E-04`][e-04] |
|         Canje de puntos por beneficios         |               Sin requerimiento asociado               | [`E-05`][e-05] |
|    Separación de funciones administrativas     |          Restringido por [`RF-A-03`][rf-a-03]          | [`E-06`][e-06] |
|        Notificación por WhatsApp o SMS         | El sistema captura el número pero no lo usa como canal | [`E-07`][e-07] |

!!! warning "Sobre el portafolio de innovación"

    El análisis preliminar no enuncia ningún requerimiento de portafolio: menciona
    proyectos como un tipo de actividad y nada más. La matriz de portafolio, en
    cambio, define veintidós campos con taxonomías completas y un código de
    proyecto que la matriz de participaciones ya referencia.

    Este modelo incluye el portafolio porque sin él la columna _código del
    proyecto_ de la matriz de participaciones queda apuntando a un vacío. Su
    alcance es el de la matriz: registro, clasificación y trayectoria. No incluye
    seguimiento de hitos, presupuesto, propiedad intelectual ni transferencia
    tecnológica, que la matriz tampoco cubre. Confirmar el alcance antes de
    escribir migraciones: ver [`R-08`][r-08].

[extensiones]: extensiones.md
[e-01]: extensiones.md#e-01
[e-02]: extensiones.md#e-02
[e-03]: extensiones.md#e-03
[e-04]: extensiones.md#e-04
[e-05]: extensiones.md#e-05
[e-06]: extensiones.md#e-06
[e-07]: extensiones.md#e-07
[r-01]: riesgos.md#r-01
[r-08]: riesgos.md#r-08
[rf-a-03]: ../requerimientos/funcionales/administracion.md#rf-a-03
[rf-a-26]: ../requerimientos/funcionales/administracion.md#rf-a-26
[rf-a-35]: ../requerimientos/funcionales/administracion.md#rf-a-35
[rf-a-50]: ../requerimientos/funcionales/administracion.md#rf-a-50
[rf-p-16]: ../requerimientos/funcionales/participantes.md#rf-p-16
