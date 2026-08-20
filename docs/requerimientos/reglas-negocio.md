---
icon: lucide/gavel
---

# Reglas de negocio

## RN-01

> **Identificación única de personas**

Toda persona registrada tiene al menos un identificador. El principal del
estudiante UAM es el CIF; el de participantes externos, docentes y mentores es la
cédula u otro documento admitido. Una persona puede tener más de uno y todos son
igualmente válidos para reconocerla.

- **Mecanismo:** `identificador_persona` con unicidad sobre tipo y valor normalizado
- **Origen:** [`RF-P-02`][rf-p-02], [`RF-A-09`][rf-a-09]

## RN-02

> **No duplicidad de personas**

Un mismo identificador no puede pertenecer a dos registros. Cuando una persona
vuelve a aparecer, el sistema usa el registro existente y le asocia la actividad
nueva en lugar de crear otro perfil.

- **Mecanismo:** índice único, detección previa al alta y `fusion_usuario` para lo ya duplicado
- **Origen:** [`RF-A-07`][rf-a-07], [`RF-A-08`][rf-a-08], [`RF-P-02`][rf-p-02]

## RN-03

> **Clasificación obligatoria por perfil**

Toda persona tiene al menos un perfil declarado. El perfil determina qué datos se
le exigen, qué puede hacer y cómo se le cuenta en los reportes.

- **Mecanismo:** trigger que exige al menos una fila de perfil por `usuario` activo
- **Origen:** [`RF-P-01`][rf-p-01], [`RF-A-10`][rf-a-10]

!!! note "Precisión frente al enunciado original"

    El documento preliminar trata el tipo de usuario como un atributo único de la
    persona. El modelo lo trata como un conjunto: los perfiles son acumulables
    porque en la práctica lo son. Un docente que además mentorea no debe elegir
    entre aparecer como docente o como mentor en los reportes del año.

## RN-04

> **Registro académico del estudiante UAM**

Todo estudiante UAM tiene facultad y carrera. La segunda carrera se registra sin
duplicar los datos personales, y la facultad se deriva de la carrera en lugar de
capturarse aparte.

- **Mecanismo:** `estudiante_carrera` con marca de principal y llave foránea a `carrera`
- **Origen:** [`RF-P-08`][rf-p-08], [`RF-P-09`][rf-p-09]

## RN-05

> **Inscripción única por actividad**

Una persona no puede tener dos inscripciones vivas en la misma actividad.

- **Mecanismo:** índice único parcial sobre persona y actividad donde la inscripción no está cerrada
- **Origen:** [`RF-P-17`][rf-p-17]

## RN-06

> **Inscripción y participación son hechos distintos**

Inscribirse no es participar. Solo la validación administrativa convierte una
inscripción en participación efectiva y da lugar a puntos, constancias y conteos
de participantes reales.

- **Mecanismo:** dos tablas separadas, `inscripcion` y `participacion`
- **Origen:** [`RF-A-26`][rf-a-26], [`RF-P-21`][rf-p-21]

## RN-07

> **Validación administrativa de la participación**

La participación la valida el administrador. Antes de esa validación no se
registran puntos, roles definitivos ni evidencias formales.

- **Mecanismo:** `participacion.validada_por` obligatorio en los estados que declaran participación efectiva
- **Origen:** [`RF-A-26`][rf-a-26]

## RN-08

> **Puntos según criterios previamente definidos**

Los puntos dependen del tipo de actividad, el rol y el desenlace, conforme a
criterios que la Dirección fija de antemano. No todas las actividades otorgan lo
mismo.

- **Mecanismo:** `regla_puntuacion` con vigencia por rango de fechas
- **Origen:** [`RF-A-30`][rf-a-30], [`RF-A-31`][rf-a-31]

## RN-09

> **Acumulación individual y trazable de puntos**

Los puntos se acumulan por persona y cada uno está ligado a una participación
validada concreta.

- **Mecanismo:** `movimiento_punto` como libro mayor `append-only` con llave foránea a `participacion`
- **Origen:** [`RF-P-22`][rf-p-22], [`RF-A-33`][rf-a-33]

## RN-10

> **Las actividades solo las administra la DIEM**

Crear, modificar, cerrar o cancelar actividades es exclusivo del administrador.
Los participantes consultan e inscriben, nunca editan la información oficial.

- **Mecanismo:** ámbito de sesión y permisos; ninguna ruta del portal del participante escribe en `actividad`
- **Origen:** [`RF-A-16`][rf-a-16], [`RF-A-17`][rf-a-17]

## RN-11

> **Control de cupo**

Alcanzado el cupo, no se admiten inscripciones nuevas salvo ampliación del cupo o
excepción administrativa declarada.

- **Mecanismo:** `CHECK` sobre el contador de inscritos más trigger que lo incrementa en la misma transacción
- **Origen:** [`RF-A-18`][rf-a-18], [`RF-P-18`][rf-p-18]

## RN-12

> **Los mentores se asocian a las actividades donde acompañan**

Un mentor consta únicamente en las actividades, equipos o grupos en los que
efectivamente acompaña.

