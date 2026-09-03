from api_core.schemas.factories import (
    build_filter_query,
    build_patch_schema,
    build_put_schema,
)
from api_core.schemas.filters import PaginatedFilterQuery, UnpaginatedFilterQuery
from rudi_catalogos.filtersets.rol import RolParticipacionFilterSet

from .base import (
    RudiCatalogoGet,
    RudiCatalogoInlineGet,
    RudiCatalogoPost,
    RudiCatalogoWrite,
)

########################################################################################


class RolParticipacionInlineGet(RudiCatalogoInlineGet):
    pass


class RolParticipacionGet(RudiCatalogoGet):
    pass


class RolParticipacionWrite(RudiCatalogoWrite):
    pass


class RolParticipacionPost(RudiCatalogoPost):
    pass


########################################################################################

RolParticipacionPut = build_put_schema(RolParticipacionWrite)
RolParticipacionPatch = build_patch_schema(RolParticipacionPut)

########################################################################################

RolParticipacionFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    RolParticipacionFilterSet,
)

RolParticipacionFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    RolParticipacionFilterSet,
)
