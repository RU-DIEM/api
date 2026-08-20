---
icon: lucide/folder-lock
---

# Portal de administración

- **Módulos:** 11
- **Total:** 50

---

## Plataforma

### RF-A-01

> **Acceso separado y sin registro público**

Panel alojado en una ruta propia, sin formulario de registro y sin enlace desde
el portal del participante. Las cuentas administrativas se crean únicamente desde
el propio panel por otra cuenta administrativa activa, mediante invitación con
enlace de un solo uso y vigencia de setenta y dos horas. Una invitación no puede
otorgar a la vez rol administrativo y perfil de participante: son dos ámbitos que
no se mezclan en una misma alta.

### RF-A-02

> **Autenticación reforzada**

Contraseña de al menos doce caracteres con mayúscula, minúscula, número y
símbolo. La sesión administrativa expira por inactividad a los treinta minutos,
plazo independiente del que rige en el portal del participante. Bloqueo de
treinta minutos tras cinco intentos fallidos consecutivos. Cada intento queda
registrado con el identificador tecleado y la dirección de origen, tanto los
exitosos como los fallidos.

### RF-A-03

> **Alcance del rol administrador**

El piloto opera con un solo rol interno, que concentra la gestión de personas,
actividades, participación, puntos, constancias, portafolio, catálogos,
parámetros y reportes. El sistema impide la operación que dejaría la plataforma
sin ninguna cuenta administrativa activa, incluso cuando esa operación afecta a
varias cuentas a la vez. La estructura de roles queda declarada desde el
principio aunque solo se pueble con un valor, para que separar funciones más
adelante no obligue a migrar.

### RF-A-04

> **Bitácora de acciones administrativas**

Toda escritura hecha desde el panel queda registrada con la cuenta que la
ejecutó, el instante, la entidad afectada, la acción y el valor anterior. La
bitácora es de solo lectura desde la interfaz y no admite borrado por ningún
rol. Consultar el historial de una persona concreta también se registra, porque
es un acceso a datos personales y no una lectura de agregados.

---

## Personas

### RF-A-05

> **Directorio unificado de personas**

Listado único de todas las personas registradas, sin importar el perfil por el
que entraron. Columnas de identificador, nombre completo, perfiles asociados,
correo, cantidad de participaciones validadas, puntos acumulados y fecha de
última actualización de sus datos. Filtros por perfil, facultad, carrera,
institución de procedencia, año de participación y estado de la autorización de
tratamiento de datos. El buscador acepta identificador, nombre y correo, y es
insensible a mayúsculas y tildes.

### RF-A-06

> **Alta administrativa de una persona**

El administrador registra a una persona que no se registró por sí misma, lo que
ocurre en toda actividad presencial donde la inscripción se recogió en papel.
El alta exige los mismos campos obligatorios que el autoservicio salvo la
contraseña, y la cuenta queda sin credencial hasta que la persona la active. El
sistema marca el registro con su origen, de modo que un dato capturado por
terceros sea distinguible de uno declarado por su titular.

### RF-A-07

> **Detección de posible duplicado**

Antes de confirmar un alta, el sistema busca coincidencias por identificador
exacto, por correo normalizado y por similitud de nombre completo con fecha de
nacimiento igual. Si encuentra candidatos, muestra la ficha de cada uno con sus
participaciones y obliga a elegir entre usar el registro existente o declarar
expresamente que se trata de otra persona. La declaración queda en bitácora con
el nombre de quien la hizo.

### RF-A-08

> **Fusión de registros duplicados**

Cuando dos registros resultan ser la misma persona, el administrador designa uno
como conservado y otro como absorbido. El sistema traslada al conservado los
identificadores, perfiles, inscripciones, participaciones, puntos, constancias y
vínculos de portafolio del absorbido; deja el absorbido sin acceso y apuntando al
conservado; y registra la operación con ambos identificadores, el motivo y la
cuenta que la ejecutó. La fusión no borra nada y es consultable después. Si ambos
registros participaron en la misma actividad, el sistema conserva la
participación validada y anula la otra dejando constancia del reemplazo.

### RF-A-09

