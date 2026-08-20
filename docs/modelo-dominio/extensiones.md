---
icon: lucide/blocks
---

# Extensiones previstas

Siete funcionalidades que el modelo **no** implementa y para las que deja sitio.

Cada una indica qué haría falta agregar y —más importante— qué **no** haría falta
migrar. Una extensión que obligue a reescribir tablas existentes es una decisión
mal tomada hoy, no una extensión.

---

## E-01

> **Asistencia por sesión con código QR**

Una actividad de varios días registra hoy una sola participación. Marcar
asistencia día a día exigiría dos tablas nuevas: `sesion_actividad` con la fecha y
el horario de cada jornada, y `asistencia_sesion` con la marca de entrada por
persona y sesión.

**No haría falta migrar nada.** `participacion` seguiría siendo el registro
consolidado y la asistencia por sesión sería su detalle, del mismo modo que el
saldo de puntos es la suma de sus movimientos. La regla de finalización pasaría de
declararse a calcularse —_asistió a seis de ocho sesiones_—, pero se expresaría en
el mismo `estado_participacion` que ya existe.

El enganche está previsto: `actividad.fecha_inicio` y `fecha_fin` ya delimitan el
rango en el que las sesiones podrían caer.

---

## E-02

> **Formularios de inscripción configurables por actividad**

Hoy el formulario de inscripción es fijo. Un hackathon que necesita preguntar
tallas y restricciones alimentarias, y un diplomado que necesita preguntar
experiencia previa, comparten hoy el mismo formulario.

Exigiría `campo_formulario` con la definición por actividad y `respuesta_formulario`
con lo que cada persona contestó, más un `jsonb` de validación por campo.

**Riesgo de la extensión:** es la puerta por la que un modelo relacional se
convierte en un almacén de pares clave-valor. Si se implementa, el criterio debe
ser que ningún dato que la DIEM reporte viva ahí: lo reportable se modela, lo
circunstancial se pregunta.

---

## E-03

> **Evaluación de proyectos y actas de jurado**

`asignacion_mentor` ya admite `tipo_acompanamiento = 'jurado'`, pero el modelo no
guarda lo que el jurado puntúa. Un concurso con rúbrica exigiría `rubrica`,
`criterio_rubrica`, `evaluacion` y `evaluacion_criterio`.

**No haría falta migrar nada.** `reconocimiento` seguiría registrando el resultado
—primer lugar, mención— y la evaluación sería su fundamento. La separación es
deliberada: el resultado es institucional y permanente; la puntuación de cada
jurado es interna y puede no publicarse nunca.

---

## E-04

> **Integración con el sistema académico de la UAM**

Hoy el estudiante declara su carrera y su año, y la DIEM confía. Con acceso al
sistema académico, `perfil_estudiante` y `estudiante_carrera` se poblarían desde
la fuente autoritativa y el CIF se verificaría contra ella en lugar de contra una
expresión regular.

**Qué haría falta:** una tabla de sincronización con la marca del último cotejo y
una columna de procedencia por campo, para distinguir lo declarado de lo
verificado. `identificador_persona.verificado_at` ya prevé esa distinción.

**Qué no cambiaría:** la estructura. Es la razón por la que `carrera` es una tabla
propia con `codigo` estable en lugar de un texto libre.

Esta extensión depende de una decisión institucional que no es de este proyecto y
está registrada como [`R-01`][r-01].

---

## E-05

> **Canje de puntos por beneficios**

Los puntos de innovación se acumulan y hoy no se gastan. Un catálogo de
beneficios exigiría `beneficio` con su costo en puntos y su disponibilidad, y
`canje` con la solicitud y su entrega.

**No haría falta migrar nada.** [`movimiento_punto`][movimiento] ya admite puntos
negativos y ya tiene `origen`; el canje sería un valor más de esa columna con su
propia llave foránea. Que el saldo sea un libro mayor y no una columna es
precisamente lo que hace que gastar puntos no toque nada de lo existente.

Antes de implementarlo hace falta una política: qué se canjea, quién lo autoriza
y qué pasa con los puntos de una participación anulada que ya se gastaron. Esa
última pregunta no tiene respuesta técnica.

---

## E-06

> **Separación de funciones administrativas**

[`RF-A-03`][rf-a-03] declara un solo rol administrativo con todas las
capacidades, y [`actores/administración`][actor-admin] documenta lo que eso
concentra: quien registra la participación es quien la valida, quien emite la
constancia y quien fusiona duplicados.

**No haría falta migrar nada.** `rol_sistema` y `usuario_rol` existen desde el
primer día con esa finalidad. La extensión es poblar `rol_sistema` con los roles
reales —registro, validación, emisión, configuración— y sustituir la comprobación
de `es_interno` por una de capacidad concreta.

El costo de haberlo previsto es de dos tablas de menos de diez filas. El costo de
no haberlo previsto habría sido reescribir la capa de autorización entera.

---

## E-07

> **Notificación por WhatsApp o SMS**

`usuario.telefono_pais` y `telefono_numero` ya guardan el número en el formato de
ocho dígitos que WhatsApp usa en Nicaragua, y `notificacion.canal` ya es una
columna con `CHECK`.

**Qué haría falta:** un valor más en ese `CHECK`, una tabla de credenciales del
proveedor y el manejo de los estados de entrega, que en mensajería son más ricos
que en correo —enviado, entregado, leído, fallido— y probablemente justifiquen su
propia tabla de eventos.

**Qué haría falta antes:** consentimiento explícito por canal.
`consentimiento_datos` cubre hoy el tratamiento de datos en general;
comunicarse por WhatsApp con alguien que aceptó recibir correos es una decisión
que el modelo no debe dar por concedida.

---

## Criterio común

|               Pregunta                |                        Respuesta esperada                         |
| :-----------------------------------: | :---------------------------------------------------------------: |
|  ¿Obliga a migrar tablas existentes?  |                    No en ninguna de las siete                     |
| ¿El enganche existe ya en el modelo?  |  Sí: columnas, `CHECK` ampliables o tablas mínimas ya presentes   |
| ¿Está condicionada a algo no técnico? | `E-04` a un acuerdo institucional, `E-05` y `E-07` a una política |

Las siete se dejaron fuera del alcance por la misma razón: ninguna resuelve el
problema que motivó el sistema, que es contar personas sin duplicarlas.

[actor-admin]: ../actores/administracion.md
[movimiento]: modulos/puntos.md#movimiento_punto
[r-01]: riesgos.md#r-01
[rf-a-03]: ../requerimientos/funcionales/administracion.md#rf-a-03
