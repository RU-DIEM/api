from api_core.schemas.base import DTO
from api_core.schemas.factories import (
    build_filter_query,
    build_patch_schema,
    build_put_schema,
)
from api_core.schemas.filters import PaginatedFilterQuery, UnpaginatedFilterQuery
from api_core.schemas.get import LaxEnum
from rudi_catalogos.enums import MotivoAmbitoTypes, MotivoVisibilidadTypes
from rudi_catalogos.filtersets.motivo import MotivoFilterSet

from .base import CatalogoCodigo, CatalogoEtiqueta, RudiCatalogoInlineGet

########################################################################################


class MotivoInlineGet(RudiCatalogoInlineGet):
    ambito: MotivoAmbitoTypes


########################################################################################


class MotivoGet(MotivoInlineGet):
    is_active: bool
    require_descripcion: bool
    visibilidad: MotivoVisibilidadTypes


########################################################################################


class MotivoWrite(DTO):
    etiqueta: CatalogoEtiqueta
    is_active: bool = True

    require_descripcion: bool = False
    visibilidad: LaxEnum[MotivoVisibilidadTypes] = MotivoVisibilidadTypes.ADMIN


########################################################################################


class MotivoPost(MotivoWrite):
    ambito: LaxEnum[MotivoAmbitoTypes]
    codigo: CatalogoCodigo


########################################################################################

MotivoPut = build_put_schema(MotivoWrite)
MotivoPatch = build_patch_schema(MotivoPut)

########################################################################################

MotivoFilterQuery = build_filter_query(PaginatedFilterQuery, MotivoFilterSet)

MotivoFilterAllQuery = build_filter_query(UnpaginatedFilterQuery, MotivoFilterSet)
