from typing import TYPE_CHECKING, override

from django.db.backends.postgresql.psycopg_any import DateRange
from django.db.models import Q, Sum
from django.db.transaction import atomic

from api_core.services.operations import (
    ForeignKeyCreateOperation,
    ForeignKeyUpdateOperation,
)
from api_exceptions.enums import RequestScopes
from api_exceptions.errors import NotFoundError
from rudi_estados.enums import ActorTypes
from rudi_estados.services.actor import set_actor
from rudi_puntos.enums import MovimientoOrigenTypes
from rudi_puntos.models import MovimientoPunto

if TYPE_CHECKING:
    from uuid import UUID

    from django.db.models import QuerySet

    from api_auth.models import ApiUser
    from api_core.schemas.base import DTO
    from api_utils.types import DatabaseModel

########################################################################################


def a_rango(data: dict) -> dict:
    """
    Turn the schema's `{lower, upper}` into the half-open `daterange` column.

    Returns:
        *data* with `vigencia` as a `DateRange`, when it was sent.

    """

    vigencia: dict | None = data.get("vigencia")

    if vigencia is None:
        return data

    return data | {
        "vigencia": DateRange(vigencia["lower"], vigencia.get("upper"), bounds="[)"),
    }


class ReglaPuntuacionCreateOperation[Get: DTO, Post: DTO](
    ForeignKeyCreateOperation[Get, Post],
):
    __slots__ = ()

    @override
    async def execute(self, data: dict) -> DatabaseModel:
        return await super().execute(a_rango(data))


class ReglaPuntuacionUpdateOperation[Get: DTO, Post: DTO](
    ForeignKeyUpdateOperation[Get, Post],
):
    __slots__ = ()

    @override
    async def execute(self, data: dict, lookup: dict) -> DatabaseModel:
        return await super().execute(a_rango(data), lookup)


########################################################################################


@atomic
def ajustar_puntos(  # ruff: ignore[too-many-arguments]
    *,
    anio: int,
    descripcion: str,
    motivo_id: UUID,
    participacion_id: UUID | None,
    puntos: int,
    qs: QuerySet,
    registrado_por: ApiUser,
    user_id: UUID,
) -> MovimientoPunto:
    """
    File a manual adjustment (RF-A-32).

    With a participation, `trg_movimientopunto_snapshot` takes the person and
    the year from it, whatever the body said.

    Returns:
        The new ledger entry.

    """

    set_actor(ActorTypes.ADMIN)

    movimiento: MovimientoPunto = MovimientoPunto.objects.create(
        anio=anio,
        descripcion=descripcion,
        motivo_id=motivo_id,
        origen=MovimientoOrigenTypes.MANUAL,
        participacion_id=participacion_id,
        puntos=puntos,
        registrado_por=registrado_por,
        user_id=user_id,
    )

    return qs.get(pk=movimiento.pk)


@atomic
def revertir_movimiento(
    *,
    descripcion: str,
    motivo_id: UUID,
    movimiento_id: UUID,
    qs: QuerySet,
    registrado_por: ApiUser,
) -> MovimientoPunto:
    """
    Revert a whole ledger entry with its exact opposite.

    `trg_movimientopunto_reverso_exacto` checks it, and
    `trg_movimientopunto_marcar_revertido` stamps the original.

    Returns:
        The reversal entry.

    """

    original: MovimientoPunto | None = MovimientoPunto.objects.filter(
        pk=movimiento_id,
    ).first()

    if original is None:
        raise NotFoundError(field_errors={"movimiento_id": str(movimiento_id)}).scoped(
            RequestScopes.BODY,
        )

    reverso: MovimientoPunto = MovimientoPunto.objects.create(
        anio=original.anio,
        descripcion=descripcion,
        motivo_id=motivo_id,
        origen=MovimientoOrigenTypes.REVERSO,
        participacion_id=original.participacion_id,  # ty: ignore[unresolved-attribute]
        puntos=-original.puntos,  # ty: ignore[unsupported-operator]
        registrado_por=registrado_por,
        revierte=original,
        user_id=original.user_id,  # ty: ignore[unresolved-attribute]
    )

    return qs.get(pk=reverso.pk)


########################################################################################


def saldo(user_id: UUID) -> dict:
    """
    Compute a person's live balance, split as RF-A-32 asks (puntos.md).

    Both the reverted entry and its reversal are left out: they cancel out,
    and the detail shows them anyway.

    Returns:
        `saldo`, `automatico` and `manual`.

    """

    vivos = MovimientoPunto.objects.filter(
        revertido_at__isnull=True,
        user_id=user_id,
    ).exclude(origen=MovimientoOrigenTypes.REVERSO)

    totales: dict = vivos.aggregate(
        automatico=Sum("puntos", filter=Q(origen=MovimientoOrigenTypes.AUTO)),
        manual=Sum("puntos", filter=~Q(origen=MovimientoOrigenTypes.AUTO)),
        saldo=Sum("puntos"),
    )

    return {"user_id": user_id} | {k: (v or 0) for k, v in totales.items()}
