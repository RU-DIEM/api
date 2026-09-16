from typing import TYPE_CHECKING

from asgiref.sync import sync_to_async
from django.db.transaction import atomic
from django.utils.timezone import now

from api_exceptions.enums import BadRequestErrorTypes, RequestScopes
from api_exceptions.errors import BadRequestError, NotFoundError
from rudi_auth.models import ConsentimientoDatos
from rudi_catalogos.enums import MotivoAmbitoTypes
from rudi_catalogos.models import Motivo
from rudi_estados.models import EstadoConsentimiento

if TYPE_CHECKING:
    from uuid import UUID

    from rudi_auth.schemas.consentimiento import ConsentimientoRetiroPost

########################################################################################


async def resolve_estado_retiro() -> EstadoConsentimiento:
    estado: EstadoConsentimiento | None = (
        await EstadoConsentimiento.objects
        .filter(
            allow_comunicacion=False,
            allow_reporte=False,
            is_active=True,
            terminal=True,
        )
        .order_by("pk")
        .afirst()
    )

    if estado is None:
        raise NotFoundError(
            detail="No hay un estado de retiro de consentimiento configurado.",
        )

    return estado


########################################################################################


async def load_motivo_retiro(motivo_id: UUID) -> Motivo:
    motivo: Motivo | None = await Motivo.objects.filter(
        ambito=MotivoAmbitoTypes.REVOKE_CONSENTIMIENTO,
        is_active=True,
        pk=motivo_id,
    ).afirst()

    if motivo is None:
        raise BadRequestError(
            field_errors={
                "motivo": (
                    "El motivo no existe o no pertenece al ámbito "
                    f"'{MotivoAmbitoTypes.REVOKE_CONSENTIMIENTO.value}'."
                ),
            },
            type=BadRequestErrorTypes.FAILED_VALIDATION,
        ).scoped(RequestScopes.BODY)

    return motivo


########################################################################################


async def retirar_consentimiento(
    data: ConsentimientoRetiroPost,
    user_id: UUID,
) -> ConsentimientoDatos:
    consentimiento: (
        ConsentimientoDatos | None
    ) = await ConsentimientoDatos.objects.filter(user_id=user_id).afirst()

    if consentimiento is None:
        raise NotFoundError(field_errors={"user_id": str(user_id)}).scoped(
            RequestScopes.PATH,
        )

    motivo: Motivo = await load_motivo_retiro(data.motivo)

    if motivo.require_descripcion and not data.descripcion:
        raise BadRequestError(
            field_errors={"descripcion": "Este motivo exige una descripción."},
            type=BadRequestErrorTypes.FAILED_VALIDATION,
        ).scoped(RequestScopes.BODY)

    if consentimiento.retirado_at is not None:
        raise BadRequestError(
            field_errors={"motivo": "El consentimiento ya fue retirado."},
            type=BadRequestErrorTypes.FAILED_VALIDATION,
        ).scoped(RequestScopes.BODY)

    estado: EstadoConsentimiento = await resolve_estado_retiro()

    @atomic
    def persist() -> None:
        consentimiento.estado = estado
        consentimiento.retirado_at = now()

        consentimiento.save(
            update_fields=("estado", "retirado_at", "updated_at"),
        )

    await sync_to_async(func=persist)()

    return consentimiento
