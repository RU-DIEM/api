---
icon: lucide/award
---

# Constancias

Tres tablas, y una columna `jsonb` que hace todo el trabajo.

```mermaid
---
config:
  elk:
    nodePlacementStrategy: NETWORK_SIMPLEX
  fontFamily: monospace
  layout: elk
---
erDiagram
  direction LR
  plantilla_constancia {
    uuid      id                PK
    varchar   codigo            UK
    varchar   etiqueta
    smallint  version           UK
    text      cuerpo
    jsonb     campos_requeridos
    varchar   firma_nombre
    varchar   firma_cargo
    date      vigente_desde
    date      vigente_hasta
    boolean   activa
  }
  constancia {
    uuid         id                      PK
    varchar      folio                   UK
    uuid         usuario_id              FK
    uuid         plantilla_id            FK
    uuid         estado_id               FK
    varchar      codigo_verificacion     UK
    varchar      nombre_congelado
    varchar      identificador_congelado
    jsonb        contenido_congelado
    text         texto_congelado
    timestamptz  emitida_at
    uuid         emitida_por             FK
    timestamptz  solicitada_at
    timestamptz  anulada_at
    uuid         motivo_id               FK
    uuid         reemplaza_a_id          UK
    varchar      documento_url
  }
  constancia_participacion {
    uuid      id                PK
    uuid      constancia_id     UK
    uuid      participacion_id  UK
    smallint  orden
  }

  plantilla_constancia ||--o{ constancia               : ""
  constancia           ||--|{ constancia_participacion : ""
  constancia           ||--o| constancia               : "reemplaza_a_id"
```

---

## El congelado

Cuatro columnas duplican datos que existen en otras tablas, y esa duplicación es
el punto del módulo.

|          Columna          |                  Qué conserva                  |
| :-----------------------: | :--------------------------------------------: |
|    `nombre_congelado`     |         El nombre tal como se imprimió         |
| `identificador_congelado` |    El CIF o la cédula tal como se imprimió     |
|   `contenido_congelado`   | Actividades, fechas, roles y horas, en `jsonb` |
|     `texto_congelado`     | El cuerpo ya sustituido, listo para reimprimir |

Una constancia impresa en 2024 dice el nombre que la persona tenía entonces.
Reconstruirla por unión con los datos actuales produciría, tres años después, un
documento distinto del que la persona tiene en la mano.

El caso decisivo es la anulación de una participación amparada: la constancia
queda anulada, pero la verificación pública tiene que seguir mostrando qué decía
ese folio para poder afirmar que dejó de tener validez.

---

## Notas del nivel físico

**`folio` lo genera un trigger desde una secuencia**, y el valor recibido se
ignora. La secuencia se consume aunque la transacción falle, y eso es correcto:
un hueco en la numeración es inocuo, un folio repetido no lo es.

**`codigo_verificacion` es independiente del folio.** El folio es correlativo y
adivinable; exigir ambos impide recorrer los folios de un año y listar las
constancias emitidas.

**`constancia_participacion` es de muchos a muchos** porque el consolidado que la
persona pide al graduarse ampara varias participaciones, y una misma participación
puede constar en la constancia individual y en ese consolidado.

**Es el índice sobre `participacion_id` el que hace operativa la anulación en
cascada.** Anulada una participación, resolver qué folios quedan invalidados es
una búsqueda directa y no un recorrido del `jsonb` de cada constancia.
