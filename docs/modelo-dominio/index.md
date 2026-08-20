---
icon: lucide/database
---

# Modelo de dominio

La base de datos consta de **82 tablas**:

- 46 tablas de dominio
- 24 tablas de catálogo administrable y de taxonomía externa
- 12 tablas de catálogo de estado y de transición

Las reglas transversales de tipos, nomenclatura y régimen de auditoría están en
[`Convenciones`][convenciones]. El patrón de estados y su catálogo completo, en
[`Estados`][estados].

!!! note "Sobre el recuento"

    Veinticuatro tablas son listas cortas que provienen literalmente de las
    listas desplegables de las matrices de soporte: sexo, etnia, talla, rol en la
    actividad, TRL, MRL, ODS y el resto de las taxonomías del portafolio. Ninguna
    supera las veinticinco filas y ninguna tiene lógica propia. El modelo de
    negocio real cabe en las 46 tablas de dominio.

---

## Cobertura de requerimientos

Los 79 requerimientos tienen soporte en el modelo.

Tres se satisfacen sin persistencia propia:

1. [`RF-P-15`][rf-p-15] — es una composición de lectura sobre `actividad`
1. [`RF-A-42`][rf-a-42] — consultas sobre `participacion` y sus vistas
1. [`RF-P-25`][rf-p-25] — filtro por identidad de sesión, no una tabla

Tres conceptos del análisis preliminar **no** son tablas, y no serlo es una
decisión, no un olvido:

|          Concepto          |                                           Por qué no es tabla                                           |            Dónde vive            |
| :------------------------: | :-----------------------------------------------------------------------------------------------------: | :------------------------------: |
| Historial de participación | Es una consulta sobre `participacion`; almacenarlo crearía una segunda verdad que puede desincronizarse |          [`D-15`][d-15]          |
|          Reporte           |               Es una consulta parametrizada; lo que sí se almacena es el **cierre** anual               | [`indicador_periodo`][indicador] |
|    Punto de innovación     |                            No es un saldo: es un libro mayor de movimientos                             | [`movimiento_punto`][movimiento] |

---

## Invariantes críticos

Seis garantías que no pueden fallar. Todas son estructurales: si alguna se
implementa en la capa de aplicación, el requerimiento correspondiente deja de ser
una garantía y pasa a ser una aspiración.

|                          Invariante                           |             Mecanismo             |               Requerimientos               |
| :-----------------------------------------------------------: | :-------------------------------: | :----------------------------------------: |
|         Un identificador pertenece a una sola persona         | `unq_identificadorpersona_valor`  | [`RF-P-02`][rf-p-02], [`RF-A-07`][rf-a-07] |
|   Una persona tiene una sola inscripción viva por actividad   | `unq_inscripcion_persona_activa`  |            [`RF-P-17`][rf-p-17]            |
|         Los inscritos nunca superan el cupo declarado         |  `chk_actividad_cupo_coherente`   | [`RF-A-18`][rf-a-18], [`RF-P-18`][rf-p-18] |
|       Un folio de constancia es único y no se reutiliza       |      `unq_constancia_folio`       | [`RF-A-35`][rf-a-35], [`RF-P-24`][rf-p-24] |
|    Exactamente una carrera del estudiante es la principal     | `unq_estudiantecarrera_principal` |            [`RF-P-09`][rf-p-09]            |
| Ninguna participación, punto, constancia ni bitácora se borra |      Trigger `BEFORE DELETE`      |            [`RF-A-50`][rf-a-50]            |

> El invariante del cupo es el único que compite bajo concurrencia. Dos personas
> pulsando _inscribirme_ en el mismo instante sobre el último lugar es el caso
> real de todo hackathon con inscripción abierta. `CHECK (inscritos <= cupo)`
> sobre `actividad`, combinado con el trigger que incrementa el contador dentro
> de la misma transacción que crea la inscripción, convierte el sobrecupo en un
> error de transacción sin necesidad de `SELECT ... FOR UPDATE` explícito en la
> aplicación y sin ventana de carrera entre la lectura y la escritura.

---

## Mapa de módulos

Las flechas indican dependencia por llave foránea: el origen referencia al
destino.

|       Módulo        |                 Depende de                  |
| :-----------------: | :-----------------------------------------: |
|    **`Estados`**    |                      —                      |
|   **`Catálogos`**   |                   Estados                   |
|  **`Taxonomías`**   |                      —                      |
|   **`Identidad`**   |             Estados, Catálogos              |
|   **`Perfiles`**    |            Identidad, Catálogos             |
|  **`Actividades`**  |   Estados, Catálogos, Identidad, Perfiles   |
| **`Participación`** | Estados, Catálogos, Identidad, Actividades  |
|    **`Puntos`**     |     Catálogos, Identidad, Participación     |
|  **`Constancias`**  |      Estados, Identidad, Participación      |
|  **`Portafolio`**   | Estados, Taxonomías, Identidad, Actividades |
|   **`Analítica`**   |                  Identidad                  |
|   **`Auditoría`**   |            Identidad, Catálogos             |

**`Estados`** y **`Taxonomías`** son hojas del grafo: no referencian a nadie y
todos los referencian.

Ningún módulo referencia a **`Participación`** salvo **`Puntos`** y
**`Constancias`**. Eso mantiene la tabla que más crece libre de acoplamientos
entrantes y permite evolucionar el baremo y el formato de las constancias sin
tocar el registro de participación, que es el activo que el sistema existe para
proteger.

**`Portafolio`** no referencia a **`Participación`**: una propuesta sobrevive a
la actividad que la originó y su equipo cambia con el tiempo, de modo que se
vincula a personas y a actividades, nunca a participaciones concretas. Es la
diferencia entre _quién participó en el hackathon_ y _quién sostiene el proyecto
hoy_.

[convenciones]: convenciones.md
[d-15]: decisiones.md#d-15
[estados]: modulos/estados.md
[indicador]: modulos/analitica.md#indicador_periodo
[movimiento]: modulos/puntos.md#movimiento_punto
[rf-a-07]: ../requerimientos/funcionales/administracion.md#rf-a-07
[rf-a-18]: ../requerimientos/funcionales/administracion.md#rf-a-18
[rf-a-35]: ../requerimientos/funcionales/administracion.md#rf-a-35
[rf-a-42]: ../requerimientos/funcionales/administracion.md#rf-a-42
[rf-a-50]: ../requerimientos/funcionales/administracion.md#rf-a-50
[rf-p-02]: ../requerimientos/funcionales/participantes.md#rf-p-02
[rf-p-09]: ../requerimientos/funcionales/participantes.md#rf-p-09
[rf-p-15]: ../requerimientos/funcionales/participantes.md#rf-p-15
[rf-p-17]: ../requerimientos/funcionales/participantes.md#rf-p-17
[rf-p-18]: ../requerimientos/funcionales/participantes.md#rf-p-18
[rf-p-24]: ../requerimientos/funcionales/participantes.md#rf-p-24
[rf-p-25]: ../requerimientos/funcionales/participantes.md#rf-p-25
