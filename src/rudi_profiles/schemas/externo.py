from typing import Annotated, Self

from pydantic import StringConstraints, model_validator

from api_core.schemas.base import DTO
from api_core.schemas.factories import (
    build_filter_query,
    build_patch_schema,
    build_put_schema,
)
from api_core.schemas.filters import PaginatedFilterQuery, UnpaginatedFilterQuery
from api_core.schemas.get import LaxEnum, RelatedId
from rudi_profiles.enums import OcupacionTypes
from rudi_profiles.filtersets.externo import ExternoProfileFilterSet
from rudi_profiles.schemas.academia import InstitucionInlineGet

from .base import RudiProfileGet, RudiProfileInlineGet

########################################################################################

type CarreraExterna = Annotated[str, StringConstraints(max_length=150)]

type OcupacionDetalle = Annotated[str, StringConstraints(max_length=500)]

########################################################################################


class ExternoProfileInlineGet(RudiProfileInlineGet):
    ocupacion: OcupacionTypes


########################################################################################


class ExternoProfileGet(RudiProfileGet):
    institucion: InstitucionInlineGet

    ocupacion: OcupacionTypes
    ocupacion_detalle: str

    carrera_externa: str


########################################################################################


class ExternoProfileWrite(DTO):
    institucion: RelatedId

    ocupacion: LaxEnum[OcupacionTypes]
    ocupacion_detalle: OcupacionDetalle = ""

    carrera_externa: CarreraExterna = ""

    @model_validator(mode="after")
    def check_carrera_externa(self) -> Self:
        if self.carrera_externa and self.ocupacion is not OcupacionTypes.ESTUDIANTE:
            raise ValueError(
                "Solo un perfil con ocupación de estudiante "
                "puede declarar una carrera externa.",
            )

        return self


########################################################################################


class ExternoProfilePost(ExternoProfileWrite):
    user: RelatedId


########################################################################################

ExternoProfilePut = build_put_schema(ExternoProfileWrite)
ExternoProfilePatch = build_patch_schema(ExternoProfilePut)

########################################################################################

ExternoProfileFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    ExternoProfileFilterSet,
)

ExternoProfileFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    ExternoProfileFilterSet,
)
