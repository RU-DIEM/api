from typing import Annotated, Any, cast

from pydantic import Field, create_model
from pydantic.fields import FieldInfo

from api_core.schemas.get import DTO

########################################################################################


def patch_annotation(field: FieldInfo) -> object:
    annotation: Any = field.annotation

    return Annotated[annotation, *field.metadata] if field.metadata else annotation


########################################################################################


def build_patch_schema[Put: type[DTO]](dto: Put) -> Put:
    kwargs: dict = {"__base__": dto} | {
        name: (patch_annotation(field), Field(default_factory=(lambda: None)))
        for name, field in dto.model_fields.items()
    }

    return cast(
        "Put",
        create_model(
            dto.__name__.replace("Put", "Patch"),
            **kwargs,
        ),
    )


########################################################################################


def build_put_schema[Post: type[DTO]](dto: Post) -> Post:
    kwargs: dict = {"__base__": dto}

    return create_model(
        dto.__name__.replace("Post", "Put").replace("Write", "Put"),
        **kwargs,
    )
