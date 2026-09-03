from api_core.schemas.factories import (
    build_filter_query,
    build_patch_schema,
    build_put_schema,
)
from api_core.schemas.filters import PaginatedFilterQuery, UnpaginatedFilterQuery
from rudi_catalogos.filtersets.mentor import TipoMentorFilterSet

from .base import (
    RudiCatalogoGet,
    RudiCatalogoInlineGet,
    RudiCatalogoPost,
    RudiCatalogoWrite,
)

########################################################################################


class TipoMentorInlineGet(RudiCatalogoInlineGet):
    pass


class TipoMentorGet(RudiCatalogoGet):
    pass


class TipoMentorWrite(RudiCatalogoWrite):
    pass


class TipoMentorPost(RudiCatalogoPost):
    pass


########################################################################################

TipoMentorPut = build_put_schema(TipoMentorWrite)
TipoMentorPatch = build_patch_schema(TipoMentorPut)

########################################################################################

TipoMentorFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    TipoMentorFilterSet,
)

TipoMentorFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    TipoMentorFilterSet,
)
