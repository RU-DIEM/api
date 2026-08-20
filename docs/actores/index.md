---
icon: lucide/user-round-pen
---

# Actores del sistema

Quién interactúa con cada superficie, qué lo distingue de los demás y qué puede
hacer. Un actor no es una persona: es un papel. La misma persona puede ser
docente y mentora sin que el sistema la trate como dos cuentas, y esa es
precisamente la propiedad que el sistema existe para garantizar.

- **Superficies:** 2
- **Actores humanos:** 7
- **Actores no humanos:** 2

---

## Matriz de capacidades

|           Capacidad            | Visitante | Estudiante UAM | Externo | Docente | Mentor  | Administrador |
| :----------------------------: | :-------: | :------------: | :-----: | :-----: | :-----: | :-----------: |
|      Ver catálogo público      |    sí     |       sí       |   sí    |   sí    |   sí    |      sí       |
|    Verificar una constancia    |    sí     |       sí       |   sí    |   sí    |   sí    |      sí       |
|    Inscribirse a actividad     |    no     |       sí       |   sí    |   sí    |   sí    |      no       |
|    Crear o unirse a equipo     |    no     |       sí       |   sí    |   no    |   no    |      no       |
|   Consultar historial propio   |    no     |       sí       |   sí    |   sí    |   sí    |      sí       |
|    Consultar puntos propios    |    no     |       sí       |   sí    |   sí    |   sí    |      sí       |
|      Solicitar constancia      |    no     |       sí       |   sí    |   sí    |   sí    |      no       |
| Aceptar asignación de mentoría |    no     |       no       |   no    |   no    |   sí    |      no       |
|   Registrar aporte de mentor   |    no     |       no       |   no    |   no    |   sí    |      no       |
|   Ver historial de terceros    |    no     |       no       |   no    |   no    |   no    |      sí       |
|    Administrar actividades     |    no     |       no       |   no    |   no    |   no    |      sí       |
|    Validar participaciones     |    no     |       no       |   no    |   no    |   no    |      sí       |
|    Asignar o ajustar puntos    |    no     |       no       |   no    |   no    |   no    |      sí       |
|       Emitir constancias       |    no     |       no       |   no    |   no    |   no    |      sí       |
|      Gestionar portafolio      |    no     |       no       |   no    |   no    |   no    |      sí       |
| Fusionar registros duplicados  |    no     |       no       |   no    |   no    |   no    |      sí       |
|   Exportar datos personales    |  parcial  |    parcial     | parcial | parcial | parcial |      sí       |
|       Cambiar parámetros       |    no     |       no       |   no    |   no    |   no    |      sí       |

_Parcial_ en la exportación significa que la persona descarga únicamente sus
propios datos, por [`RF-P-26`][rf-p-26].

El estudiante externo comparte columna con el participante externo: se distinguen
por los datos que declaran, no por lo que pueden hacer.

---

## Actores no humanos

### Proceso programado

> **Trabajos que corren sin intervención**

Cierra las ventanas de inscripción vencidas, promueve automáticamente desde las
listas de espera al liberarse cupo, pasa a en curso y a finalizada las actividades
cuyas fechas ya pasaron, expira los enlaces de verificación e invitación, marca
como desactualizados los perfiles que superan el período de vigencia, recalcula
las vistas de indicadores y purga los registros vencidos.

Sus escrituras quedan en bitácora con actor de tipo sistema, sin persona
asociada. Es un actor porque escribe: si sus acciones no fueran distinguibles de
las humanas, la bitácora perdería la mitad de su valor.

### Proveedor de correo

> **Servicio del que el sistema depende para verificar identidad**

Entrega los correos de verificación, recuperación, invitación, promoción desde
lista de espera y notificación de constancia emitida. No inicia interacciones:
responde a las del sistema y devuelve acuses que alimentan el estado de cada
notificación.

Su indisponibilidad bloquea el alta de cuentas nuevas, porque
[`RF-P-04`][rf-p-04] hace del correo verificado la condición para inscribirse. Es
la dependencia externa de mayor impacto del sistema.

---

## Superficies

1. [Portal de administración](administracion.md)
1. [Portal del participante](participantes.md)

[rf-p-04]: ../requerimientos/funcionales/participantes.md#rf-p-04
[rf-p-26]: ../requerimientos/funcionales/participantes.md#rf-p-26
