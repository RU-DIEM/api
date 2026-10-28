from datetime import timedelta
from secrets import choice
from string import ascii_uppercase, digits
from typing import TYPE_CHECKING, Final, override

from asgiref.sync import sync_to_async
from django.db import IntegrityError
from django.db.models import Max
from django.db.transaction import atomic
from django.utils.dateparse import parse_duration
from django.utils.timezone import now

from api_core.services.operations import ForeignKeyCreateOperation
from api_exceptions.enums import RequestScopes
from api_exceptions.errors import ForbiddenError, NotFoundError
from rudi_actividades.models import Actividad
from rudi_auth.services.persona import persona_de, puede
from rudi_catalogos.models import Parametro
from rudi_estados.enums import ActorTypes, InputSourceTypes
from rudi_estados.services.catalogo import initial_estado_id, resolve_estado_id
from rudi_estados.services.transicion import transicionar
from rudi_participacion.models import (
    AsignacionMentor,
    Equipo,
    EquipoMiembro,
    Inscripcion,
)

if TYPE_CHECKING:
    from uuid import UUID

    from django.db.models import QuerySet

    from api_auth.models import ApiUser
    from api_core.schemas.base import DTO
    from api_utils.types import DatabaseModel
    from rudi_auth.models import RudiUser

########################################################################################

CODIGO_UNION: Final[str] = ascii_uppercase + digits

PLAZO_MENTORIA: Final[timedelta] = timedelta(days=7)

########################################################################################
# inscripción


@atomic
def inscribir(  # ruff: ignore[too-many-arguments]
    *,
    actividad_id: UUID,
    creada_por: ApiUser | None,
    is_excepcion_cupo: bool = False,
    origen: InputSourceTypes,
    persona_id: UUID,
    qs: QuerySet,
) -> Inscripcion:
    """
    File an inscription, into the waiting list when the quota is full.

    The activity row is locked first, so two people competing for its last
    seat queue here instead of both reading a free seat; the quota itself is
    still the database's `chk_actividad_cupo_coherente`, this only decides
    whether the newcomer waits.

    Returns:
        The new inscription, read back through *qs*.

    """

    actividad: Actividad | None = (
        Actividad.objects.select_for_update().filter(pk=actividad_id).first()
    )

    if actividad is None:
        raise NotFoundError(field_errors={"actividad": str(actividad_id)}).scoped(
            RequestScopes.BODY,
        )

    lleno: bool = (
        actividad.cupo is not None and actividad.inscritos_activos >= actividad.cupo
    )

    datos: dict = {
        "actividad_id": actividad_id,
        "creada_por": creada_por,
        "is_excepcion_cupo": is_excepcion_cupo,
        "origen": origen,
        "user_id": persona_id,
    }

    if lleno and not is_excepcion_cupo and actividad.admite_lista_espera:
        ultima: int | None = Inscripcion.objects.filter(
            actividad_id=actividad_id,
        ).aggregate(ultima=Max("posicion_espera"))["ultima"]

        datos |= {
            "estado_id": resolve_estado_id("inscripcion", "en_espera"),
            "posicion_espera": (ultima or 0) + 1,
        }
    else:
        datos["estado_id"] = initial_estado_id("inscripcion", origen)

    return qs.get(pk=Inscripcion.objects.create(**datos).pk)


def cerrar_inscripcion(  # ruff: ignore[too-many-arguments]
    *,
    codigo: str,
    cuenta: ApiUser,
    inscripcion_id: UUID,
    motivo_descripcion: str,
    motivo_id: UUID,
    qs: QuerySet,
) -> Inscripcion:
    """
    Cancel or reject an inscription; its holder may cancel their own.

    Returns:
        The closed inscription.

    Raises:
        ForbiddenError: The account neither holds it nor manages inscriptions.

    """

    propia: bool = Inscripcion.objects.filter(
        pk=inscripcion_id,
        user__user=cuenta,
    ).exists()

    if not propia and not puede(cuenta, "rudiparticipacion.change_inscripcion"):
        raise ForbiddenError

    return transicionar(
        actor=(ActorTypes.USER if propia else ActorTypes.ADMIN),
        cerrada_at=now(),
        codigo=codigo,
        entidad="inscripcion",
        motivo_descripcion=motivo_descripcion,
        motivo_id=motivo_id,
        pk=inscripcion_id,
        posicion_espera=None,
        qs=qs,
    )


