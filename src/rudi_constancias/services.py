from secrets import choice
from string import ascii_uppercase, digits
from typing import TYPE_CHECKING, Final

from django.db.models import Max
from django.db.transaction import atomic
from django.utils.timezone import now

from api_exceptions.enums import BadRequestErrorTypes, RequestScopes
from api_exceptions.errors import BadRequestError, NotFoundError
from rudi_auth.models import IdentificadorUser, RudiUser
from rudi_constancias.models import (
    Constancia,
    ConstanciaParticipacion,
    PlantillaConstancia,
)
from rudi_estados.enums import ActorTypes
from rudi_estados.services.catalogo import initial_estado_id
from rudi_estados.services.transicion import transicionar
from rudi_participacion.models import Participacion

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime
    from uuid import UUID

    from django.db.models import QuerySet

    from api_auth.models import ApiUser

########################################################################################

CODIGO_VERIFICACION: Final[str] = ascii_uppercase + digits

########################################################################################


@atomic
def crear_version(*, data: dict, qs: QuerySet) -> PlantillaConstancia:
    """
    File a new version of a certificate's text, closing the one in use.

    Versions are never edited in place once used (RF-A-34): a new text is a
    new row, numbered after the last one of its code.

    Returns:
        The new version.

    """

    codigo: str = data["codigo"]

    ultima: int | None = PlantillaConstancia.objects.filter(codigo=codigo).aggregate(
        ultima=Max("version"),
    )["ultima"]

    PlantillaConstancia.objects.filter(
        codigo=codigo,
        vigente_hasta__isnull=True,
    ).update(vigente_hasta=data["vigente_desde"])

    plantilla: PlantillaConstancia = PlantillaConstancia.objects.create(
        **data,
        version=(ultima or 0) + 1,
    )

    return qs.get(pk=plantilla.pk)


########################################################################################


def contexto(persona: RudiUser, participaciones: Sequence[Participacion]) -> dict:
    """
    Gather what a certificate's text can say, frozen at issue time (D-16).

    Returns:
        The values the template's markers resolve to.

    """

    cuenta: ApiUser = persona.user  # ty: ignore[invalid-assignment]

    nombre: str = f"{cuenta.first_name} {cuenta.last_name}".strip() or str(cuenta.email)

    identificador: str = (
        IdentificadorUser.objects
        .filter(is_main=True, user=persona)
        .values_list("valor", flat=True)
        .first()
    ) or ""

    actividades: list[dict] = [
        {
            "actividad": p.actividad.nombre,  # ty: ignore[unresolved-attribute]
            "anio": p.anio,
            "estado": p.estado.etiqueta,  # ty: ignore[unresolved-attribute]
            "rol": p.rol.etiqueta,  # ty: ignore[unresolved-attribute]
        }
        for p in participaciones
    ]

    return {
        "actividades": ", ".join(
            f"{a['actividad']} ({a['anio']})" for a in actividades
        ),
        "detalle": actividades,
        "fecha": now().date().isoformat(),
        "identificador": identificador,
        "nombre": nombre,
    }


def sustituir(texto: str, valores: dict) -> str:
    for campo, valor in valores.items():
        if isinstance(valor, str):
            texto = texto.replace("{" + campo + "}", valor)

    return texto


def rechazar(campo: str, detalle: str) -> BadRequestError:
    return BadRequestError(
        field_errors={campo: detalle},
        type=BadRequestErrorTypes.FAILED_VALIDATION,
    ).scoped(RequestScopes.BODY)


