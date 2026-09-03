from api_core.schemas.factories import (
    build_filter_query,
    build_patch_schema,
    build_put_schema,
)
from api_core.schemas.filters import PaginatedFilterQuery, UnpaginatedFilterQuery
from rudi_catalogos.filtersets.area import AreaExperienciaFilterSet

from .base import (
    RudiCatalogoGet,
    RudiCatalogoInlineGet,
    RudiCatalogoPost,
    RudiCatalogoWrite,
)

########################################################################################


class AreaExperienciaInlineGet(RudiCatalogoInlineGet):
    pass


class AreaExperienciaGet(RudiCatalogoGet):
    pass


class AreaExperienciaWrite(RudiCatalogoWrite):
    pass


class AreaExperienciaPost(RudiCatalogoPost):
    pass


########################################################################################

AreaExperienciaPut = build_put_schema(AreaExperienciaWrite)
AreaExperienciaPatch = build_patch_schema(AreaExperienciaPut)

########################################################################################

AreaExperienciaFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    AreaExperienciaFilterSet,
)

AreaExperienciaFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    AreaExperienciaFilterSet,
)
