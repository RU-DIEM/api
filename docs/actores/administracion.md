---
icon: lucide/folder-lock
---

# Portal de administración

## Administrador DIEM

> **Responsable de toda la operación del sistema**

Registra y fusiona personas, administra programas y actividades, valida
participaciones, define el baremo y ajusta puntos, emite y anula constancias,
mantiene el portafolio de innovación, gobierna catálogos y parámetros, genera
reportes y cierra los indicadores del año.

Es el único actor que ve datos personales de terceros, y cada consulta que hace a
la ficha de una persona concreta queda registrada. No puede borrar
participaciones, puntos, constancias ni bitácora: solo anularlos con motivo, por
[`RN-16`][rn-16].

Siempre debe existir al menos uno activo. El sistema rechaza la operación que
dejaría la plataforma sin ninguno, incluso cuando afecta a varias cuentas a la
vez.

---

## Sobre la ausencia de separación de funciones

Hay un solo rol interno y su matriz de capacidades es una columna.
Es una decisión de alcance del piloto, no una propiedad del dominio. La DIEM
concentra hoy en una persona cuatro funciones que en cualquier otra organización
estarían separadas:

|    Función    |                  Qué hace                   |               Riesgo de concentrarla               |
| :-----------: | :-----------------------------------------: | :------------------------------------------------: |
|   Operación   |   Registra personas, valida participación   |     Quien captura el dato es quien lo aprueba      |
| Configuración |    Cambia catálogos, baremo y parámetros    | Cambiar el baremo altera puntos de todo el sistema |
|   Análisis    | Consulta reportes y exporta datos agregados |   No necesita datos personales y aun así los ve    |
|   Auditoría   | Revisa la bitácora de sus propias acciones  |     Nadie verifica al que verifica a los demás     |

El modelo declara la estructura de roles desde el principio y la puebla con un
solo valor. Separar funciones más adelante es dar de alta filas en un catálogo,
no migrar el esquema. El enganche está en [`E-06`][e-06].

[e-06]: ../modelo-dominio/extensiones.md#e-06
[rn-16]: ../requerimientos/reglas-negocio.md#rn-16
