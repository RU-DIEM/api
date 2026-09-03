from api_core.schemas.factories import (
    build_filter_query,
    build_patch_schema,
    build_put_schema,
)
from api_core.schemas.filters import PaginatedFilterQuery, UnpaginatedFilterQuery
from rudi_catalogos.filtersets.reconocimiento import TipoReconocimientoFilterSet

from .base import (
    RudiCatalogoGet,
    RudiCatalogoInlineGet,
    RudiCatalogoPost,
    RudiCatalogoWrite,
)

########################################################################################


class TipoReconocimientoInlineGet(RudiCatalogoInlineGet):
    pass


class TipoReconocimientoGet(RudiCatalogoGet):
    pass


class TipoReconocimientoWrite(RudiCatalogoWrite):
    pass


class TipoReconocimientoPost(RudiCatalogoPost):
    pass


########################################################################################

TipoReconocimientoPut = build_put_schema(TipoReconocimientoWrite)
TipoReconocimientoPatch = build_patch_schema(TipoReconocimientoPut)

########################################################################################

TipoReconocimientoFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    TipoReconocimientoFilterSet,
)

TipoReconocimientoFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    TipoReconocimientoFilterSet,
)
