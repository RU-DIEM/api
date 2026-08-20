---
icon: lucide/users-round
---

# Portal del participante

- **Módulos:** 5
- **Total:** 15

---

## Acceso

### CU-P-01

> **Explorar el catálogo sin cuenta**

- **Actor:** [Visitante][act-visitante]
- **Precondición:** Ninguna
- **Requerimientos:**
  > - [`RF-P-14`][rf-p-14]
  > - [`RF-P-15`][rf-p-15]

**Flujo principal**

1. El visitante abre el catálogo y ve las actividades publicadas con sus fechas, cupo restante y puntos.
2. Filtra por tipo, modalidad o programa.
3. Abre la ficha de una actividad y ve descripción, requisitos, responsables y mentores confirmados.

!!! example "**Alternativas**"

    === "**3a**"

        **Intenta inscribirse**

        El sistema le pide registrarse conservando la actividad seleccionada, y
        lo lleva de vuelta a ella al terminar el registro.

- **Postcondición:** Ninguna. El catálogo es de solo lectura.

### CU-P-02

> **Registrarse como estudiante UAM**

- **Actor:** [Visitante][act-visitante]
- **Precondición:** La persona no tiene cuenta
- **Requerimientos:**
  > - [`RF-P-01`][rf-p-01]
  > - [`RF-P-02`][rf-p-02]
  > - [`RF-P-03`][rf-p-03]
  > - [`RF-P-07`][rf-p-07]
  > - [`RF-P-08`][rf-p-08]

**Flujo principal**

1. El visitante elige el perfil de estudiante UAM.
2. Introduce su CIF, datos personales, correo institucional y contraseña.
3. Elige carrera y año; el sistema deriva la facultad de la carrera.
4. Lee el aviso de privacidad vigente y otorga su consentimiento.
5. El sistema crea la cuenta, guarda la versión del aviso aceptada y envía el enlace de verificación.

!!! example "**Alternativas**"

    === "**2a**"

        **El CIF ya está registrado**

        El sistema informa que ese identificador ya existe y ofrece recuperar el
        acceso de la cuenta existente. No crea una cuenta nueva.

    === "**2b**"

        **El correo no pertenece al dominio institucional**

        El sistema lo rechaza para este perfil e indica que un correo personal
        corresponde al perfil de participante externo.

    === "**4a**"

        **La persona no otorga el consentimiento**

        El sistema no crea la cuenta y explica que sin autorización no puede
        registrar sus datos ni su participación.

- **Postcondición:** Existe una cuenta pendiente de verificación de correo.

### CU-P-03

> **Registrarse como participante externo**

- **Actor:** [Visitante][act-visitante]
- **Precondición:** La persona no tiene cuenta
- **Requerimientos:**
  > - [`RF-P-01`][rf-p-01]
  > - [`RF-P-02`][rf-p-02]
  > - [`RF-P-10`][rf-p-10]

**Flujo principal**

1. El visitante elige el perfil de participante externo.
2. Introduce cédula, pasaporte o carné de residencia, datos personales, correo y contraseña.
3. Elige su institución de procedencia del catálogo y describe a qué se dedica.
4. Otorga el consentimiento y el sistema crea la cuenta.

!!! example "**Alternativas**"

    === "**3a**"

        **Su institución no está en el catálogo**

        El sistema admite capturarla como texto nuevo y la marca como pendiente
        de normalización, para que la administración la unifique después con sus
        variantes de escritura.

    === "**3b**"

        **Es estudiante de otra universidad**

        El formulario pide además su carrera como texto libre, porque el catálogo
        institucional solo cubre las carreras de la UAM.

- **Postcondición:** Existe una cuenta pendiente de verificación de correo.

### CU-P-04

> **Verificar el correo electrónico**

- **Actor:** [Participante][act-participante]
- **Precondición:** Existe una cuenta con correo sin verificar
- **Requerimientos:**
  > - [`RF-P-04`][rf-p-04]

**Flujo principal**

1. La persona abre el enlace recibido.
2. El sistema marca el correo como verificado con su instante y consume el enlace.
3. La cuenta queda habilitada para inscribirse.

!!! example "**Alternativas**"

    === "**1a**"

        **El enlace expiró**

        El sistema ofrece reenviar, con un límite de intentos por hora.

    === "**1b**"

        **El enlace ya se usó**

        El sistema informa que la cuenta ya está verificada y lleva al inicio de
        sesión. Un enlace de un solo uso no se canjea dos veces.