@atomic
def emitir_constancia(  # ruff: ignore[too-many-arguments]
    *,
    emitida_por: ApiUser,
    participaciones: Sequence[UUID],
    plantilla_id: UUID,
    qs: QuerySet,
    reemplaza_a_id: UUID | None,
    solicitada_at: datetime | None,
    user_id: UUID,
) -> Constancia:
    """
    Issue a certificate: freeze its text and content, and list what it covers.

    The folio comes from `trg_constancia_folio_asignar`; whether each
    participation may be covered is `trg_constanciaparticipacion_amparo`'s
    call (validated, not annulled, a state that `allow_constancia`, same
    person).

    Returns:
        The issued certificate.

    Raises:
        NotFoundError: The person or the template does not exist.
        rechazar: A participation does not exist, or the template needs data
            the person lacks.

    """  # ruff: ignore[docstring-extraneous-exception]

    persona: RudiUser | None = (
        RudiUser.objects.select_related("user").filter(pk=user_id).first()
    )

    if persona is None:
        raise NotFoundError(field_errors={"user_id": str(user_id)}).scoped(
            RequestScopes.BODY,
        )

    plantilla: PlantillaConstancia | None = PlantillaConstancia.objects.filter(
        pk=plantilla_id,
    ).first()

    if plantilla is None:
        raise NotFoundError(field_errors={"plantilla_id": str(plantilla_id)}).scoped(
            RequestScopes.BODY,
        )

    filas: list[Participacion] = list(
        Participacion.objects
        .select_related("actividad", "estado", "rol")
        .filter(pk__in=participaciones)
        .order_by("anio", "actividad__fecha_inicio")
    )

    if len(filas) != len(set(participaciones)):
        raise rechazar("participaciones", "Alguna de las participaciones no existe.")

    valores: dict = contexto(persona, filas)

    faltantes: list[str] = [
        campo
        for campo in plantilla.campos_requeridos  # ty: ignore[not-iterable]
        if not valores.get(campo)
    ]

    if faltantes:
        raise rechazar(
            "plantilla_id",
            "La plantilla exige datos que esta persona no tiene: "
            f"{', '.join(faltantes)}.",
        )

    constancia: Constancia = Constancia.objects.create(
        codigo_verificacion="".join(choice(CODIGO_VERIFICACION) for _ in range(10)),
        contenido_congelado={"participaciones": valores["detalle"]},
        emitida_por=emitida_por,
        estado_id=initial_estado_id("constancia"),
        identificador_congelado=valores["identificador"][:20],
        nombre_congelado=valores["nombre"][:201],
        plantilla=plantilla,
        reemplaza_a_id=reemplaza_a_id,
        solicitada_at=solicitada_at,
        texto_congelado=sustituir(plantilla.cuerpo, valores),  # ty: ignore[invalid-argument-type]
        user=persona,
    )

    ConstanciaParticipacion.objects.bulk_create(
        ConstanciaParticipacion(constancia=constancia, orden=orden, participacion=p)
        for orden, p in enumerate(filas, start=1)
    )

    return qs.get(pk=constancia.pk)


########################################################################################


def anular_constancia(
    *,
    constancia_id: UUID,
    motivo_descripcion: str,
    motivo_id: UUID,
    qs: QuerySet,
) -> Constancia:
    return transicionar(
        actor=ActorTypes.ADMIN,
        anulada_at=now(),
        codigo="anulada",
        entidad="constancia",
        motivo_descripcion=motivo_descripcion,
        motivo_id=motivo_id,
        pk=constancia_id,
        qs=qs,
    )


def verificar_constancia(*, codigo_verificacion: str, folio: str) -> dict:
    """
    Answer the public verification page; both values must match (RF-P-24).

    Returns:
        The frozen facts and whether the certificate is still valid.

    Raises:
        NotFoundError: No certificate has that folio and code.

    """

    constancia: Constancia | None = (
        Constancia.objects
        .select_related("estado")
        .filter(codigo_verificacion=codigo_verificacion, folio=folio)
        .first()
    )

    if constancia is None:
        raise NotFoundError(detail="No hay una constancia con ese folio y código.")

    return {
        "anulada_at": constancia.anulada_at,
        "emitida_at": constancia.emitida_at,
        "folio": constancia.folio,
        "nombre_congelado": constancia.nombre_congelado,
        "texto_congelado": constancia.texto_congelado,
        "valida": constancia.estado.valid,  # ty: ignore[unresolved-attribute]
    }