> **Verificación de identificadores**

Cada tipo de identificador tiene un patrón declarado que el sistema comprueba al
capturarlo: el CIF con el formato institucional vigente y la cédula nicaragüense
con sus catorce caracteres. Un identificador que no cumple el patrón se acepta
solo marcándolo como pendiente de verificación, nunca en silencio. Una misma
persona puede tener más de un identificador —un estudiante UAM tiene CIF y
cédula— y cualquiera de ellos vale para reconocerla.

### RF-A-10

> **Gestión de perfiles de una persona**

El administrador agrega, edita y retira los perfiles de una persona: estudiante
UAM, estudiante o participante externo, docente y mentor. Los perfiles son
acumulables, porque un docente puede ser mentor y un estudiante puede ser mentor
estudiantil. Retirar un perfil no borra las participaciones registradas bajo él:
las conserva y las sigue contando en los reportes del año en que ocurrieron.

### RF-A-11

> **Expediente del mentor**

Ficha con nivel académico, descripción profesional, áreas de experiencia,
certificaciones nacionales o internacionales con institución y año, necesidades
de formación declaradas, tipo de mentor y ubicación por municipio. Incluye el
historial de actividades en las que acompañó, con su rol en cada una, y el
resumen de en cuántas ediciones de cada programa ha participado.

---

## Estructura institucional

### RF-A-12

> **Catálogo de facultades y carreras**

Alta, edición y desactivación de facultades y de las carreras que dependen de
cada una. Una carrera pertenece a exactamente una facultad. Desactivar una
carrera impide asociarla a matrículas nuevas pero no altera las existentes ni las
retira de los reportes históricos. El catálogo no admite borrado: una carrera
citada por una sola matrícula es parte del historial académico del sistema.

### RF-A-13

> **Catálogo de instituciones externas**

Registro de las universidades, centros educativos, empresas y organizaciones de
procedencia de los participantes externos, con su nombre oficial y su tipo. El
alta admite capturarlas sobre la marcha durante un registro, con una marca de
pendiente de normalización que el administrador resuelve después fusionando las
variantes de escritura de una misma institución.

### RF-A-14

> **Catálogos operativos y demográficos**

Administración de las listas cerradas que alimentan los formularios: sexo, etnia
autodeclarada, talla de camiseta, nivel académico, año de carrera, rol dentro de
la actividad, tipo de actividad, tipo de mentor, tipo de reconocimiento, área de
experiencia y municipio. Cada entrada admite editar su etiqueta y desactivarla,
nunca borrarla. Agregar un valor nuevo no requiere despliegue.

---

## Actividades

### RF-A-15

> **Programas e iniciativas recurrentes**

Alta de los programas que se repiten año con año —Hackathon Nicaragua, Rally
Nacional de Innovación, Rally Latinoamericano, Programa PIA, Semillero,
diplomados— con su nombre oficial, su tipo por defecto y su estado. Un programa
no tiene fechas: las tienen sus ediciones. Esta separación es lo que permite
preguntar por la participación en Hackathon Nicaragua a lo largo de cuatro años
sin depender de que el nombre se haya escrito igual cada vez.

### RF-A-16

> **Alta de una actividad**

Cada actividad es una edición concreta y lleva nombre, descripción, programa al
que pertenece cuando aplica, etiqueta de edición o cohorte, tipo, modalidad,
lugar, fecha de inicio, fecha de finalización, cupo, ventana de inscripción,
responsables y puntaje base. Las actividades sin programa —una charla única, un
taller aislado— se registran igual, con el programa vacío.

### RF-A-17

> **Ciclo de vida de la actividad**

Estados de borrador, publicada, en curso, finalizada y cancelada, con las
transiciones legales declaradas como datos y no como código. Una actividad en
borrador no aparece en el catálogo público ni admite inscripciones. Cancelar una
actividad exige motivo, cancela sus inscripciones vivas y notifica a los
inscritos, pero no toca las participaciones ya validadas de ediciones anteriores.

### RF-A-18

> **Cupo y ventana de inscripción**

