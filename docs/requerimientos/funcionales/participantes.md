---
icon: lucide/users-round
---

# Portal del participante

- **Módulos:** 5
- **Total:** 29

---

## Acceso

### RF-P-01

> **Registro autoservicio**

Formulario público de registro que exige elegir el perfil con el que la persona
entra: estudiante UAM, estudiante o participante externo, docente o mentor. El
perfil elegido determina qué campos adicionales se piden y no puede quedar
vacío. Una persona puede añadir después otros perfiles a la misma cuenta sin
volver a registrarse.

### RF-P-02

> **Identificador único obligatorio**

Todo registro exige al menos un identificador: CIF para el estudiante UAM y
cédula, pasaporte o carné de residencia para los demás perfiles. El estudiante
UAM puede declarar además su cédula. Si el identificador ya existe en el sistema,
el formulario no crea una cuenta nueva: informa que ese identificador ya está
registrado y ofrece recuperar el acceso de la cuenta existente.

### RF-P-03

> **Correo institucional del estudiante UAM**

El registro con perfil de estudiante UAM exige un correo del dominio
institucional. El dominio aceptado es un parámetro del sistema y no una constante
del código. Los demás perfiles admiten correo personal o institucional de su
propia organización. Una persona con perfil de estudiante UAM y perfil externo
tiene un solo correo de contacto y ese correo debe ser el institucional.

### RF-P-04

> **Verificación del correo**

El alta envía un enlace de un solo uso con vigencia parametrizable. Hasta que el
correo esté verificado la cuenta puede consultar el catálogo pero no inscribirse.
El sistema permite reenviar el enlace con un límite de intentos por hora. El
instante de verificación queda registrado, porque un correo verificado hace tres
años sobre una cuenta inactiva no prueba lo mismo que uno verificado ayer.

### RF-P-05

> **Inicio de sesión y recuperación**

Inicio de sesión con correo o identificador más contraseña. Recuperación por
enlace de un solo uso enviado al correo verificado, con vigencia corta. Cambiar
la contraseña invalida las sesiones abiertas. La sesión del portal del
participante tiene una vigencia más larga que la administrativa, definida como
parámetro.

---

## Perfil

### RF-P-06

> **Datos personales y de contacto**

Nombres, apellidos, fecha de nacimiento, sexo, etnia autodeclarada, número de
WhatsApp con código de país, correo electrónico y talla de camiseta. El sexo y la
etnia son autodeclarados y el formulario lo indica: nunca se infieren del nombre,
la procedencia ni la apariencia. La talla se pide porque las actividades entregan
indumentaria, y el formulario lo explica en lugar de pedirla sin motivo.

### RF-P-07

> **Consentimiento de tratamiento de datos**

El registro presenta el aviso de privacidad vigente y exige una decisión
explícita antes de guardar. El sistema almacena la versión concreta del aviso que
la persona aceptó, el instante y el canal. Sin consentimiento vigente la cuenta
existe pero no aparece en reportes nominales ni recibe comunicaciones no
esenciales. La persona puede retirar el consentimiento desde su perfil, lo que
inicia el proceso de baja descrito en [`RF-A-50`][rf-a-50].

### RF-P-08

> **Perfil académico del estudiante UAM**

Facultad, carrera y año actual de la carrera. La carrera se elige del catálogo
institucional y determina la facultad, que no se captura por separado para que no
puedan contradecirse. El año de carrera admite el valor de egresado, porque un
egresado sigue participando en actividades de la DIEM y sigue apareciendo en los
reportes.

### RF-P-09

> **Segunda carrera o doble titulación**

El estudiante puede declarar una segunda carrera, de la misma facultad o de otra,
sin duplicar sus datos personales. Cada carrera declarada lleva su propio año y
su propia marca de principal. El sistema impide declarar dos veces la misma
carrera y exige que exactamente una esté marcada como principal.

### RF-P-10

> **Perfil de participante externo**

Institución de procedencia elegida del catálogo o capturada como texto nuevo, y
descripción de a qué se dedica: estudiante de otra institución, emprendedor,
profesional independiente, colaborador de una empresa u otro perfil. Cuando la
persona es estudiante de otra universidad, el formulario pide además su carrera
como texto libre, ya que el catálogo institucional solo cubre la UAM.

### RF-P-11

> **Perfil de docente**

Vinculación con la UAM, facultad o facultades a las que está adscrito y nivel
académico. Un docente puede además tener perfil de mentor, y el sistema no lo
obliga a elegir entre uno y otro.

### RF-P-12

> **Perfil de mentor**

Nivel académico, descripción profesional, áreas de experiencia elegidas de un
catálogo, certificaciones nacionales o internacionales con institución y año,
necesidades de formación declaradas y municipio. El perfil de mentor no se
autoasigna: la persona lo solicita y la DIEM lo confirma, porque acompañar a un
equipo en nombre de la Dirección es una designación institucional.

### RF-P-13

> **Vigencia de los datos**

Cada perfil registra la fecha de su última actualización confirmada. Transcurrido
el período definido como parámetro, el sistema pide a la persona revisar sus
datos al iniciar sesión, con opción de confirmarlos sin cambios. Confirmar sin
cambios actualiza la fecha: el dato relevante es cuándo se verificó, no cuándo se
modificó.

