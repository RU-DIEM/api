from typing import TYPE_CHECKING, Final, override

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.db.transaction import atomic
from django.utils.timezone import now
from django.views.decorators.debug import sensitive_variables

from api_auth.enums import VerificationPurposes
from api_auth.models import ApiUser
from api_auth.schemas.user import ApiUserBaseWrite
from api_auth.services.user import (
    check_password_match,
    check_password_strength,
    dump_user_post_data,
)
from api_core.services.operations import CreateOperation
from api_core.services.operations.m2m import write_m2m_post
from api_exceptions.enums import ConflictErrorTypes, RequestScopes
from api_exceptions.errors import ConflictError
from api_utils.db import set_immediate_constraints
from rudi_auth.enums import ConsentimientoCanalTypes
from rudi_auth.models import (
    ConsentimientoDatos,
    IdentificadorUser,
    PoliticaPrivacidad,
    RudiUser,
)
from rudi_estados.enums import InputSourceTypes

from .estados import (
    initial_estado_consentimiento,
    initial_estado_user,
)
from .politica import load_politica_vigente
from .verificacion import issue_codigo

if TYPE_CHECKING:
    from api_core.schemas.base import DTO
    from api_utils.types import DatabaseModel
    from rudi_estados.models import EstadoConsentimiento, EstadoRudiUser

########################################################################################

CUENTA_FIELDS: Final[frozenset[str]] = frozenset({
    *ApiUserBaseWrite.model_fields,
    "groups",
    "password",
})

PERSONA_FIELDS: Final[frozenset[str]] = frozenset({
    "etnia",
    "fecha_nacimiento",
    "genero",
    "talla",
    "telefono",
})

########################################################################################


def check_cuenta_disponible(email: str, username: str) -> None:
    tomados: dict[str, str] = {
        campo: valor
        for campo, valor in (("email", email), ("username", username))
        if get_user_model().objects.filter(**{f"{campo}__iexact": valor}).exists()
    }

    if not tomados:
        return

    raise ConflictError(
        field_errors=dict.fromkeys(
            tomados,
            "Ya existe una cuenta registrada con este valor.",
        ),
        type=ConflictErrorTypes.UNIQUE,
    ).scoped(RequestScopes.BODY)


########################################################################################


class RudiUserCreateOperation[Get: DTO, Post: DTO](CreateOperation[Get, Post]):
    __slots__ = ()

    canal: ConsentimientoCanalTypes = ConsentimientoCanalTypes.PORTAL
    origen: InputSourceTypes = InputSourceTypes.SELF
    proposito: VerificationPurposes = VerificationPurposes.EMAIL

    @override
    @sensitive_variables()
    def dump(self, dto: Post) -> dict:
        # the account half is dumped exactly as the template's registration
        # dumps it: same checks, same groups, same password handling
        if dto.password1 is not None:  # ty: ignore[unresolved-attribute]
            check_password_match(dto)
            check_password_strength(dto)

        data: dict = dump_user_post_data(dto)

        return {
            "cuenta": {name: data[name] for name in CUENTA_FIELDS},
            "identificador": data.get("identificador"),
            "persona": {name: data[name] for name in PERSONA_FIELDS if name in data},
        }

    @override
    @sensitive_variables()
    async def execute(self, data: dict) -> DatabaseModel:
        estado = await initial_estado_user()
        consentimiento = await initial_estado_consentimiento(self.origen)
        politica = await load_politica_vigente()

        user: RudiUser = await sync_to_async(func=self.persist)(
            consentimiento=consentimiento,
            data=data,
            estado=estado,
            politica=politica,
        )

        await issue_codigo(
            proposito=self.proposito,
            user=user.user,
        )

        return user

    @atomic
    @sensitive_variables()
    def persist(
        self,
        consentimiento: EstadoConsentimiento,
        data: dict,
        estado: EstadoRudiUser,
        politica: PoliticaPrivacidad,
    ) -> RudiUser:
        identificador: dict | None = data["identificador"]

        check_cuenta_disponible(
            email=data["cuenta"]["email"],
            username=data["cuenta"]["username"],
        )

        # the template's own account creation, minus its retrying transaction,
        # so the account commits (or not) together with the persona. Whether
        # it may log in follows the persona's state (`trg_rudiuser_sync_active`)
        cuenta: ApiUser = write_m2m_post(  # ty: ignore[invalid-assignment]
            "groups",
            data=data["cuenta"],
            qs=ApiUser.objects.all(),
            user=True,
        )

        user: RudiUser = RudiUser.objects.create(
            estado=estado,
            origen=self.origen,
            user=cuenta,
            **data["persona"],
        )

        ConsentimientoDatos.objects.create(
            canal=self.canal,
            estado=consentimiento,
            otorgado_at=now(),
            politica=politica,
            user=user,
        )

        if identificador is not None:
            IdentificadorUser.objects.create(
                is_main=True,
                tipo_id=identificador["tipo"],
                user=user,
                valor=identificador["valor"],
            )

        set_immediate_constraints()

        return user


########################################################################################


class RudiInviteCreateOperation[Get: DTO, Post: DTO](
    RudiUserCreateOperation[Get, Post]
):
    __slots__ = ()

    canal: ConsentimientoCanalTypes = ConsentimientoCanalTypes.PAPER
    origen: InputSourceTypes = InputSourceTypes.MODERN
    proposito: VerificationPurposes = VerificationPurposes.INVITATION