- **Mecanismo:** `asignacion_mentor` con estado propio; solo la asignación confirmada aparece como acompañamiento
- **Origen:** [`RF-A-20`][rf-a-20], [`RF-P-27`][rf-p-27]

## RN-13

> **Los reportes distinguen inscripciones de participantes únicos**

Una persona que participa en varias actividades del año cuenta varias veces como
inscripción y una sola como participante único.

- **Mecanismo:** conteo distinto sobre el registro conservado tras fusiones, nunca sobre filas de inscripción
- **Origen:** [`RF-A-43`][rf-a-43]

## RN-14

> **Cada quien ve su propio historial**

El participante consulta solo lo suyo. El administrador consulta el de todos, y
cada consulta a datos de una persona concreta queda registrada.

- **Mecanismo:** filtro por identidad de sesión en el portal del participante; bitácora de acceso en el panel
- **Origen:** [`RF-P-25`][rf-p-25], [`RF-A-04`][rf-a-04]

## RN-15

> **Constancias solo sobre participación validada**

No se emite constancia por inscripción. La constancia acredita algo que ocurrió y
que alguien verificó.

- **Mecanismo:** trigger que rechaza la emisión si alguna participación amparada no está validada
- **Origen:** [`RF-A-35`][rf-a-35], [`RF-P-23`][rf-p-23]

## RN-16

> **La información histórica no se elimina**

Participaciones, puntos, constancias, indicadores cerrados y bitácora no se
borran. Se corrigen anulando con motivo y conservando el registro original.

- **Mecanismo:** triggers `BEFORE DELETE` que abortan, y anulación por marca temporal más movimiento inverso
- **Origen:** [`RF-A-29`][rf-a-29], [`RF-A-33`][rf-a-33], [`RF-A-50`][rf-a-50]

---

## Reglas añadidas por el modelo

## RN-17

> **El consentimiento se guarda versionado, no como un sí**

El sistema almacena qué versión del aviso de privacidad aceptó cada persona y
cuándo. Un consentimiento retirado o nunca otorgado deja a la persona fuera de
los reportes nominales y de las comunicaciones no esenciales, sin borrar sus
participaciones.

- **Mecanismo:** `politica_privacidad` versionada y `consentimiento_datos` con estado propio
- **Origen:** [`RF-P-07`][rf-p-07]

El campo _autorización para tratamiento de datos_ de la matriz de estudiantes
tiene tres valores —documentada, pendiente de verificar y no autorizada— y la
propia matriz advierte que no sustituye al formulario ni al aviso de privacidad.
Guardar solo ese estado sin la versión del aviso reproduce el problema en el
sistema nuevo.

## RN-18

> **La corrección de un año cerrado no reescribe su cierre**

Un indicador anual cerrado es inmutable. Toda corrección posterior a
participaciones de ese año se refleja como diferencia frente al cierre, nunca
modificándolo.

- **Mecanismo:** `indicador_periodo` `append-only` con instante de cierre
- **Origen:** [`RF-A-45`][rf-a-45]

Sin esta regla, un informe institucional entregado en enero deja de ser
reproducible en cuanto alguien valida una participación rezagada de diciembre, y
la DIEM no puede explicar por qué la misma consulta da dos cifras distintas.

[rf-a-04]: funcionales/administracion.md#rf-a-04
[rf-a-07]: funcionales/administracion.md#rf-a-07
[rf-a-08]: funcionales/administracion.md#rf-a-08
[rf-a-09]: funcionales/administracion.md#rf-a-09
[rf-a-10]: funcionales/administracion.md#rf-a-10
[rf-a-16]: funcionales/administracion.md#rf-a-16
[rf-a-17]: funcionales/administracion.md#rf-a-17
[rf-a-18]: funcionales/administracion.md#rf-a-18
[rf-a-20]: funcionales/administracion.md#rf-a-20
[rf-a-26]: funcionales/administracion.md#rf-a-26
[rf-a-29]: funcionales/administracion.md#rf-a-29
[rf-a-30]: funcionales/administracion.md#rf-a-30
[rf-a-31]: funcionales/administracion.md#rf-a-31
[rf-a-33]: funcionales/administracion.md#rf-a-33
[rf-a-35]: funcionales/administracion.md#rf-a-35
[rf-a-43]: funcionales/administracion.md#rf-a-43
[rf-a-45]: funcionales/administracion.md#rf-a-45
[rf-a-50]: funcionales/administracion.md#rf-a-50
[rf-p-01]: funcionales/participantes.md#rf-p-01
[rf-p-02]: funcionales/participantes.md#rf-p-02
[rf-p-07]: funcionales/participantes.md#rf-p-07
[rf-p-08]: funcionales/participantes.md#rf-p-08
[rf-p-09]: funcionales/participantes.md#rf-p-09
[rf-p-17]: funcionales/participantes.md#rf-p-17
[rf-p-18]: funcionales/participantes.md#rf-p-18
[rf-p-21]: funcionales/participantes.md#rf-p-21
[rf-p-22]: funcionales/participantes.md#rf-p-22
[rf-p-23]: funcionales/participantes.md#rf-p-23
[rf-p-25]: funcionales/participantes.md#rf-p-25
[rf-p-27]: funcionales/participantes.md#rf-p-27