- **Postcondición:** El correo consta verificado con fecha.

### CU-P-05

> **Recuperar el acceso**

- **Actor:** [Participante][act-participante]
- **Precondición:** La cuenta existe y tiene correo verificado
- **Requerimientos:**
  > - [`RF-P-05`][rf-p-05]

**Flujo principal**

1. La persona introduce su correo o su identificador.
2. El sistema envía un enlace de un solo uso de vigencia corta al correo verificado.
3. La persona define una contraseña nueva.
4. El sistema invalida las sesiones abiertas de esa cuenta.

!!! example "**Alternativas**"

    === "**1a**"

        **El correo no corresponde a ninguna cuenta**

        El sistema responde igual que en el caso exitoso, sin revelar si la
        cuenta existe.

    === "**1b**"

        **La cuenta se creó desde administración y nunca tuvo contraseña**

        El flujo sirve igual: es la vía por la que una persona registrada en
        papel activa su acceso.

- **Postcondición:** La persona recupera el acceso y las sesiones previas quedan cerradas.

---

## Perfil

### CU-P-06

> **Declarar una segunda carrera**

- **Actor:** [Estudiante UAM][act-estudiante]
- **Precondición:** Sesión abierta y carrera principal declarada
- **Requerimientos:**
  > - [`RF-P-09`][rf-p-09]

**Flujo principal**

1. El estudiante agrega una carrera desde su perfil académico.
2. Elige la carrera, que puede ser de otra facultad, e indica el año que cursa.
3. El sistema la registra como carrera no principal, sin duplicar datos personales.

!!! example "**Alternativas**"

    === "**2a**"

        **Elige una carrera que ya tiene declarada**

        El sistema lo rechaza.

    === "**3a**"

        **Quiere que la segunda pase a ser la principal**

        El sistema traslada la marca de principal a la carrera elegida y la
        retira de la anterior en la misma operación, porque exactamente una debe
        tenerla.

- **Postcondición:** El estudiante cuenta en los reportes de ambas carreras y una vez en el total general.

### CU-P-07

> **Confirmar la vigencia de los datos**

- **Actor:** [Participante][act-participante]
- **Precondición:** El perfil superó el período de vigencia
- **Requerimientos:**
  > - [`RF-P-13`][rf-p-13]

**Flujo principal**

1. Al iniciar sesión, el sistema pide revisar los datos personales y académicos.
2. La persona los corrige o los confirma sin cambios.
3. El sistema actualiza la fecha de última confirmación en ambos casos.

!!! example "**Alternativas**"

    === "**1a**"

        **La persona pospone la revisión**

        Puede continuar usando el portal. El aviso reaparece en el siguiente
        ingreso y su perfil consta como desactualizado en el directorio.

- **Postcondición:** El perfil consta revisado en una fecha, con o sin cambios.

---

## Actividades

### CU-P-08

> **Inscribirse en una actividad**

- **Actor:** [Participante][act-participante]
- **Precondición:** Correo verificado, consentimiento vigente y ventana abierta
- **Requerimientos:**
  > - [`RF-P-16`][rf-p-16]
  > - [`RF-P-17`][rf-p-17]

**Flujo principal**

1. La persona abre la ficha de la actividad y confirma su inscripción.
2. El sistema comprueba cupo, ventana y ausencia de inscripción previa.
3. Crea la inscripción con su instante y muestra el resultado.

!!! example "**Alternativas**"

    === "**2a**"

        **Ya está inscrita**

        El sistema muestra el estado de la inscripción existente en lugar de
        crear otra.

    === "**2b**"

        **La actividad alcanzó el cupo**

        El sistema ofrece lista de espera si la actividad la tiene habilitada, y
        si no, informa que no hay lugares.

    === "**2c**"

        **La cuenta no tiene el correo verificado**

        El sistema lo impide y ofrece reenviar el enlace de verificación.

    === "**2d**"

        **El consentimiento fue retirado**

        El sistema lo impide y explica que la inscripción requiere autorización
        vigente para el tratamiento de sus datos.

- **Postcondición:** La persona consta inscrita, con lugar o en lista de espera.

### CU-P-09

> **Cancelar la propia inscripción**

- **Actor:** [Participante][act-participante]
- **Precondición:** La inscripción está viva y la ventana abierta
- **Requerimientos:**
  > - [`RF-P-19`][rf-p-19]

