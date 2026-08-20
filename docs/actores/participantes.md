---
icon: lucide/users-round
---

# Portal del participante

## Visitante

> **Persona sin cuenta que explora el catálogo**
>
> > **Precede a:** [`Participante`](#participante)

Ve las actividades publicadas con sus fechas, cupo restante y puntos que otorgan,
y verifica la validez de una constancia introduciendo su folio. No puede
inscribirse, ni ver historial, ni acceder a dato personal alguno.

Al intentar inscribirse, el sistema le pide registrarse conservando la actividad
que había seleccionado.

## Participante

> **Persona con cuenta verificada y consentimiento otorgado**
>
> > **Deriva de:** [`Visitante`](#visitante)

Es el actor base del portal y el único que se inscribe. Tiene correo verificado,
al menos un identificador y al menos un perfil declarado. Se inscribe, cancela
dentro de la ventana, consulta su historial y sus puntos, solicita constancias y
descarga sus propios datos.

Los cuatro actores siguientes son este mismo actor con un perfil declarado
encima. Ninguno reemplaza al participante: lo especializan.

## Estudiante UAM

> **Participante vinculado académicamente a la Universidad**
>
> > **Deriva de:** [`Participante`](#participante)
> >
> > > - Añade perfil académico y correo institucional obligatorio

Se identifica con su CIF y se registra con correo del dominio institucional.
Declara facultad, carrera y año, y puede declarar una segunda carrera cuando
cursa doble titulación. Es el actor que el sistema segmenta con más detalle,
porque los reportes institucionales se piden por carrera y por facultad.

Puede formar equipos y, con perfil de mentor añadido, acompañar como mentor
estudiantil.

## Participante externo

> **Persona ajena a la UAM que participa en actividades de la DIEM**
>
> > **Deriva de:** [`Participante`](#participante)
> >
> > > - Añade institución de procedencia y descripción de a qué se dedica

Se identifica con cédula, pasaporte o carné de residencia y se registra con
correo personal. Cubre dos poblaciones que el sistema no separa por capacidad
pero sí por dato declarado: estudiantes de otras instituciones, que declaran
universidad y carrera, y emprendedores, profesionales independientes o
colaboradores de empresas, que declaran su ocupación.

Es la población de los hackathones y los rallies, y la que más crece por edición.

## Docente

> **Participante vinculado laboralmente a la UAM**
>
> > **Deriva de:** [`Participante`](#participante)
> >
> > > - Añade adscripción a facultad y nivel académico

Asiste a talleres, charlas, diplomados y programas, y aparece en los reportes de
participación institucional como personal académico. No administra actividades
por el hecho de ser docente: si además coordina, lo hace con una cuenta
administrativa.

## Mentor

> **Participante designado por la DIEM para acompañar equipos**
>
> > **Deriva de:** [`Participante`](#participante)
> >
> > > - Añade expediente profesional y asignaciones a actividades

Acompaña, orienta y asesora en hackathones, rallies, semilleros y programas.
Declara nivel académico, descripción profesional, áreas de experiencia,
certificaciones y necesidades de formación, y registra el aporte de cada
acompañamiento.

El perfil no se autoasigna: la persona lo solicita y la DIEM lo confirma. Un
mentor sin asignaciones confirmadas es un expediente disponible, no un
acompañamiento en curso.

## Participante sin consentimiento vigente

> **Cuenta que existe pero no puede operar**
>
> > **Deriva de:** [`Participante`](#participante)

Conserva el acceso, su historial y sus constancias ya emitidas, pero no puede
inscribirse ni recibir comunicaciones no esenciales, y queda fuera de los
reportes nominales. Ocurre en tres casos: consentimiento nunca otorgado, retirado
por la persona, o pendiente de verificar en un registro importado desde las
matrices históricas.

Las participaciones que la persona ya acumuló siguen contando en los agregados de
los años en que ocurrieron. Retirarlas alteraría reportes ya cerrados y sería una
respuesta desproporcionada a un consentimiento retirado.
