---
icon: lucide/chart-network
---

# Decisiones transversales

## D-01

> **Llave primaria `uuid` con `DEFAULT uuidv7()`**

Ordenable en el tiempo, con localidad de índice equivalente a un serial; no
enumerable desde fuera. Que no sea enumerable importa aquí más que en otros
sistemas: una ruta con identificador secuencial permitiría recorrer el directorio
completo de personas cambiando un número en la barra de direcciones.

## D-02

> **Todo instante en `timestamptz` almacenado en UTC**

La fecha de negocio se materializa aparte como `date` cuando hace falta agrupar
por día. Nicaragua no aplica horario de verano, lo que hace la conversión a
`America/Managua` estable.

El año de participación, en cambio, **no** se deriva del instante: es una columna
propia, porque una actividad que empieza en diciembre y termina en enero pertenece
al año que la DIEM decida reportar, no al que diga el reloj. Ver [`D-14`](#d-14).

## D-03

> **Una sola tabla `usuario` para toda persona**

Estudiantes, externos, docentes, mentores y administradores comparten tabla.
Lo que los diferencia son los perfiles de [`Perfiles`][perfiles] y el rol de
sistema.

Es la decisión que hace posible el requerimiento central: si un docente que
además mentorea tuviera dos filas, el conteo de participantes únicos volvería a
estar mal por construcción, que es exactamente el problema que el sistema viene a
resolver.

## D-04

> **Los identificadores viven en tabla propia, no en columnas de `usuario`**

`usuario` no tiene columnas `cif` ni `cedula`. Tiene filas en
`identificador_persona`, cada una con su tipo y su valor.

Con columnas, una persona con CIF y cédula obliga a comparar cuatro combinaciones
para detectar un duplicado, y agregar el pasaporte para participantes extranjeros
—que los rallies latinoamericanos traen todos los años— es una migración. Con
filas, la detección es una sola consulta por valor normalizado y agregar un tipo
es insertar en un catálogo.

## D-05

> **El tipo de usuario no es una columna: se deriva de los perfiles**

El análisis preliminar trata el tipo como un atributo único. El modelo lo trata
como el conjunto de perfiles declarados, porque son acumulables en la práctica:
el listado de mentores contiene docentes de la UAM y estudiantes.

Los reportes por perfil suman una persona en cada perfil que tenga y lo declaran
explícitamente, en lugar de forzar una clasificación que obligaría a decidir si
un docente-mentor cuenta como docente o como mentor.

## D-06

> **Nunca se declara una llave primaria natural**

El CIF es el candidato obvio para llave primaria de estudiante y es exactamente
por eso que no se usa. Un CIF puede corregirse tras un error de captura, y una
llave primaria corregible se propaga a `inscripcion`, `participacion`,
`movimiento_punto` y `constancia`.

Las relaciones 1:1 se expresan con un índice único sobre la llave foránea, que da
la misma garantía sin propagar columnas.

## D-07

> **Texto y colecciones nunca son nulables**

El valor de ausencia es `''`, `[]` o `{}`, declarado como `DEFAULT`.

Dos valores vacíos obligan a escribir `col IS NOT NULL AND col <> ''` en cada
predicado, y basta olvidar una mitad para que la consulta mienta. El nulo se
reserva para los tipos donde no existe centinela honesto: instantes, fechas,
cantidades y llaves foráneas opcionales.

## D-08

> **Inmutabilidad forzada con triggers `BEFORE`**

Lanzan excepción en el motor, no validando reglas en la capa de aplicación.

[`RN-16`][rn-16] establece que la información histórica no se elimina. Una regla
que vive en el servicio se evade desde cualquier cliente de base de datos; una
que vive en el trigger, no. La DIEM administra su propio sistema y su
administrador tendrá acceso a la base: la protección tiene que estar por debajo
de él.

## D-09

> **Predicados de índice parcial derivados de marcas temporales**

El predicado de un índice solo admite expresiones inmutables sobre columnas de la
misma fila: no puede consultar `estado_<entidad>` ni llamar a `now()`.

Cada entidad con ciclo de vida lleva las marcas que registran sus transiciones
—`cancelada_at`, `validada_at`, `anulada_at`— y el subconjunto vivo se identifica
con `IS NULL` sobre la marca de cierre. Es lo que sostiene la unicidad de
inscripción viva bajo concurrencia.

## D-10

> **Máquinas de estado como datos**

Las transiciones legales de `inscripcion`, `participacion`, `actividad` y
`propuesta` se declaran en tablas `transicion_<entidad>`, no en código.

Agregar un desenlace de participación —la matriz de estudiantes ya tiene seis y
la DIEM añadirá más— debe ser una fila, no un despliegue.

## D-11

> **Inscripción y participación son tablas distintas**

No es normalización: es el requerimiento. [`RN-06`][rn-06] existe porque contar
inscripciones y llamarlas participantes es el error que motiva el proyecto.

Una participación puede existir sin inscripción, porque en las charlas abiertas
la asistencia se registra el mismo día. Por eso `participacion.inscripcion_id` es
nulable y la llave foránea real es a `usuario` y `actividad`.

## D-12

> **Los puntos son un libro mayor, no un contador**

`usuario` no tiene columna `puntos`. Tiene filas en `movimiento_punto`, y el
saldo es su suma.

Un contador denormalizado obliga a que toda corrección lo actualice y a que toda
concurrencia lo bloquee, y el primer descuadre entre el contador y el detalle es
indetectable. Con un libro mayor, el saldo y el detalle no pueden discrepar
porque son la misma cosa.

## D-13

> **Programa y actividad, no una cadena de edición**

`Hackathon Nicaragua` es un programa; `Hackathon Nicaragua 2025` es una actividad
que lo referencia. La matriz de estudiantes guarda hoy el nombre y la edición
como dos listas desplegables independientes, lo que permite escribir
`Hackathon Nicaragua` con `I Cohorte 2026` sin que nada lo impida.

Con dos tablas, preguntar por la participación acumulada en un programa a lo
largo de cuatro años es una llave foránea, y no depende de que el nombre se haya
escrito igual cada vez.

## D-14

> **El año de participación es un dato, no una derivación**

`participacion.anio` es una columna propia y no `EXTRACT(year FROM fecha_inicio)`.

Una edición del Rally que se ejecuta en diciembre y cierra en enero se reporta
completa en un solo año, y quién decide cuál es la DIEM. Derivarlo del instante
partiría esa edición en dos ejercicios y ninguna de las dos mitades cuadraría con
el informe institucional.

## D-15

> **El historial y el reporte no son tablas**

Ambos aparecen como conceptos en el análisis preliminar. Ninguno se persiste.

El historial es una consulta sobre `participacion` y `movimiento_punto`.
Almacenarlo crearía una segunda verdad que puede desincronizarse de la primera, y
la pregunta _cuál de las dos es correcta_ no tendría respuesta. Lo que sí se
persiste es el **cierre anual**, que es otra cosa: una foto fechada e inmutable,
descrita en [`RN-18`][rn-18].

## D-16

> **La constancia congela su contenido**

`constancia` guarda el nombre, el identificador, las actividades y las fechas tal
como estaban al emitirse, no llaves foráneas que se lean al imprimir.

Un documento institucional entregado a un tercero no puede cambiar de contenido
porque alguien corrigió una fecha tres meses después. Las llaves foráneas también
están, para poder navegar, pero el texto que se imprime sale de las columnas
congeladas.

## D-17

> **Doble titulación como filas, no como columnas**

`estudiante_carrera` admite una fila por carrera con su marca de principal, en
lugar de `carrera_1` y `carrera_2` sobre el perfil.

Con columnas, el reporte por carrera necesita unir la tabla consigo misma y el
tercer caso —que existe— obliga a migrar. Con filas, el reporte es un `GROUP BY`
y el estudiante con tres carreras no rompe nada.

## D-18

> **Los catálogos no se borran, se desactivan**

Toda tabla de catálogo lleva `activo` y bloquea `DELETE` con trigger.

Una carrera cerrada hace cinco años sigue siendo la carrera de las personas que
participaron entonces. Borrarla dejaría huérfanos los reportes históricos que
justifican la existencia del sistema.

## D-19

> **El dato demográfico es autodeclarado y opcional en el reporte**

Sexo y etnia son listas administrables y llevan valor de _prefiero no declarar_.
Ningún reporte los exige como dimensión obligatoria y ninguna validación los
infiere del nombre o de la procedencia.

La matriz de estudiantes lo pide explícitamente para la etnia. El modelo extiende
el mismo criterio al sexo, porque el argumento es idéntico.

## D-20

> **Nombres de tabla en singular, `snake_case`, en español**

El dominio se enuncia en español en todos los documentos de origen y traducirlo
introduce una capa de equivalencias que hay que mantener en la cabeza al leer una
consulta. Las tablas puente llevan los nombres de ambos extremos en orden de
dependencia (`estudiante_carrera`, `constancia_participacion`).

[perfiles]: modulos/perfiles.md
[rn-06]: ../requerimientos/reglas-negocio.md#rn-06
[rn-16]: ../requerimientos/reglas-negocio.md#rn-16
[rn-18]: ../requerimientos/reglas-negocio.md#rn-18
