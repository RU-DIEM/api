from typing import ClassVar, override

from dmr import Body, FileMetadata
from dmr.parsers import MultiPartParser

from api_core.controllers.models import (
    ModelListController,
    ModelReadOnlyDetailController,
)
from api_core.controllers.serializers import (
    CustomPydanticFastSerializer,
    CustomPydanticSerializer,
)
from api_core.schemas.pagination import Paginated
from api_core.services.mappers import ModelMapper
from api_core.services.operations import CreateOperation
from api_media.filtersets import ApiMediaFilterSet
from api_media.models import ApiMedia
from api_media.schemas import (
    ApiMediaFilterQuery,
    ApiMediaGet,
    ApiMediaPost,
    ApiMediaUpload,
)
from api_media.services.media import MediaUploadOperation, media_mapper

########################################################################################


class ApiMediaListController(
    ModelListController[
        CustomPydanticSerializer,
        ApiMedia,
        ApiMediaFilterSet,
        ApiMediaFilterQuery,
        ApiMediaGet,
        ApiMediaPost,
        Paginated[ApiMediaGet],
    ],
):
    create_operation: ClassVar[type[CreateOperation]] = MediaUploadOperation
    mapper: ModelMapper[ApiMediaGet] = staticmethod(media_mapper)  # ty: ignore[invalid-assignment]

    parsers = (MultiPartParser(),)

    @override
    async def post(  # ty: ignore[invalid-method-override]
        self,
        parsed_body: Body[ApiMediaPost],
        parsed_file_metadata: FileMetadata[ApiMediaUpload],
    ) -> ApiMediaGet:
        return await self.build_operation(
            MediaUploadOperation,
            user=self.request.user,
        ).run(body=parsed_body, file=self.request.FILES["file"])


########################################################################################


class ApiMediaDetailController(
    ModelReadOnlyDetailController[
        CustomPydanticFastSerializer,
        ApiMedia,
        ApiMediaGet,
    ],
):
    mapper: ModelMapper[ApiMediaGet] = staticmethod(media_mapper)  # ty: ignore[invalid-assignment]
