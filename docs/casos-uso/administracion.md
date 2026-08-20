---
icon: lucide/folder-lock
---

# Portal de administración

- **Módulos:** 9
- **Total:** 22

---

## Acceso

### CU-A-01

> **Iniciar sesión en el panel**

- **Actor:** [Administrador DIEM][act-admin]
- **Precondición:** La cuenta administrativa está activa
- **Requerimientos:**
  > - [`RF-A-01`][rf-a-01]
  > - [`RF-A-02`][rf-a-02]

**Flujo principal**

1. El administrador introduce correo y contraseña en la ruta del panel.
2. El sistema abre la sesión con ámbito administrativo y expiración por inactividad de treinta minutos.
3. Registra el ingreso en bitácora con la dirección de origen.

!!! example "**Alternativas**"

    === "**1a**"

        **Cinco intentos fallidos consecutivos**

        El sistema bloquea el acceso treinta minutos y registra cada intento con
        el identificador tecleado.

    === "**1b**"

        **Las credenciales corresponden a una cuenta de participante**

        El sistema rechaza el acceso sin indicar si la cuenta existe. El panel no
        admite cuentas de ámbito participante, aunque la persona sea la misma.

- **Postcondición:** Sesión administrativa activa.

### CU-A-02

> **Dar de alta una cuenta administrativa**

- **Actor:** [Administrador DIEM][act-admin]
- **Precondición:** Sesión abierta
- **Requerimientos:**
  > - [`RF-A-01`][rf-a-01]
  > - [`RF-A-03`][rf-a-03]

**Flujo principal**

1. El administrador introduce el correo del invitado.
2. El sistema emite una invitación con enlace de un solo uso y vigencia de setenta y dos horas.
3. El invitado abre el enlace y crea su contraseña.
4. El sistema activa la cuenta, la registra en bitácora y notifica a las demás cuentas administrativas.

!!! example "**Alternativas**"

    === "**1a**"

        **El correo ya tiene una invitación viva**

        El sistema reutiliza la invitación pendiente en lugar de acumular dos
        enlaces válidos al mismo destinatario.

    === "**2a**"

        **La invitación intenta otorgar rol administrativo y perfil de participante**

        El sistema la rechaza. Son ámbitos que no se mezclan en una misma alta.

    === "**3a**"

        **El enlace expiró**

        El sistema lo informa y exige emitir una invitación nueva. El enlace
        vencido no se reactiva.

- **Postcondición:** Existe una cuenta administrativa activa más.

---

## Personas

### CU-A-03

> **Registrar una persona desde administración**

- **Actor:** [Administrador DIEM][act-admin]
- **Precondición:** Sesión abierta
- **Requerimientos:**
  > - [`RF-A-06`][rf-a-06]
  > - [`RF-A-07`][rf-a-07]

**Flujo principal**

1. El administrador introduce el identificador de la persona.
2. El sistema busca coincidencias y no encuentra ninguna.
3. El administrador completa datos personales, perfil y, si es estudiante UAM, carrera y año.
4. El sistema crea el registro marcado con origen administrativo, sin credencial de acceso.
5. Registra el alta en bitácora.

!!! example "**Alternativas**"

    === "**2a**"

        **El identificador ya existe**

        El sistema muestra la ficha existente con sus participaciones y ofrece
        usarla. No crea un registro nuevo bajo ninguna circunstancia: es la
        regla que el sistema existe para hacer cumplir.

    === "**2b**"

        **Hay coincidencia por nombre y fecha de nacimiento, no por identificador**

        El sistema presenta los candidatos y exige que el administrador declare
        expresamente que se trata de otra persona. La declaración queda en
        bitácora con su nombre.

    === "**3a**"

        **El identificador no cumple el patrón de su tipo**

        El sistema lo acepta marcándolo como pendiente de verificación y lo lista
        en la bandeja de identificadores por revisar.

