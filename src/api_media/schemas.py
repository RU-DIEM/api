from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel as PydanticModel,
    PositiveInt,
)

from api_core.schemas.base import PermissiveDTO
from api_core.schemas.factories import build_filter_query
from api_core.schemas.filters import PaginatedFilterQuery
from api_core.schemas.get import BaseGet
from api_media.enums import MediaVisibility
from api_media.filtersets import ApiMediaFilterSet

########################################################################################


class ApiMediaGet(BaseGet):
    visibility: MediaVisibility
    mime: str
    size: PositiveInt
    width: PositiveInt | None
    height: PositiveInt | None
    checksum: str
    uploaded_by_id: UUID
    created_at: datetime
    url: str


########################################################################################


class ApiMediaPost(PermissiveDTO):
    visibility: MediaVisibility = MediaVisibility.PUBLIC


class ApiMediaUploadMetadata(PydanticModel):
    model_config = PermissiveDTO.model_config

    content_type: str
    size: PositiveInt


class ApiMediaUpload(PydanticModel):
    model_config = PermissiveDTO.model_config

    file: ApiMediaUploadMetadata


########################################################################################

ApiMediaFilterQuery = build_filter_query(PaginatedFilterQuery, ApiMediaFilterSet)