Cupo máximo opcional, fecha de apertura y fecha de cierre de inscripciones. El
sistema rechaza la inscripción que superaría el cupo y ofrece lista de espera
cuando la actividad la tiene habilitada. Ampliar el cupo promueve
automáticamente a los primeros de la lista de espera en orden de llegada y
notifica a cada uno. El administrador puede inscribir por encima del cupo
dejando registrada la excepción.

### RF-A-19

> **Responsables de la actividad**

Una o varias personas de la DIEM designadas como responsables, con su rol
—coordinación, facilitación, logística—. Aparecen en la ficha pública de la
actividad y en los reportes de carga de trabajo por período.

### RF-A-20

> **Asignación de mentores**

Vinculación de una persona con perfil de mentor a una actividad, con el tipo de
acompañamiento que brindará y, cuando aplica, el equipo concreto que acompaña. La
asignación tiene su propio ciclo: propuesta, confirmada, declinada, finalizada o
cancelada. Un mentor puede acompañar varias actividades y una actividad puede
tener varios mentores. La asignación confirmada genera participación al validarse
igual que la de cualquier otro perfil.

### RF-A-21

> **Equipos de la actividad**

Conformación de equipos dentro de una actividad, con nombre y miembros. Una
persona pertenece como máximo a un equipo por actividad. El equipo puede tener
un líder declarado, y su composición queda congelada al finalizar la actividad
para que los reportes históricos no cambien cuando alguien edite un equipo de una
edición anterior.

---

## Inscripción

### RF-A-22

> **Bandeja de inscripciones**

Listado de inscripciones por actividad, con el estado de cada una, la fecha, el
origen —autoservicio o captura administrativa— y si la persona ya tiene
participación registrada. Filtros por estado y por perfil, y contador visible de
inscritos frente a cupo. Exportable como listado de asistencia para el día de la
actividad.

### RF-A-23

> **Inscripción administrativa**

El administrador inscribe a una persona ya registrada en una actividad, lo que
cubre las inscripciones recogidas por otros medios. La inscripción queda marcada
con su origen y con la cuenta que la creó, y respeta las mismas reglas de cupo y
unicidad que el autoservicio salvo la excepción declarada de cupo.

### RF-A-24

> **Cierre y cancelación de inscripciones**

Cerrar la ventana impide inscripciones nuevas sin afectar a las existentes.
Cancelar una inscripción concreta exige motivo, libera el cupo y promueve a quien
siga en lista de espera. Una inscripción cuya participación ya fue validada no
puede cancelarse: primero hay que anular la participación.

---

## Participación

### RF-A-25

> **Registro de participación**

Alta de la participación de una persona en una actividad, con su rol dentro de
ella, el equipo cuando aplica, las fechas de inicio y finalización, el resultado
y el enlace de evidencia. La participación puede existir sin inscripción previa,
porque en actividades abiertas la asistencia se registra el mismo día.

### RF-A-26

> **Validación de participación**

Solo la validación administrativa convierte una inscripción o un registro de
asistencia en participación efectiva. La validación registra quién la hizo y
cuándo, y es el hecho que habilita puntos y constancias. El sistema distingue los
desenlaces de finalizada, en curso, retirada y no completó, y ninguno de los tres
últimos genera constancia de finalización.

### RF-A-27

> **Validación masiva desde listado**

Carga de un listado de asistencia para validar muchas participaciones de una
actividad en una sola operación. El sistema resuelve cada fila contra el
directorio por identificador, reporta las que no resuelve sin abortar el resto y
deja un resumen consultable con el conteo de validadas, rechazadas y ya
existentes. Ninguna fila del listado crea personas nuevas en silencio: las no
resueltas quedan en una bandeja para decidirlas una por una.

### RF-A-28

> **Resultados y reconocimientos**

Registro de los resultados obtenidos en una actividad: culminación, posición en
un concurso, premio, microcredencial o certificación, con su tipo, descripción y
fecha. Una participación puede acumular varios reconocimientos. Los
reconocimientos son consultables como listado propio para armar los reportes de
premiación del año.

### RF-A-29

> **Anulación controlada de participación**