- **Postcondición:** La persona existe en el directorio y puede ser inscrita.

### CU-A-04

> **Resolver un posible duplicado**

- **Actor:** [Administrador DIEM][act-admin]
- **Precondición:** Existen dos registros marcados como posible duplicado
- **Requerimientos:**
  > - [`RF-A-07`][rf-a-07]
  > - [`RF-A-08`][rf-a-08]

**Flujo principal**

1. El administrador abre la bandeja de posibles duplicados.
2. El sistema muestra los dos registros lado a lado con sus identificadores, perfiles y participaciones.
3. El administrador decide si son la misma persona.
4. Si lo son, continúa con [`CU-A-05`](#cu-a-05); si no, marca el par como distinto.
5. El sistema guarda la decisión para no volver a proponer ese par.

- **Postcondición:** El par queda resuelto en un sentido o en el otro.

### CU-A-05

> **Fusionar dos registros de la misma persona**

- **Actor:** [Administrador DIEM][act-admin]
- **Precondición:** Ambos registros existen y se confirmó que son la misma persona
- **Requerimientos:**
  > - [`RF-A-08`][rf-a-08]
  > - [`RF-A-43`][rf-a-43]

**Flujo principal**

1. El administrador designa el registro que se conserva y el que se absorbe.
2. El sistema muestra qué se trasladará: identificadores, perfiles, inscripciones, participaciones, puntos, constancias y vínculos de portafolio.
3. El administrador introduce el motivo y confirma.
4. El sistema traslada todo al conservado, deja el absorbido sin acceso apuntando al conservado y registra la fusión con ambos identificadores.
5. Los reportes de participantes únicos dejan de contar dos veces, también en años anteriores.

!!! example "**Alternativas**"

    === "**2a**"

        **Ambos registros participaron en la misma actividad**

        El sistema conserva la participación validada y anula la otra dejando
        constancia del reemplazo. Si ambas están validadas, conserva la más
        antigua y lo indica en el resumen.

    === "**2b**"

        **Los dos registros tienen constancias emitidas**

        Las constancias no se tocan: siguen siendo válidas y verificables por su
        folio, ahora asociadas al registro conservado.

    === "**3a**"

        **La fusión se hizo por error**

        No hay deshacer automático. El registro de la fusión conserva el detalle
        de lo trasladado, y revertirla es una operación manual documentada. Ver
        [`R-04`][r-04].

- **Postcondición:** Existe un solo registro operativo para esa persona y la fusión es consultable.

### CU-A-06

> **Verificar el identificador de una persona**

- **Actor:** [Administrador DIEM][act-admin]
- **Precondición:** El identificador está pendiente de verificación
- **Requerimientos:**
  > - [`RF-A-09`][rf-a-09]

**Flujo principal**

1. El administrador abre la bandeja de identificadores pendientes.
2. Contrasta el valor contra el documento o el listado institucional.
3. Marca el identificador como verificado o lo corrige.
4. El sistema registra quién verificó y cuándo.

!!! example "**Alternativas**"

    === "**3a**"

        **La corrección produce un valor que ya pertenece a otra persona**

        El sistema la rechaza y abre el flujo de posible duplicado, porque dos
        personas con el mismo identificador es exactamente lo que el modelo
        impide.

- **Postcondición:** El identificador queda verificado o corregido, con rastro.

---

## Actividades

### CU-A-07

> **Dar de alta un programa**

- **Actor:** [Administrador DIEM][act-admin]
- **Precondición:** Sesión abierta
- **Requerimientos:**
  > - [`RF-A-15`][rf-a-15]

**Flujo principal**

1. El administrador introduce el nombre oficial del programa y su tipo por defecto.
2. El sistema lo crea sin fechas: las fechas pertenecen a sus ediciones.
3. El programa queda disponible para asociarle actividades.

- **Postcondición:** El programa existe y agrupará sus ediciones en los reportes.

### CU-A-08

> **Crear una actividad**

- **Actor:** [Administrador DIEM][act-admin]
- **Precondición:** Sesión abierta
- **Requerimientos:**
  > - [`RF-A-16`][rf-a-16]
  > - [`RF-A-18`][rf-a-18]
  > - [`RF-A-19`][rf-a-19]

**Flujo principal**

1. El administrador elige el programa o deja la actividad como única.
2. Introduce nombre, etiqueta de edición, tipo, modalidad, lugar, fechas, cupo, ventana de inscripción y puntaje base.
3. Designa responsables.
4. El sistema crea la actividad en borrador, invisible en el catálogo público.
5. El administrador la publica cuando está lista.

!!! example "**Alternativas**"

    === "**2a**"

        **La ventana de inscripción cierra después de la fecha de inicio**

        El sistema lo admite y lo advierte: hay actividades que aceptan
        inscripciones el mismo día. Lo que rechaza es que la ventana abra después
        de que cierre.

    === "**2b**"

        **La fecha de finalización es anterior a la de inicio**

        El sistema la rechaza.

    === "**4a**"

        **Se publica una actividad sin cupo declarado**

        El sistema la admite: cupo vacío significa sin límite, y es lo normal en
        charlas abiertas.

- **Postcondición:** La actividad es visible y admite inscripciones dentro de su ventana.

### CU-A-09

> **Cancelar una actividad**

- **Actor:** [Administrador DIEM][act-admin]
- **Precondición:** La actividad está publicada o en curso
- **Requerimientos:**
  > - [`RF-A-17`][rf-a-17]
  > - [`RF-A-24`][rf-a-24]

**Flujo principal**

1. El administrador selecciona el motivo de cancelación.
2. El sistema cancela las inscripciones vivas, libera la lista de espera y notifica a cada inscrito.
3. La actividad pasa a cancelada y desaparece del catálogo público.

!!! example "**Alternativas**"

    === "**2a**"

        **La actividad ya tiene participaciones validadas**

        El sistema conserva esas participaciones, sus puntos y sus constancias.
        Cancelar la edición no borra lo que ya ocurrió en ella.

- **Postcondición:** La actividad queda cancelada con motivo y sin inscripciones vivas.

### CU-A-10

> **Asignar un mentor a una actividad**

- **Actor:** [Administrador DIEM][act-admin]
- **Precondición:** La persona tiene perfil de mentor confirmado
- **Requerimientos:**
  > - [`RF-A-20`][rf-a-20]
  > - [`RF-P-27`][rf-p-27]

**Flujo principal**

1. El administrador elige al mentor y la actividad, e indica el tipo de acompañamiento.
2. El sistema crea la asignación en estado propuesta y notifica al mentor.
3. El mentor acepta desde su portal.
4. La asignación pasa a confirmada y el mentor aparece en la ficha pública de la actividad.

!!! example "**Alternativas**"

    === "**3a**"

        **El mentor declina**

        La asignación queda declinada con el motivo que indicó y el mentor no
        aparece en la ficha pública. La DIEM ve el motivo en la bandeja.

    === "**3b**"

        **El mentor no responde antes del inicio de la actividad**

        La asignación permanece como propuesta y el proceso programado la marca
        como vencida. Nunca se autoconfirma por silencio.

- **Postcondición:** El acompañamiento consta con un estado explícito.

### CU-A-11

> **Conformar un equipo**

- **Actor:** [Administrador DIEM][act-admin]
- **Precondición:** La actividad admite equipos
- **Requerimientos:**
  > - [`RF-A-21`][rf-a-21]

**Flujo principal**

1. El administrador crea el equipo con su nombre dentro de la actividad.
2. Agrega miembros de entre las personas inscritas y designa al líder.
3. El sistema valida el tamaño mínimo y máximo declarados por la actividad.
4. Al cerrar la inscripción, la composición queda fijada.

!!! example "**Alternativas**"

    === "**2a**"

        **La persona ya pertenece a otro equipo de la misma actividad**

        El sistema lo rechaza. Una persona por equipo y por actividad.

    === "**4a**"

        **Hay que mover a alguien después del cierre**

        El sistema lo admite solo desde administración y lo registra en bitácora,
        porque cambia la composición de un equipo que ya se reportó.

- **Postcondición:** El equipo existe y sus miembros son citables en la participación.

---

## Inscripción

### CU-A-12

> **Inscribir a una persona en nombre de un tercero**

- **Actor:** [Administrador DIEM][act-admin]
- **Precondición:** La persona existe en el directorio y la actividad admite inscripciones
- **Requerimientos:**
  > - [`RF-A-23`][rf-a-23]

**Flujo principal**

1. El administrador busca a la persona por identificador.
2. Elige la actividad y confirma.
3. El sistema crea la inscripción marcada con origen administrativo y con la cuenta que la creó.

!!! example "**Alternativas**"

    === "**2a**"

        **La persona ya está inscrita**

        El sistema muestra la inscripción existente y no crea otra.

    === "**2b**"

        **La actividad alcanzó su cupo**

        El sistema ofrece inscribir por excepción, exigiendo confirmación
        explícita, y deja la excepción registrada. El cupo se supera con rastro o
        no se supera.

- **Postcondición:** La inscripción existe y es distinguible de una hecha por la propia persona.

### CU-A-13

> **Promover una inscripción desde la lista de espera**

- **Actor:** [Proceso programado][act-proceso], [Administrador DIEM][act-admin]
- **Precondición:** Se liberó un lugar y hay lista de espera
- **Requerimientos:**
  > - [`RF-A-18`][rf-a-18]
  > - [`RF-P-18`][rf-p-18]

**Flujo principal**

1. Una cancelación o una ampliación de cupo libera lugares.
2. El sistema promueve al primero de la lista en orden de llegada.
3. Notifica a la persona promovida y actualiza la posición de las restantes.

!!! example "**Alternativas**"

    === "**2a**"

        **La ventana de inscripción ya cerró**

        No hay promoción automática. El administrador puede promover
        manualmente, y esa promoción queda registrada como excepción.

- **Postcondición:** El cupo liberado se ocupa sin intervención y en orden.

---

## Participación

### CU-A-14

> **Validar la participación de una persona**

- **Actor:** [Administrador DIEM][act-admin]
- **Precondición:** La actividad ocurrió y la persona consta como inscrita o asistente
- **Requerimientos:**
  > - [`RF-A-25`][rf-a-25]
  > - [`RF-A-26`][rf-a-26]
  > - [`RF-A-31`][rf-a-31]

**Flujo principal**

1. El administrador abre el listado de la actividad y selecciona a la persona.
2. Indica el rol desempeñado, el desenlace, las fechas y el enlace de evidencia.
3. El sistema registra la validación con su cuenta y el instante.
4. Resuelve la regla de puntuación vigente y genera el movimiento de puntos.
5. La participación queda disponible para constancia y para los reportes de participantes reales.

!!! example "**Alternativas**"

    === "**1a**"

        **La persona asistió sin haberse inscrito**

        El sistema admite registrar la participación sin inscripción previa, que
        es lo que ocurre en toda charla abierta. Si la persona no existe en el
        directorio, primero se ejecuta [`CU-A-03`](#cu-a-03).

    === "**2a**"

        **El desenlace es retirada o no completó**

        El sistema registra la participación pero no habilita constancia de
        finalización, y aplica la regla de puntuación correspondiente a ese
        desenlace, que puede ser de cero puntos.

    === "**4a**"

        **Ninguna regla del baremo aplica**

        La participación queda validada con cero puntos y aparece en la lista de
        revisión. El sistema no inventa un valor ni aborta la validación.

- **Postcondición:** Existe participación efectiva y, si corresponde, puntos asociados.

### CU-A-15

> **Validar participaciones a partir de un listado**

- **Actor:** [Administrador DIEM][act-admin]
- **Precondición:** La actividad ocurrió y existe listado de asistencia
- **Requerimientos:**
  > - [`RF-A-27`][rf-a-27]

**Flujo principal**

1. El administrador carga el listado con los identificadores de los asistentes.
2. El sistema resuelve cada fila contra el directorio y presenta un resumen: resueltas, no resueltas y ya validadas.
3. El administrador revisa el resumen y confirma.
4. El sistema valida las resueltas en una sola operación y genera sus puntos.
5. Las no resueltas quedan en una bandeja para decidirlas una por una.

!!! example "**Alternativas**"

    === "**2a**"

        **Una fila no corresponde a ninguna persona registrada**

        Queda en la bandeja. La carga masiva no crea personas: crear una persona
        exige las validaciones de [`CU-A-03`](#cu-a-03).

    === "**3a**"

        **El administrador cancela en el resumen**

        No se escribe nada. La confirmación es el único punto donde la operación
        se materializa.

- **Postcondición:** Las participaciones resueltas quedan validadas y las demás, pendientes con motivo.

### CU-A-16

> **Anular una participación validada**

- **Actor:** [Administrador DIEM][act-admin]
- **Precondición:** La participación está validada
- **Requerimientos:**
  > - [`RF-A-29`][rf-a-29]
  > - [`RF-A-33`][rf-a-33]

**Flujo principal**

1. El administrador selecciona el motivo de anulación.
2. El sistema marca la participación como anulada, sin borrarla.
3. Emite un movimiento de puntos de signo contrario que apunta al original.
4. Invalida las constancias emitidas a partir de ella y lo informa.
5. Registra la anulación en bitácora.

!!! example "**Alternativas**"

    === "**4a**"

        **La participación pertenece a un año ya cerrado**

        La anulación se admite y el indicador cerrado no cambia. La diferencia
        aparece como corrección posterior al cierre, por [`RN-18`][rn-18].

- **Postcondición:** La participación consta como anulada y sus efectos están revertidos.

---

## Puntos y constancias

### CU-A-17

> **Definir el baremo de puntuación**

- **Actor:** [Administrador DIEM][act-admin]
- **Precondición:** Sesión abierta
- **Requerimientos:**
  > - [`RF-A-30`][rf-a-30]

**Flujo principal**

1. El administrador declara la combinación de tipo de actividad, rol y desenlace.
2. Introduce los puntos y la fecha desde la cual rige.
3. El sistema cierra la vigencia de la regla anterior equivalente y activa la nueva.
4. Los movimientos ya generados no cambian.

!!! example "**Alternativas**"

    === "**3a**"

        **La nueva vigencia se solapa con otra regla equivalente**

        El sistema lo rechaza. Dos reglas vigentes para la misma combinación
        harían indeterminado el puntaje.

- **Postcondición:** El baremo nuevo rige para las validaciones futuras.

### CU-A-18

> **Emitir una constancia**

- **Actor:** [Administrador DIEM][act-admin]
- **Precondición:** Existe al menos una participación validada de la persona
- **Requerimientos:**
  > - [`RF-A-35`][rf-a-35]
  > - [`RF-P-23`][rf-p-23]

**Flujo principal**

1. El administrador elige a la persona, la plantilla y las participaciones a amparar.
2. El sistema comprueba que todas estén validadas.
3. Genera el folio, congela nombre, identificador, actividades, fechas y roles, y produce el código de verificación.
4. Notifica a la persona y registra la emisión.

!!! example "**Alternativas**"

    === "**2a**"

        **Alguna participación seleccionada no está validada**

        El sistema rechaza la emisión y señala cuál, por [`RN-15`][rn-15].

    === "**3a**"

        **La persona cambió su nombre después de participar**

        La constancia congela el nombre vigente al momento de emitirse, no el que
        tenía al participar. Una constancia debe poder contrastarse contra el
        documento de identidad actual de quien la presenta.

- **Postcondición:** Existe una constancia con folio único y verificable.

### CU-A-19

> **Anular una constancia**

- **Actor:** [Administrador DIEM][act-admin]
- **Precondición:** La constancia está emitida
- **Requerimientos:**
  > - [`RF-A-36`][rf-a-36]

**Flujo principal**

1. El administrador selecciona el motivo.
2. El sistema marca la constancia como anulada.
3. La verificación pública de ese folio pasa a informar que dejó de tener validez.
4. Si corresponde, el administrador reemite, generando un folio nuevo que apunta al anulado.

- **Postcondición:** El folio anulado nunca vuelve a usarse y su estado es público.

---

## Portafolio

### CU-A-20

> **Registrar una propuesta en el portafolio**

- **Actor:** [Administrador DIEM][act-admin]
- **Precondición:** Existe la actividad de origen
- **Requerimientos:**
  > - [`RF-A-37`][rf-a-37]
  > - [`RF-A-38`][rf-a-38]
  > - [`RF-A-39`][rf-a-39]
  > - [`RF-A-40`][rf-a-40]

**Flujo principal**

1. El administrador introduce nombre, actividad de origen, problema, solución, usuario beneficiario y adoptante.
2. Clasifica la propuesta en lo que ya sea evaluable y deja el resto como por determinar.
3. Vincula a los integrantes desde el directorio de personas.
4. El sistema genera el código correlativo del año de ingreso y crea la propuesta.

!!! example "**Alternativas**"

    === "**2a**"

        **No hay evidencia para asignar madurez tecnológica o de mercado**

        Se registra como por determinar. Registrar un nivel planificado en lugar
        del demostrado hace inservible todo el indicador.

    === "**3a**"

        **Un integrante no está en el directorio**

        Se ejecuta [`CU-A-03`](#cu-a-03) antes de continuar. El portafolio no
        guarda nombres sueltos: guarda vínculos a personas.

- **Postcondición:** La propuesta existe con código estable y es citable desde las participaciones.

### CU-A-21

> **Actualizar la etapa de una propuesta**

- **Actor:** [Administrador DIEM][act-admin]
- **Precondición:** La propuesta existe
- **Requerimientos:**
  > - [`RF-A-41`][rf-a-41]

**Flujo principal**

1. El administrador cambia la etapa de desarrollo, el estado en el portafolio o alguna clasificación.
2. El sistema comprueba que la transición esté declarada como legal.
3. Guarda el valor nuevo y añade una entrada a la trayectoria con el valor anterior, la fecha y su cuenta.

!!! example "**Alternativas**"

    === "**1a**"

        **La propuesta avanza de etapa pero queda en pausa**

        Son dimensiones distintas y se registran por separado: una propuesta
        puede estar en incubación y en pausa a la vez.

- **Postcondición:** La clasificación vigente cambió y su historial lo explica.

---

## Sistema

### CU-A-22

> **Importar una matriz histórica**

- **Actor:** [Administrador DIEM][act-admin]
- **Precondición:** Sesión abierta y archivo conforme a la plantilla
- **Requerimientos:**
  > - [`RF-A-49`][rf-a-49]

**Flujo principal**

1. El administrador carga el archivo e indica de qué matriz se trata.
2. El sistema valida cada fila con las mismas reglas del alta manual y produce un resumen de altas, actualizaciones y rechazos con su motivo.
3. El administrador revisa el resumen y confirma.
4. El sistema aplica los cambios y guarda el detalle fila por fila.

!!! example "**Alternativas**"

    === "**2a**"

        **Una fila repite un identificador ya presente en el archivo**

        El sistema la rechaza señalando la fila anterior, sin abortar el resto de
        la carga.

    === "**2b**"

        **Una fila trae una carrera o institución que no está en el catálogo**

        Queda rechazada con ese motivo. La importación no crea catálogos: eso
        convertiría cada error de escritura en una entrada nueva.

    === "**3a**"

        **El archivo carece de la autorización de tratamiento de datos**

        Las personas se crean con consentimiento pendiente de verificar y quedan
        fuera de los reportes nominales hasta resolverlo.

- **Postcondición:** Los datos históricos quedan en el sistema con rastro de su origen.

[act-admin]: ../actores/administracion.md#administrador-diem
[act-proceso]: ../actores/index.md#proceso-programado
[r-04]: ../modelo-dominio/riesgos.md#r-04
[rf-a-01]: ../requerimientos/funcionales/administracion.md#rf-a-01
[rf-a-02]: ../requerimientos/funcionales/administracion.md#rf-a-02
[rf-a-03]: ../requerimientos/funcionales/administracion.md#rf-a-03
[rf-a-06]: ../requerimientos/funcionales/administracion.md#rf-a-06
[rf-a-07]: ../requerimientos/funcionales/administracion.md#rf-a-07
[rf-a-08]: ../requerimientos/funcionales/administracion.md#rf-a-08
[rf-a-09]: ../requerimientos/funcionales/administracion.md#rf-a-09
[rf-a-15]: ../requerimientos/funcionales/administracion.md#rf-a-15
[rf-a-16]: ../requerimientos/funcionales/administracion.md#rf-a-16
[rf-a-17]: ../requerimientos/funcionales/administracion.md#rf-a-17
[rf-a-18]: ../requerimientos/funcionales/administracion.md#rf-a-18
[rf-a-19]: ../requerimientos/funcionales/administracion.md#rf-a-19
[rf-a-20]: ../requerimientos/funcionales/administracion.md#rf-a-20
[rf-a-21]: ../requerimientos/funcionales/administracion.md#rf-a-21
[rf-a-23]: ../requerimientos/funcionales/administracion.md#rf-a-23
[rf-a-24]: ../requerimientos/funcionales/administracion.md#rf-a-24
[rf-a-25]: ../requerimientos/funcionales/administracion.md#rf-a-25
[rf-a-26]: ../requerimientos/funcionales/administracion.md#rf-a-26
[rf-a-27]: ../requerimientos/funcionales/administracion.md#rf-a-27
[rf-a-29]: ../requerimientos/funcionales/administracion.md#rf-a-29
[rf-a-30]: ../requerimientos/funcionales/administracion.md#rf-a-30
[rf-a-31]: ../requerimientos/funcionales/administracion.md#rf-a-31
[rf-a-33]: ../requerimientos/funcionales/administracion.md#rf-a-33
[rf-a-35]: ../requerimientos/funcionales/administracion.md#rf-a-35
[rf-a-36]: ../requerimientos/funcionales/administracion.md#rf-a-36
[rf-a-37]: ../requerimientos/funcionales/administracion.md#rf-a-37
[rf-a-38]: ../requerimientos/funcionales/administracion.md#rf-a-38
[rf-a-39]: ../requerimientos/funcionales/administracion.md#rf-a-39
[rf-a-40]: ../requerimientos/funcionales/administracion.md#rf-a-40
[rf-a-41]: ../requerimientos/funcionales/administracion.md#rf-a-41
[rf-a-43]: ../requerimientos/funcionales/administracion.md#rf-a-43
[rf-a-49]: ../requerimientos/funcionales/administracion.md#rf-a-49
[rf-p-18]: ../requerimientos/funcionales/participantes.md#rf-p-18
[rf-p-23]: ../requerimientos/funcionales/participantes.md#rf-p-23
[rf-p-27]: ../requerimientos/funcionales/participantes.md#rf-p-27
[rn-15]: ../requerimientos/reglas-negocio.md#rn-15
[rn-18]: ../requerimientos/reglas-negocio.md#rn-18