**Flujo principal**

1. La persona cancela desde su listado de inscripciones e indica un motivo de lista cerrada.
2. El sistema cancela la inscripción y libera el cupo.
3. Se dispara la promoción desde lista de espera de [`CU-A-13`][cu-a-13].

!!! example "**Alternativas**"

    === "**1a**"

        **La participación ya fue validada**

        El sistema lo impide. Lo que ocurrió no se cancela desde el portal:
        corregirlo es una anulación administrativa.

    === "**1b**"

        **La ventana de inscripción ya cerró**

        El sistema lo impide y le indica que se comunique con la DIEM, para que
        la ausencia quede registrada como tal y no como una baja silenciosa.

- **Postcondición:** El cupo queda libre y la cancelación tiene motivo.

### CU-P-10

> **Crear o unirse a un equipo**

- **Actor:** [Estudiante UAM][act-estudiante], [Participante externo][act-externo]
- **Precondición:** Inscripción viva en una actividad que admite equipos
- **Requerimientos:**
  > - [`RF-P-20`][rf-p-20]

**Flujo principal**

1. La persona crea un equipo con su nombre o introduce el código de uno existente.
2. El sistema valida el tamaño máximo declarado por la actividad.
3. La incorpora al equipo y muestra a sus integrantes.

!!! example "**Alternativas**"

    === "**1a**"

        **Ya pertenece a un equipo de esa actividad**

        El sistema lo rechaza y le muestra su equipo actual.

    === "**2a**"

        **El equipo alcanzó el máximo**

        El sistema lo rechaza e informa el tamaño máximo.

    === "**3a**"

        **La inscripción cerró**

        La composición queda fijada y la persona ya no puede cambiar de equipo
        desde el portal.

- **Postcondición:** La persona pertenece a un equipo y su participación podrá citarlo.

---

## Historial

### CU-P-11

> **Consultar el historial y los puntos**

- **Actor:** [Participante][act-participante]
- **Precondición:** Sesión abierta
- **Requerimientos:**
  > - [`RF-P-21`][rf-p-21]
  > - [`RF-P-22`][rf-p-22]
  > - [`RF-P-25`][rf-p-25]

**Flujo principal**

1. La persona abre su historial.
2. El sistema muestra sus actividades con año, programa, edición, rol, equipo, estado, resultado y puntos, distinguiendo lo inscrito de lo validado.
3. Muestra el saldo de puntos y el detalle de cada movimiento con la regla que lo originó.

!!! example "**Alternativas**"

    === "**2a**"

        **Tiene inscripciones sin participación validada**

        Aparecen como inscritas y sin puntos, con una nota que explica que la
        validación la hace la DIEM después de la actividad.

    === "**3a**"

        **Tiene un movimiento anulado**

        Aparece el movimiento original y su reverso, ambos visibles. El saldo
        cuadra con la suma de lo mostrado.

- **Postcondición:** Ninguna. Es una consulta, y queda registrada como acceso a datos propios.

### CU-P-12

> **Solicitar una constancia**

- **Actor:** [Participante][act-participante]
- **Precondición:** Tiene al menos una participación validada
- **Requerimientos:**
  > - [`RF-P-23`][rf-p-23]

**Flujo principal**

1. La persona abre la solicitud y ve qué participaciones son elegibles.
2. Selecciona una o varias y confirma.
3. El sistema registra la solicitud y la envía al administrador.
4. Al emitirse, la persona recibe aviso y puede descargarla.

!!! example "**Alternativas**"

    === "**1a**"

        **Ninguna participación es elegible**

        El sistema lo explica indicando el motivo de cada una: pendiente de
        validación, retirada o no completada.

- **Postcondición:** Existe una solicitud pendiente de emisión.

### CU-P-13

> **Verificar una constancia por folio**

- **Actor:** [Visitante][act-visitante]
- **Precondición:** Ninguna
- **Requerimientos:**
  > - [`RF-P-24`][rf-p-24]

**Flujo principal**

1. El visitante introduce el folio y el código de verificación.
2. El sistema confirma la validez y muestra el nombre, las actividades amparadas y la fecha de emisión.

!!! example "**Alternativas**"

    === "**2a**"

        **La constancia está anulada**

        El sistema informa que ese folio dejó de tener validez, sin exponer el
        motivo de la anulación.

    === "**2b**"

        **El folio no existe o el código no corresponde**

        El sistema responde que no se encontró, sin distinguir entre ambos casos
        y sin permitir listar ni buscar constancias.

