from api_core.schemas.factories import (
    build_filter_query,
    build_patch_schema,
    build_put_schema,
)
from api_core.schemas.filters import PaginatedFilterQuery, UnpaginatedFilterQuery
from rudi_catalogos.filtersets.actividad import TipoActividadFilterSet

from .base import (
    RudiCatalogoGet,
    RudiCatalogoInlineGet,
    RudiCatalogoPost,
    RudiCatalogoWrite,
)

########################################################################################


class TipoActividadInlineGet(RudiCatalogoInlineGet):
    pass


class TipoActividadGet(RudiCatalogoGet):
    pass


class TipoActividadWrite(RudiCatalogoWrite):
    pass


class TipoActividadPost(RudiCatalogoPost):
    pass


########################################################################################

TipoActividadPut = build_put_schema(TipoActividadWrite)
TipoActividadPatch = build_patch_schema(TipoActividadPut)

########################################################################################

TipoActividadFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    TipoActividadFilterSet,
)

TipoActividadFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    TipoActividadFilterSet,
)
