---
icon: lucide/circle-alert
---

# Riesgos abiertos

Diez cuestiones que el diseño no resuelve. Cada una indica su naturaleza, qué
pasa si no se atiende y qué deja preparado el modelo.

Un riesgo documentado no es un riesgo controlado. Es un riesgo que alguien podrá
reconocer cuando ocurra, en lugar de descubrirlo como un defecto.

---

## R-01

> **Integración con el sistema académico de la UAM**

- **Naturaleza:** institucional
- **Impacto si se materializa:** medio

El sistema confía en lo que el estudiante declara sobre su carrera y su año. No
hay forma de verificar que un CIF corresponde a un estudiante activo ni de
detectar que alguien dejó de serlo.

**Consecuencia práctica:** los reportes por carrera reflejan lo declarado, no lo
matriculado. Un egresado que sigue participando aparece en su carrera de origen
salvo que actualice su perfil.

**Qué deja preparado el modelo:** `identificador_persona.verificado_at` distingue
el identificador comprobado del declarado, y `carrera` es catálogo institucional
con código estable. La integración es [`E-04`][e-04].

**Quién decide:** la Dirección, con Registro Académico. No es una decisión de
este proyecto.

---

## R-02

> **Autoridad sobre los catálogos**

- **Naturaleza:** organizativa
- **Impacto si se materializa:** medio

Veinticuatro tablas de catálogo y taxonomía son administrables, y el modelo no
dice quién las administra. Si cualquier administrador puede agregar valores a
`vertical_innovacion` o a `area_experiencia`, en dos años habrá tres variantes de
_EdTech_ y los reportes por vertical dejarán de sumar.

**Qué deja preparado el modelo:** `codigo` es inmutable por trigger, lo que impide
el peor caso (renombrar un valor y romper el histórico), pero no impide crear
duplicados semánticos.

**Mitigación pendiente:** designar una persona responsable por catálogo, o
restringir el alta de valores a un rol específico cuando exista [`E-06`][e-06].

---

## R-03

> **Calidad de la carga inicial**

- **Naturaleza:** de datos
- **Impacto si se materializa:** alto

Las tres matrices se llenaron durante años sin validación. Contienen nombres
escritos de dos maneras, correos que ya no existen, cédulas incompletas y
participaciones sin fecha. [`RF-A-49`][rf-a-49] valida cada fila contra las
mismas reglas del alta manual, lo que significa que **una parte de la historia no
va a entrar**.

**Consecuencia práctica:** el sistema arranca con menos participaciones de las que
la DIEM cree tener, y la diferencia se atribuirá al sistema y no a la matriz.

**Qué deja preparado el modelo:** `importacion_fila.datos_crudos` conserva íntegra
toda fila rechazada, de modo que nada se pierde y la depuración puede hacerse
después. `usuario.origen = 'importacion'` marca los registros de procedencia
histórica.

**Mitigación pendiente:** depurar las matrices **antes** de la carga, no después.
El esfuerzo es el mismo y el resultado no lo es.

---

## R-04

> **Irreversibilidad de las fusiones**

- **Naturaleza:** de diseño
- **Impacto si se materializa:** alto

Fusionar dos personas traslada inscripciones, participaciones, puntos y
constancias al registro conservado. `fusion_usuario` guarda qué se trasladó y
cuántas filas, pero **no** guarda el estado previo completo, y por tanto la
operación no se deshace.

**Consecuencia práctica:** fusionar por error a dos hermanos con nombres parecidos
mezcla dos historiales de forma permanente.

**Qué deja preparado el modelo:** `usuario.fusionado_en_id` mantiene el registro
absorbido vivo y localizable, `fusion_usuario.resumen` congela el conteo por
entidad, y la fusión pasa por confirmación explícita con motivo.

**Mitigación pendiente:** una fusión reversible exigiría marcar cada fila
trasladada con su origen. Se descartó por costo frente a un caso poco frecuente,
pero la decisión debe revisarse si en el primer año ocurre más de una vez.

---

## R-05

> **Adopción del registro de participación**

- **Naturaleza:** organizativa
- **Impacto si se materializa:** alto

El sistema separa inscripción de participación porque contar inscritos como
participantes es el error que motivó el proyecto. Pero la participación **la
registra y la valida una persona**, después de la actividad, cuando la urgencia
ya pasó.

**Consecuencia práctica:** si la validación no se hace, el sistema mostrará
muchas inscripciones y pocas participaciones, y el indicador que la DIEM más
necesita será el más incompleto. El sistema habría cambiado el problema de sitio
en lugar de resolverlo.

**Qué deja preparado el modelo:** `idx_participacion_sin_validar` sostiene la
bandeja de pendientes, y `mv_participacion_actividad` publica las tres cifras
juntas, de modo que la brecha entre inscritos y validados sea visible en el
tablero desde el primer día.

**Mitigación pendiente:** que el cierre de una actividad no se considere completo
hasta que su participación esté validada. Es una regla de trabajo, no de software.

---

## R-06

> **Consentimiento de los registros importados**

- **Naturaleza:** legal
- **Impacto si se materializa:** alto

Las matrices contienen datos personales de cientos de personas —nombre, cédula,
correo, teléfono, etnia autodeclarada— recogidos por formularios cuyo texto de
autorización no consta. La propia matriz de estudiantes tiene un campo con el
valor _pendiente de verificar_, que es un reconocimiento del problema.

**Consecuencia práctica:** una parte del padrón importado no puede aparecer en
reportes nominales ni recibir comunicaciones hasta que se regularice.

**Qué deja preparado el modelo:** `consentimiento_datos` nace con estado
`pendiente_verificar` y canal `importacion` para todo registro importado, y
`estado_consentimiento` gobierna con `habilita_reporte_nominal` y
`habilita_comunicacion` qué se puede hacer con esos datos. [`RN-17`][rn-17] lo
convierte en regla.