########################################################################################
# participación


class ParticipacionCreateOperation[Get: DTO, Post: DTO](
    ForeignKeyCreateOperation[Get, Post],
):
    """
    A participation starts in the initial state; its year comes from the activity.
    """

    __slots__ = ()

    @override
    async def execute(self, data: dict) -> DatabaseModel:
        estado_id: UUID = await sync_to_async(func=initial_estado_id)("participacion")

        # `trg_participacion_snapshot` overwrites the year from the activity
        return await super().execute(data | {"anio": None, "estado_id": estado_id})


########################################################################################
# equipos


def nuevo_codigo_union() -> str:
    return "".join(choice(CODIGO_UNION) for _ in range(8))


@atomic
def crear_equipo(
    *,
    actividad_id: UUID,
    cuenta: ApiUser,
    nombre: str,
    qs: QuerySet,
) -> Equipo:
    persona: RudiUser | None = getattr(cuenta, "rudi", None)

    equipo: Equipo = Equipo.objects.create(
        actividad_id=actividad_id,
        codigo_union=nuevo_codigo_union(),
        creado_por=persona,
        nombre=nombre,
    )

    if persona is not None:
        EquipoMiembro.objects.create(equipo=equipo, is_lider=True, user=persona)

    return qs.get(pk=equipo.pk)


@atomic
def unirse_a_equipo(*, codigo_union: str, cuenta: ApiUser, qs: QuerySet) -> Equipo:
    equipo: Equipo | None = Equipo.objects.filter(codigo_union=codigo_union).first()

    if equipo is None:
        raise NotFoundError(field_errors={"codigo_union": codigo_union}).scoped(
            RequestScopes.BODY,
        )

    EquipoMiembro.objects.create(equipo=equipo, user=persona_de(cuenta))

    return qs.get(pk=equipo.pk)


########################################################################################
# asignación de mentores


class AsignacionMentorCreateOperation[Get: DTO, Post: DTO](
    ForeignKeyCreateOperation[Get, Post],
):
    __slots__ = ()

    @override
    async def execute(self, data: dict) -> DatabaseModel:
        estado_id: UUID = await sync_to_async(func=initial_estado_id)(
            "asignacion_mentor",
        )

        return await super().execute(data | {"estado_id": estado_id})


def responder_mentoria(
    *,
    asignacion_id: UUID,
    codigo: str,
    cuenta: ApiUser,
    qs: QuerySet,
    **cambios: object,
) -> AsignacionMentor:
    """
    Move a mentoring assignment; the mentor answers their own proposals.

    Returns:
        The moved assignment.

    Raises:
        ForbiddenError: The account is neither its mentor nor manages them.

    """

    propia: bool = AsignacionMentor.objects.filter(
        mentor__user__user=cuenta,
        pk=asignacion_id,
    ).exists()

    if not propia and not puede(cuenta, "rudiparticipacion.change_asignacionmentor"):
        raise ForbiddenError

    return transicionar(
        actor=(ActorTypes.USER if propia else ActorTypes.ADMIN),
        codigo=codigo,
        entidad="asignacion_mentor",
        pk=asignacion_id,
        qs=qs,
        **cambios,
    )


def vencer_propuestas_mentoria() -> int:
    """
    Expire mentoring proposals nobody answered in time (procesos.md).

    The deadline is `vigencia.propuesta_mentoria` (seven days if unset). A
    proposal is never confirmed by silence: it expires.

    Returns:
        How many proposals expired.

    """

    valor: object = (
        Parametro.objects
        .filter(codigo="vigencia.propuesta_mentoria", is_active=True)
        .values_list("valor", flat=True)
        .first()
    )

    plazo: timedelta = (
        parse_duration(valor) if isinstance(valor, str) else None
    ) or PLAZO_MENTORIA

    vencidas: int = 0

    for pk in AsignacionMentor.objects.filter(
        estado__initial=True,
        finalizada_at__isnull=True,
        propuesta_at__lt=(now() - plazo),
        respondida_at__isnull=True,
    ).values_list("pk", flat=True):
        try:
            transicionar(
                actor=ActorTypes.SYS,
                codigo="vencida",
                entidad="asignacion_mentor",
                pk=pk,
                qs=AsignacionMentor.objects.all(),
            )
        except IntegrityError:
            continue

        vencidas += 1

    return vencidas
