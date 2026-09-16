from datetime import datetime
from typing import Annotated, Final

from pydantic import AfterValidator, Field, StringConstraints

from api_core.schemas.base import DTO
from api_core.schemas.factories import (
    build_filter_query,
    build_patch_schema,
    build_put_schema,
)
from api_core.schemas.filters import PaginatedFilterQuery, UnpaginatedFilterQuery
from api_core.schemas.get import BaseGet, RelatedId
from api_core.schemas.validators import empty_or_url
from api_utils.dates import current_year
from rudi_catalogos.schemas.area import AreaExperienciaInlineGet
from rudi_catalogos.schemas.mentor import TipoMentorInlineGet
from rudi_catalogos.schemas.ubicaciones import MunicipioInlineGet
from rudi_profiles.filtersets.mentor import (
    MentorAreaExperienciaFilterSet,
    MentorCertificacionFilterSet,
    MentorProfileFilterSet,
)

from .base import RudiProfileGet, RudiProfileInlineGet
from .docente import NivelAcademico

########################################################################################

MIN_CERTIFICACION_YEAR: Final[int] = 1960

########################################################################################

type CertificacionInstitucion = Annotated[str, StringConstraints(max_length=200)]

type CertificacionNombre = Annotated[
    str,
    StringConstraints(max_length=200, min_length=2),
]

type CertificacionYear = Annotated[
    int,
    Field(ge=MIN_CERTIFICACION_YEAR, le=(current_year() + 1)),
]

type EnlaceUrl = Annotated[
    str,
    AfterValidator(func=empty_or_url),
    StringConstraints(max_length=500),
]

type MentorDescripcion = Annotated[str, StringConstraints(max_length=4_000)]

type MentorDireccion = Annotated[str, StringConstraints(max_length=2_000)]

type MentorNecesidades = Annotated[str, StringConstraints(max_length=2_000)]

########################################################################################


class MentorAreaExperienciaGet(BaseGet):
    area: AreaExperienciaInlineGet

    is_main: bool


########################################################################################


class MentorAreaExperienciaWrite(DTO):
    is_main: bool = False


########################################################################################


class MentorAreaExperienciaPost(MentorAreaExperienciaWrite):
    area: RelatedId


########################################################################################


class MentorCertificacionGet(BaseGet):
    nombre: str
    institucion: str

    year: int | None

    enlace_url: str


########################################################################################


class MentorCertificacionWrite(DTO):
    nombre: CertificacionNombre
    institucion: CertificacionInstitucion = ""

    year: CertificacionYear | None = None

    enlace_url: EnlaceUrl = ""


########################################################################################


class MentorCertificacionPost(MentorCertificacionWrite):
    pass


########################################################################################


class MentorProfileInlineGet(RudiProfileInlineGet):
    tipo_mentor: TipoMentorInlineGet | None


########################################################################################


class MentorProfileGet(RudiProfileGet):
    tipo_mentor: TipoMentorInlineGet | None
    municipio: MunicipioInlineGet | None

    nivel_academico: NivelAcademico

    direccion: str
    descripcion_profesional: str
    necesidades_formacion: str

    confirmado_at: datetime | None


########################################################################################


class MentorProfileWrite(DTO):
    tipo_mentor: RelatedId | None = None
    municipio: RelatedId | None = None

    nivel_academico: NivelAcademico = ""

    direccion: MentorDireccion = ""
    descripcion_profesional: MentorDescripcion = ""
    necesidades_formacion: MentorNecesidades = ""


########################################################################################


class MentorProfilePost(MentorProfileWrite):
    user: RelatedId


########################################################################################

MentorAreaExperienciaPut = build_put_schema(MentorAreaExperienciaWrite)
MentorAreaExperienciaPatch = build_patch_schema(MentorAreaExperienciaPut)

MentorCertificacionPut = build_put_schema(MentorCertificacionWrite)
MentorCertificacionPatch = build_patch_schema(MentorCertificacionPut)

MentorProfilePut = build_put_schema(MentorProfileWrite)
MentorProfilePatch = build_patch_schema(MentorProfilePut)

########################################################################################

MentorAreaExperienciaFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    MentorAreaExperienciaFilterSet,
)

MentorCertificacionFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    MentorCertificacionFilterSet,
)

MentorProfileFilterQuery = build_filter_query(
    PaginatedFilterQuery,
    MentorProfileFilterSet,
)

MentorProfileFilterAllQuery = build_filter_query(
    UnpaginatedFilterQuery,
    MentorProfileFilterSet,
)