**Quién decide:** la Universidad. El modelo hace cumplir la decisión, no la toma.

---

## R-07

> **Clasificación no validable del portafolio**

- **Naturaleza:** de datos
- **Impacto si se materializa:** medio

Diez clasificaciones por propuesta —TRL, MRL, tipo de innovación de Doblin,
sector CUAEN, vertical, quíntuple hélice, dos ODS— asignadas por criterio
experto. El sistema **no puede verificar ninguna**. Una propuesta clasificada como
TRL 7 por optimismo es indistinguible de una clasificada como TRL 7 por
evidencia.

El propio glosario de la matriz lo advierte: registrar el nivel demostrado y no el
planificado, y no asignar ODS por afinidad superficial.

**Consecuencia práctica:** el reporte de madurez tecnológica del portafolio puede
ser sistemáticamente optimista sin que nada lo delate.

**Qué deja preparado el modelo:** el valor neutro `por_determinar` en cada
taxonomía y `propuesta.clasificada_at`, que permite medir cuántas propuestas
están realmente clasificadas frente a cuántas conservan valores neutros. Es el
indicador de honestidad del módulo.

**Mitigación pendiente:** revisión periódica por más de una persona, o
justificación escrita para los niveles altos.

---

## R-08

> **Alcance del portafolio frente al análisis preliminar**

- **Naturaleza:** de alcance
- **Impacto si se materializa:** medio

El análisis preliminar no enuncia ningún requerimiento de portafolio: menciona
proyectos como un tipo de actividad. La matriz de portafolio define veintidós
campos con taxonomías completas. El modelo tomó la matriz como fuente y derivó
[`RF-A-37`][rf-a-37] a [`RF-A-41`][rf-a-41], que **nadie pidió explícitamente**.

**Consecuencia práctica:** cuatro tablas y nueve taxonomías podrían quedar vacías
si la DIEM no confirma que quiere gestionar el portafolio en este sistema.

**Qué deja preparado el modelo:** el módulo es una hoja del grafo. Nada depende de
`Portafolio`, y retirarlo del alcance no toca ninguna otra tabla.

**Mitigación pendiente:** confirmarlo con la Dirección antes de implementar. Es la
pregunta más barata de este documento.

---

## R-09

> **Escala y rendimiento en el reporte anual**

- **Naturaleza:** técnica
- **Impacto si se materializa:** bajo

El sistema es pequeño: entre 1,500 y 6,000 personas y decenas de miles de
participaciones. Las tablas que crecen sin techo son `bitacora`,
`participacion_evento` y `notificacion`.

**Consecuencia práctica:** ninguna en los primeros años. El riesgo real es el
opuesto: sobreoptimizar un sistema de este tamaño y complicarlo sin necesidad.

**Qué deja preparado el modelo:** índices BRIN sobre las tres tablas de alto
volumen, vistas materializadas para el tablero y la purga por retención mensual.
El particionado por año está disponible si alguna vez hace falta y **no se
implementó**, porque particionar cuarenta mil filas es ceremonia.

**Umbral de revisión:** cuando `bitacora` supere el millón de filas o el refresco
de las vistas pase de un minuto.

---

## R-10

> **Un solo administrador y ningún suplente**

- **Naturaleza:** organizativa
- **Impacto si se materializa:** medio

[`RF-A-03`][rf-a-03] concentra todas las capacidades administrativas en un rol
único, y el piloto contempla poblarlo con muy pocas cuentas. El modelo lo protege
de un solo modo: `trg_usuariorol_minimo_interno` impide dejar el sistema sin
ningún administrador.

**Consecuencia práctica:** si la persona que administra el sistema se ausenta en
la semana de un hackathon, las inscripciones siguen entrando y nadie valida,
emite constancias ni resuelve duplicados.

**Qué deja preparado el modelo:** nada más allá del trigger. Es un riesgo
operativo, no de datos.

**Mitigación pendiente:** al menos dos cuentas con rol interno desde el primer
día, aunque una sea de respaldo. Cuesta un registro y evita el único fallo que el
software no puede compensar.

---

## Resumen

| Riesgo |  Naturaleza   | Impacto |   Decide    |
| :----: | :-----------: | :-----: | :---------: |
| `R-01` | Institucional |  Medio  | Universidad |
| `R-02` | Organizativa  |  Medio  |    DIEM     |
| `R-03` |   De datos    |  Alto   |    DIEM     |
| `R-04` |   De diseño   |  Alto   |  Proyecto   |
| `R-05` | Organizativa  |  Alto   |    DIEM     |
| `R-06` |     Legal     |  Alto   | Universidad |
| `R-07` |   De datos    |  Medio  |    DIEM     |
| `R-08` |  De alcance   |  Medio  |    DIEM     |
| `R-09` |    Técnica    |  Bajo   |  Proyecto   |
| `R-10` | Organizativa  |  Medio  |    DIEM     |

Cinco de los diez los decide la DIEM y dos la Universidad. Solo dos son del
equipo de desarrollo, y ninguno de esos dos es el de mayor impacto. Es la forma
del riesgo en un sistema cuyo problema nunca fue técnico.

[e-04]: extensiones.md#e-04
[e-06]: extensiones.md#e-06
[rf-a-03]: ../requerimientos/funcionales/administracion.md#rf-a-03
[rf-a-37]: ../requerimientos/funcionales/administracion.md#rf-a-37
[rf-a-41]: ../requerimientos/funcionales/administracion.md#rf-a-41
[rf-a-49]: ../requerimientos/funcionales/administracion.md#rf-a-49
[rn-17]: ../requerimientos/reglas-negocio.md#rn-17
