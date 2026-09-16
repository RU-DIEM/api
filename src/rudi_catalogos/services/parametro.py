from typing import TYPE_CHECKING, override

from api_core.services.operations.flat import FlatUpdateOperation
from api_exceptions.enums import BadRequestErrorTypes, RequestScopes
from api_exceptions.errors import BadRequestError, NotFoundError
from api_utils.dates import format_duration, parse_duration
from rudi_catalogos.enums import ParametroTypes
from rudi_catalogos.models import Parametro

if TYPE_CHECKING:
    from datetime import timedelta

    from django.db.models import QuerySet

    from api_auth.models import ApiUser
    from api_core.schemas.base import DTO
    from api_core.services.mappers import ModelMapper
    from api_utils.types import DatabaseModel
    from rudi_catalogos.schemas.parametro import ParametroValor

########################################################################################


async def read_parametro(codigo: str, tipo: ParametroTypes):  # ruff: ignore[missing-return-type-undocumented-public-function]
    parametro: Parametro | None = await Parametro.objects.filter(
        codigo=codigo,
        is_active=True,
        tipo=tipo,
    ).afirst()

    if parametro is None:
        raise NotFoundError(field_errors={"codigo": codigo, "tipo": tipo})

    return parametro.valor


########################################################################################


async def read_duracion(codigo: str) -> timedelta:
    return parse_duration(await read_parametro(codigo, ParametroTypes.TIME))


########################################################################################


def reject(detail: str) -> BadRequestError:
    return BadRequestError(
        field_errors={"valor": detail},
        type=BadRequestErrorTypes.FAILED_VALIDATION,
    ).scoped(RequestScopes.BODY)


########################################################################################


def check_shape(tipo: ParametroTypes, valor: ParametroValor) -> ParametroValor:
    match tipo:
        case ParametroTypes.BOOL if not isinstance(valor, bool):
            raise reject("Este parámetro exige un valor booleano.")
        case ParametroTypes.INT if isinstance(valor, bool) or not isinstance(
            valor,
            int,
        ):
            raise reject("Este parámetro exige un número entero.")
        case ParametroTypes.LIST if not isinstance(valor, list):
            raise reject("Este parámetro exige una lista de textos.")
        case ParametroTypes.STR | ParametroTypes.TIME if not isinstance(valor, str):
            raise reject("Este parámetro exige un texto.")
        case _:
            pass

    if tipo is not ParametroTypes.TIME or not isinstance(valor, str):
        return valor

    try:
        return format_duration(parse_duration(valor))
    except ValueError as v:
        raise reject(
            "La duración debe seguir el formato ISO 8601, como PT30M o P365D.",
        ) from v


########################################################################################


def check_limits(restricciones: dict, valor: ParametroValor) -> None:
    choices = restricciones.get("choices")

    if choices is not None:
        pending = (
            set(valor) - set(choices)
            if isinstance(valor, list)
            else {valor} - set(choices)
        )

        if pending:
            raise reject(
                f"Valores no admitidos: {', '.join(sorted(str(p) for p in pending))}.",
            )

    if not isinstance(valor, int) or isinstance(valor, bool):
        return

    minimo = restricciones.get("min")
    maximo = restricciones.get("max")

    if minimo is not None and valor < minimo:
        raise reject(f"El valor mínimo admitido es {minimo}.")

    if maximo is not None and valor > maximo:
        raise reject(f"El valor máximo admitido es {maximo}.")


########################################################################################


class ParametroUpdateOperation[Get: DTO, Post: DTO](FlatUpdateOperation[Get, Post]):
    __slots__ = ("actor",)

    def __init__(
        self,
        *fields: str,
        actor: ApiUser,
        mapper: ModelMapper[Get],
        partial: bool = False,
        schema: type[Get],
        qs: QuerySet,
    ) -> None:
        super().__init__(*fields, mapper=mapper, partial=partial, schema=schema, qs=qs)

        self.actor: ApiUser = actor

    @override
    async def execute(self, data: dict, lookup: dict) -> DatabaseModel:
        parametro: Parametro = await self.qs.aget(**lookup)

        if not data:
            return parametro

        if "valor" in data:
            valor: ParametroValor = check_shape(
                tipo=ParametroTypes(parametro.tipo),
                valor=data["valor"],
            )

            check_limits(
                restricciones=parametro.restricciones,  # ty: ignore[invalid-argument-type]
                valor=valor,
            )

            data["valor"] = valor

        data["updated_by"] = self.actor

        return await super().execute(data, lookup)