Una participación validada no se borra: se anula con motivo obligatorio y queda
visible como anulada en el expediente de la persona. La anulación revierte los
puntos que generó mediante un movimiento de signo contrario, nunca editando el
movimiento original, e invalida las constancias emitidas a partir de ella.

---

## Puntos de innovación

### RF-A-30

> **Baremo de puntuación**

Tabla de reglas que determina cuántos puntos otorga una participación en función
del tipo de actividad, el rol desempeñado y el desenlace. Cada regla tiene
vigencia por rango de fechas, de modo que cambiar el baremo no altera los puntos
ya otorgados bajo el baremo anterior. Una actividad puede declarar un puntaje
propio que prevalece sobre la regla general.

### RF-A-31

> **Asignación automática al validar**

Al validar una participación, el sistema resuelve la regla vigente y genera el
movimiento de puntos correspondiente, dejando registrada qué regla lo produjo. Si
ninguna regla aplica, la participación queda validada con cero puntos y aparece
en una lista de revisión, en lugar de fallar o de inventar un valor.

### RF-A-32

> **Ajuste manual con motivo**

El administrador otorga o descuenta puntos fuera del baremo indicando motivo y
descripción. El movimiento queda marcado como manual y nombra a quien lo hizo.
Los ajustes manuales se reportan aparte del total automático, para que el
indicador de puntos siga siendo auditable.

### RF-A-33

> **Reverso de puntos**

Ningún movimiento de puntos se edita ni se borra. Corregir significa emitir un
movimiento que anula al anterior, apuntando a él y explicando el motivo. El saldo
de una persona es siempre la suma de sus movimientos vivos, calculada y no
almacenada.

---

## Constancias

### RF-A-34

> **Plantillas de constancia**

Plantillas administrables con el texto, los campos que se sustituyen y la firma
institucional. Distintas plantillas para constancia de participación, de
finalización y de acompañamiento como mentor. Editar una plantilla no altera las
constancias ya emitidas con la versión anterior.

### RF-A-35

> **Emisión de constancias**

Una constancia se emite únicamente a partir de participaciones validadas y
congela en el momento de emitirse el nombre, el identificador, las actividades
que ampara, las fechas y el rol desempeñado. Lleva folio único, la cuenta que la
emitió y un código de verificación. Una misma constancia puede amparar varias
participaciones cuando la persona pide un consolidado, típicamente al graduarse.

### RF-A-36

> **Anulación y reemisión**

Una constancia se anula con motivo y queda registrada como anulada, de modo que
la verificación pública informe que ese folio dejó de tener validez. Reemitir
genera un folio nuevo que apunta al anulado. Nunca se reutiliza un folio.

---

## Portafolio de innovación

### RF-A-37

> **Registro de una propuesta**

Alta de las propuestas de innovación surgidas de las actividades, con nombre,
año de ingreso al portafolio, actividad de origen, descripción del problema y
oportunidad, síntesis de la solución, usuario o beneficiario principal, cliente o
adoptante principal y enlace al expediente documental. El año de ingreso es el
del primer ingreso y no cambia aunque la propuesta siga participando en
actividades posteriores.

### RF-A-38

> **Código institucional de la propuesta**

Cada propuesta recibe un código estable con la forma `UAM-INN-<año>-<correlativo>`,
generado por el sistema y correlativo dentro del año de ingreso. El código es
inmutable y es la referencia que usa la hoja de participaciones para vincular a
una persona con un proyecto.

### RF-A-39

> **Clasificación de la propuesta**

Registro del nivel de formalización, la etapa de desarrollo, el estado en el
portafolio, el ámbito de la quíntuple hélice, el sector de aplicación según el
clasificador nacional de actividades económicas, la vertical de innovación, el
tipo predominante de innovación, el nivel de madurez tecnológica, el nivel de
preparación de mercado y hasta dos Objetivos de Desarrollo Sostenible. Cada
clasificación admite un valor de _por determinar_, porque una propuesta recién
ingresada casi nunca tiene todos estos datos.

### RF-A-40

> **Integrantes de la propuesta**

