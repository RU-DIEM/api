from typing import Annotated

from pydantic import StringConstraints

from api_core.schemas.base import DTO
from api_core.schemas.get import BaseGet

########################################################################################

type CatalogoCodigo = Annotated[
    str,
    StringConstraints(max_length=50, min_length=1, pattern=r"^[a-z][a-z0-9_]*$"),
]

type CatalogoDescripcion = Annotated[str, StringConstraints(max_length=300)]

type CatalogoEtiqueta = Annotated[str, StringConstraints(max_length=100, min_length=1)]

type CatalogoRegex = Annotated[str, StringConstraints(max_length=100)]

########################################################################################


class RudiCatalogoInlineGet(BaseGet):
    codigo: str
    etiqueta: str


########################################################################################


class RudiCatalogoGet(RudiCatalogoInlineGet):
    descripcion: str
    is_active: bool


########################################################################################


class RudiCatalogoWrite(DTO):
    etiqueta: CatalogoEtiqueta
    descripcion: CatalogoDescripcion = ""
    is_active: bool = True


########################################################################################


class RudiCatalogoPost(RudiCatalogoWrite):
    codigo: CatalogoCodigo