---

## Actividades

### RF-P-14

> **Catálogo de actividades abiertas**

Listado público de las actividades publicadas, con nombre, programa, tipo,
modalidad, fechas, lugar, cupo restante y puntos que otorga. Filtros por tipo,
modalidad y programa. Visible sin cuenta, porque exigir registro para ver qué
ofrece la DIEM reduce la participación que el sistema existe para medir.

### RF-P-15

> **Ficha de la actividad**

Descripción completa, requisitos, responsables, mentores confirmados, ventana de
inscripción y condición de participación en equipo. Indica si la persona ya está
inscrita y en qué estado.

### RF-P-16

> **Inscripción**

Una acción desde la ficha, disponible solo con la cuenta verificada y el
consentimiento otorgado. La inscripción registra el instante y queda pendiente o
confirmada según lo que defina la actividad. El sistema muestra de inmediato el
resultado, incluida la posición en lista de espera cuando corresponde.

### RF-P-17

> **Inscripción única por actividad**

Una persona no puede inscribirse dos veces en la misma actividad. Si ya está
inscrita, el sistema conserva la inscripción existente y muestra su estado en
lugar de crear otra. Una inscripción cancelada por la propia persona sí puede
rehacerse mientras la ventana siga abierta y quede cupo.

### RF-P-18

> **Cupo y lista de espera**

Cuando la actividad alcanza su cupo, el sistema deja de admitir inscripciones y
ofrece lista de espera si la actividad la tiene habilitada. La persona ve su
posición. Al liberarse un lugar, el primero de la lista es promovido y
notificado. La promoción es automática y en orden de llegada, sin intervención
administrativa.

### RF-P-19

> **Cancelación de la inscripción**

La persona cancela su propia inscripción mientras la ventana esté abierta,
indicando un motivo de lista cerrada. Una inscripción cuya participación ya fue
validada no puede cancelarse desde el portal. La cancelación libera el cupo de
inmediato.

### RF-P-20

> **Equipo de trabajo**

En las actividades que lo requieren, la persona crea un equipo o se une a uno
existente mediante un código que comparte quien lo creó. El sistema respeta el
tamaño mínimo y máximo declarados por la actividad e impide pertenecer a más de
un equipo por actividad. Al cerrarse la inscripción, la composición queda fijada.

---

## Historial

### RF-P-21

> **Historial de participación**

Listado de todas las actividades en las que la persona participó, con año,
programa, actividad, edición, rol desempeñado, equipo, fechas, estado de la
participación, resultado y puntos obtenidos. Distingue visualmente lo inscrito de
lo validado, porque son cosas distintas y la persona necesita saber cuál tiene.

### RF-P-22

> **Puntos de innovación**

Saldo acumulado y detalle de cada movimiento, con la actividad que lo originó, la
fecha y la regla aplicada. Los ajustes manuales y los reversos aparecen
explicados. El saldo es la suma de los movimientos vivos y el detalle siempre
cuadra con él.

### RF-P-23

> **Solicitud de constancia**

La persona solicita constancia de una participación validada o un consolidado de
varias. El sistema muestra qué participaciones son elegibles y cuáles no, con el
motivo. La solicitud llega al administrador para su emisión.

### RF-P-24

> **Verificación pública de una constancia**

Página pública que, dado un folio y su código de verificación, confirma si la
constancia es válida y muestra el nombre de la persona, las actividades que
ampara y la fecha de emisión. Una constancia anulada se informa como anulada. La
página no permite listar ni buscar constancias: solo verificar una concreta.

### RF-P-25

> **Aislamiento del historial**

Cada persona ve únicamente su propio historial, sus puntos y sus constancias.
Ninguna vista del portal del participante expone datos de terceros, con la única
excepción del nombre de los integrantes del propio equipo dentro de una actividad
compartida.

### RF-P-26

> **Descarga de los datos propios**

La persona descarga en formato tabular todo lo que el sistema guarda sobre ella:
datos personales, perfiles, inscripciones, participaciones, puntos, constancias y
vínculos de portafolio. La descarga queda registrada como cualquier otro acceso a
datos personales.

---

## Mentoría

### RF-P-27

> **Invitación a acompañar una actividad**

El mentor recibe la asignación propuesta por la DIEM y la acepta o la declina
indicando motivo. Mientras no responda, la asignación consta como propuesta y no
aparece como mentor confirmado en la ficha pública de la actividad.

### RF-P-28

> **Agenda de acompañamiento**

Listado de las actividades que el mentor acompaña o acompañó, con fechas, equipos
asignados y estado de cada asignación. Es la vista equivalente al historial de
participación, orientada al rol de acompañamiento.

### RF-P-29

> **Registro del aporte del mentor**

El mentor registra observaciones sobre los equipos que acompañó y adjunta el
enlace de evidencia de su acompañamiento. Estas observaciones son visibles para
la administración y para el propio mentor, nunca para los demás participantes.

[rf-a-50]: administracion.md#rf-a-50