Vinculación de personas con la propuesta, con su rol y el período en que
estuvieron activas. Los integrantes de una propuesta son independientes de los
equipos de cada actividad: una propuesta sobrevive a la actividad que la originó
y su equipo cambia con el tiempo.

### RF-A-41

> **Trayectoria de la propuesta**

Historial de los cambios de etapa, de estado y de clasificación de cada
propuesta, con la fecha y la cuenta que los registró, más el listado de las
actividades en las que ha participado después de la de origen. Es lo que permite
reconstruir la evolución de una propuesta sin depender de la memoria de quien la
acompañó.

---

## Reportes y tableros

### RF-A-42

> **Reporte de participación**

Conteos por año, programa, actividad, tipo de actividad y perfil de participante,
distinguiendo inscripciones, participaciones registradas y participaciones
validadas. Cada cifra es navegable hasta el listado de personas que la componen,
porque un total que no se puede abrir no se puede defender ante una auditoría.

### RF-A-43

> **Participantes únicos frente a inscripciones**

Todo reporte que cuente personas declara explícitamente las dos cifras: cuántas
inscripciones hubo y cuántas personas distintas las produjeron. La cifra de
personas distintas se calcula sobre el registro conservado tras las fusiones, de
modo que un duplicado resuelto deje de contar doble también en los reportes de
años anteriores.

### RF-A-44

> **Segmentación académica y de perfil**

Filtros combinables por facultad, carrera, año de carrera, institución de
procedencia, perfil, sexo, etnia autodeclarada y municipio. Los estudiantes con
doble titulación se cuentan una vez en el total general y una vez en cada
carrera, y el reporte lo indica en lugar de dejar que los totales por carrera no
sumen el total general.

### RF-A-45

> **Cierre anual de indicadores**

Al cerrar un año, el sistema congela sus indicadores en un registro fechado que
ya no cambia aunque después se corrijan participaciones de ese año. Las
correcciones posteriores aparecen como diferencia frente al cierre, no
reescribiéndolo. Es lo que permite que el informe institucional entregado en
enero siga siendo reproducible en diciembre.

### RF-A-46

> **Exportación con registro de acceso**

Exportación de cualquier listado a formato tabular. Toda exportación que incluya
datos personales queda registrada con la cuenta, el instante, el filtro aplicado
y la cantidad de filas. Las exportaciones agregadas no llevan datos personales y
se distinguen de las nominales en el registro.

### RF-A-47

> **Tablero administrativo**

Indicadores de un vistazo: participantes únicos del año en curso, inscripciones,
participaciones validadas, actividades realizadas y en curso, distribución por
tipo de actividad, participación por facultad y por carrera, mentores activos,
propuestas en portafolio por etapa y evolución mensual. Cada indicador declara el
período que cubre y la fecha de su último cálculo.

---

## Sistema

### RF-A-48

> **Parámetros del sistema**

Pantalla única para los valores que gobiernan el comportamiento del sistema sin
desplegar: vigencia de la verificación de correo, plazo de expiración de
invitaciones, período tras el cual los datos personales se consideran
desactualizados, tamaño máximo de una carga masiva, dominio de correo
institucional aceptado y umbral de similitud para la detección de duplicados.
Cada cambio registra el valor anterior, la cuenta que lo hizo y el instante, y
puede revertirse.

### RF-A-49

> **Importación de matrices históricas**

Carga de las matrices de estudiantes, participaciones, mentores y portafolio que
la DIEM mantiene hoy en hojas de cálculo. La importación valida cada fila contra
las mismas reglas del alta manual, no crea nada hasta que el administrador
confirma el resumen, y deja registro fila por fila de lo insertado, lo
actualizado y lo rechazado con su motivo. Una fila rechazada no detiene la carga.

### RF-A-50

> **Retención e imposibilidad de borrado**

Participaciones, movimientos de puntos, constancias, bitácora e indicadores
cerrados no admiten borrado desde ninguna interfaz ni por ningún rol. La
corrección se hace por anulación con motivo, conservando el registro original. La
baja de una persona anonimiza sus datos personales manteniendo sus participaciones
contabilizadas, porque retirarlas alteraría los reportes de años ya cerrados.
