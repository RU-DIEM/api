from api_core.controllers.mixins import ReadOnlyMixin
from api_core.controllers.models import (
    ModelListAllController,
    ModelReadOnlyDetailController,
)
from api_core.controllers.serializers import CustomPydanticFastSerializer
from rudi_estados.filtersets import (
    EstadoActividadFilterSet,
    EstadoAsignacionMentorFilterSet,
    EstadoConsentimientoFilterSet,
    EstadoConstanciaFilterSet,
    EstadoInscripcionFilterSet,
    EstadoParticipacionFilterSet,
    EstadoPropuestaFilterSet,
    EstadoRudiUserFilterSet,
)
from rudi_estados.models import (
    EstadoActividad,
    EstadoAsignacionMentor,
    EstadoConsentimiento,
    EstadoConstancia,
    EstadoInscripcion,
    EstadoParticipacion,
    EstadoPropuesta,
    EstadoRudiUser,
)
from rudi_estados.schemas import (
    EstadoActividadFilterAllQuery,
    EstadoActividadGet,
    EstadoAsignacionMentorFilterAllQuery,
    EstadoAsignacionMentorGet,
    EstadoConsentimientoFilterAllQuery,
    EstadoConsentimientoGet,
    EstadoConstanciaFilterAllQuery,
    EstadoConstanciaGet,
    EstadoInscripcionFilterAllQuery,
    EstadoInscripcionGet,
    EstadoParticipacionFilterAllQuery,
    EstadoParticipacionGet,
    EstadoPropuestaFilterAllQuery,
    EstadoPropuestaGet,
    EstadoRudiUserFilterAllQuery,
    EstadoRudiUserGet,
)

########################################################################################


class EstadoActividadDetailController(
    ReadOnlyMixin,
    ModelReadOnlyDetailController[
        CustomPydanticFastSerializer,
        EstadoActividad,
        EstadoActividadGet,
    ],
):
    pass


class EstadoActividadListAllController(
    ReadOnlyMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        EstadoActividad,
        EstadoActividadFilterSet,
        EstadoActividadFilterAllQuery,
        EstadoActividadGet,
        list[EstadoActividadGet],
    ],
):
    pass


########################################################################################


class EstadoAsignacionMentorDetailController(
    ReadOnlyMixin,
    ModelReadOnlyDetailController[
        CustomPydanticFastSerializer,
        EstadoAsignacionMentor,
        EstadoAsignacionMentorGet,
    ],
):
    pass


class EstadoAsignacionMentorListAllController(
    ReadOnlyMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        EstadoAsignacionMentor,
        EstadoAsignacionMentorFilterSet,
        EstadoAsignacionMentorFilterAllQuery,
        EstadoAsignacionMentorGet,
        list[EstadoAsignacionMentorGet],
    ],
):
    pass


########################################################################################


class EstadoConsentimientoDetailController(
    ReadOnlyMixin,
    ModelReadOnlyDetailController[
        CustomPydanticFastSerializer,
        EstadoConsentimiento,
        EstadoConsentimientoGet,
    ],
):
    pass


class EstadoConsentimientoListAllController(
    ReadOnlyMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        EstadoConsentimiento,
        EstadoConsentimientoFilterSet,
        EstadoConsentimientoFilterAllQuery,
        EstadoConsentimientoGet,
        list[EstadoConsentimientoGet],
    ],
):
    pass


########################################################################################


class EstadoConstanciaDetailController(
    ReadOnlyMixin,
    ModelReadOnlyDetailController[
        CustomPydanticFastSerializer,
        EstadoConstancia,
        EstadoConstanciaGet,
    ],
):
    pass


class EstadoConstanciaListAllController(
    ReadOnlyMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        EstadoConstancia,
        EstadoConstanciaFilterSet,
        EstadoConstanciaFilterAllQuery,
        EstadoConstanciaGet,
        list[EstadoConstanciaGet],
    ],
):
    pass


########################################################################################


class EstadoInscripcionDetailController(
    ReadOnlyMixin,
    ModelReadOnlyDetailController[
        CustomPydanticFastSerializer,
        EstadoInscripcion,
        EstadoInscripcionGet,
    ],
):
    pass


class EstadoInscripcionListAllController(
    ReadOnlyMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        EstadoInscripcion,
        EstadoInscripcionFilterSet,
        EstadoInscripcionFilterAllQuery,
        EstadoInscripcionGet,
        list[EstadoInscripcionGet],
    ],
):
    pass


########################################################################################


class EstadoParticipacionDetailController(
    ReadOnlyMixin,
    ModelReadOnlyDetailController[
        CustomPydanticFastSerializer,
        EstadoParticipacion,
        EstadoParticipacionGet,
    ],
):
    pass


class EstadoParticipacionListAllController(
    ReadOnlyMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        EstadoParticipacion,
        EstadoParticipacionFilterSet,
        EstadoParticipacionFilterAllQuery,
        EstadoParticipacionGet,
        list[EstadoParticipacionGet],
    ],
):
    pass


########################################################################################


class EstadoPropuestaDetailController(
    ReadOnlyMixin,
    ModelReadOnlyDetailController[
        CustomPydanticFastSerializer,
        EstadoPropuesta,
        EstadoPropuestaGet,
    ],
):
    pass


class EstadoPropuestaListAllController(
    ReadOnlyMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        EstadoPropuesta,
        EstadoPropuestaFilterSet,
        EstadoPropuestaFilterAllQuery,
        EstadoPropuestaGet,
        list[EstadoPropuestaGet],
    ],
):
    pass


########################################################################################


class EstadoRudiUserDetailController(
    ReadOnlyMixin,
    ModelReadOnlyDetailController[
        CustomPydanticFastSerializer,
        EstadoRudiUser,
        EstadoRudiUserGet,
    ],
):
    pass


class EstadoRudiUserListAllController(
    ReadOnlyMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        EstadoRudiUser,
        EstadoRudiUserFilterSet,
        EstadoRudiUserFilterAllQuery,
        EstadoRudiUserGet,
        list[EstadoRudiUserGet],
    ],
):
    pass