- **Postcondición:** Ninguna. La verificación no revela más de lo que la propia constancia ya declara.

### CU-P-14

> **Descargar los datos propios**

- **Actor:** [Participante][act-participante]
- **Precondición:** Sesión abierta
- **Requerimientos:**
  > - [`RF-P-26`][rf-p-26]

**Flujo principal**

1. La persona solicita la descarga desde su perfil.
2. El sistema genera un archivo tabular con datos personales, perfiles, inscripciones, participaciones, puntos, constancias y vínculos de portafolio.
3. Registra la descarga como acceso a datos personales.

- **Postcondición:** La persona obtiene todo lo que el sistema guarda sobre ella.

---

## Mentoría

### CU-P-15

> **Aceptar una invitación de mentoría**

- **Actor:** [Mentor][act-mentor]
- **Precondición:** Existe una asignación en estado propuesta
- **Requerimientos:**
  > - [`RF-P-27`][rf-p-27]
  > - [`RF-P-29`][rf-p-29]

**Flujo principal**

1. El mentor abre la asignación propuesta y ve la actividad, las fechas y el tipo de acompañamiento.
2. La acepta.
3. El sistema la marca como confirmada y publica al mentor en la ficha de la actividad.
4. Terminada la actividad, el mentor registra sus observaciones y el enlace de evidencia.

!!! example "**Alternativas**"

    === "**2a**"

        **La declina**

        Indica el motivo. La asignación queda declinada y no aparece en la ficha
        pública.

    === "**4a**"

        **Registra observaciones sobre un equipo**

        Son visibles para la administración y para él mismo, nunca para los demás
        participantes ni para el equipo observado.

- **Postcondición:** El acompañamiento consta confirmado y, al cierre, documentado.

[act-estudiante]: ../actores/participantes.md#estudiante-uam
[act-externo]: ../actores/participantes.md#participante-externo
[act-mentor]: ../actores/participantes.md#mentor
[act-participante]: ../actores/participantes.md#participante
[act-visitante]: ../actores/participantes.md#visitante
[cu-a-13]: administracion.md#cu-a-13
[rf-p-01]: ../requerimientos/funcionales/participantes.md#rf-p-01
[rf-p-02]: ../requerimientos/funcionales/participantes.md#rf-p-02
[rf-p-03]: ../requerimientos/funcionales/participantes.md#rf-p-03
[rf-p-04]: ../requerimientos/funcionales/participantes.md#rf-p-04
[rf-p-05]: ../requerimientos/funcionales/participantes.md#rf-p-05
[rf-p-07]: ../requerimientos/funcionales/participantes.md#rf-p-07
[rf-p-08]: ../requerimientos/funcionales/participantes.md#rf-p-08
[rf-p-09]: ../requerimientos/funcionales/participantes.md#rf-p-09
[rf-p-10]: ../requerimientos/funcionales/participantes.md#rf-p-10
[rf-p-13]: ../requerimientos/funcionales/participantes.md#rf-p-13
[rf-p-14]: ../requerimientos/funcionales/participantes.md#rf-p-14
[rf-p-15]: ../requerimientos/funcionales/participantes.md#rf-p-15
[rf-p-16]: ../requerimientos/funcionales/participantes.md#rf-p-16
[rf-p-17]: ../requerimientos/funcionales/participantes.md#rf-p-17
[rf-p-19]: ../requerimientos/funcionales/participantes.md#rf-p-19
[rf-p-20]: ../requerimientos/funcionales/participantes.md#rf-p-20
[rf-p-21]: ../requerimientos/funcionales/participantes.md#rf-p-21
[rf-p-22]: ../requerimientos/funcionales/participantes.md#rf-p-22
[rf-p-23]: ../requerimientos/funcionales/participantes.md#rf-p-23
[rf-p-24]: ../requerimientos/funcionales/participantes.md#rf-p-24
[rf-p-25]: ../requerimientos/funcionales/participantes.md#rf-p-25
[rf-p-26]: ../requerimientos/funcionales/participantes.md#rf-p-26
[rf-p-27]: ../requerimientos/funcionales/participantes.md#rf-p-27
[rf-p-29]: ../requerimientos/funcionales/participantes.md#rf-p-29
