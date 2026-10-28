from collections.abc import Sequence
from http import HTTPMethod, HTTPStatus
from typing import ClassVar

from django.utils.timezone import now
from dmr import Body, modify

from api_auth.services.permissions import T_CHANGE_PERM
from api_core.controllers.mixins import OpenReadMixin
from api_core.controllers.models import (
    ModelController,
    ModelListAllController,
    ModelListController,
    ModelReadOnlyDetailController,
    ModelReadUpdateDetailController,
    ScopedDetailController,
    ScopedListController,
)
from api_core.controllers.serializers import CustomPydanticFastSerializer
from api_core.schemas.factories import build_scoped_path
from api_core.schemas.pagination import Paginated
from api_core.services.operations import (
    CreateOperation,
    ForeignKeyUpdateOperation,
    UpdateOperation,
)
from rudi_auth.services.persona import persona_de
from rudi_core.services import ejecutar
from rudi_estados.enums import ActorTypes, InputSourceTypes
from rudi_estados.services.transicion import transicionar
from rudi_participacion.filtersets import (
    AsignacionMentorFilterSet,
    EquipoFilterSet,
    EquipoMiembroFilterSet,
    InscripcionFilterSet,
    ParticipacionFilterSet,
    ReconocimientoFilterSet,
)
from rudi_participacion.models import (
    AsignacionMentor,
    Equipo,
    EquipoMiembro,
    Inscripcion,
    Participacion,
    Reconocimiento,
)
from rudi_participacion.schemas import (
    AsignacionAccionPost,
    AsignacionCierrePost,
    AsignacionMentorFilterQuery,
    AsignacionMentorGet,
    AsignacionMentorPatch,
    AsignacionMentorPost,
    AsignacionMentorPut,
    EquipoFilterAllQuery,
    EquipoFilterQuery,
    EquipoGet,
    EquipoMiembroFilterQuery,
    EquipoMiembroGet,
    EquipoMiembroPatch,
    EquipoMiembroPost,
    EquipoMiembroPut,
    EquipoPatch,
    EquipoPost,
    EquipoPut,
    InscribirmePost,
    InscripcionAccionPost,
    InscripcionCierrePost,
    InscripcionFilterQuery,
    InscripcionGet,
    InscripcionPost,
    ParticipacionAnularPost,
    ParticipacionFilterQuery,
    ParticipacionGet,
    ParticipacionPatch,
    ParticipacionPost,
    ParticipacionPut,
    ParticipacionValidarPost,
    ReconocimientoFilterQuery,
    ReconocimientoGet,
    ReconocimientoPatch,
    ReconocimientoPost,
    ReconocimientoPut,
    UnirmeEquipoPost,
)
from rudi_participacion.services import (
    AsignacionMentorCreateOperation,
    ParticipacionCreateOperation,
    cerrar_inscripcion,
    crear_equipo,
    inscribir,
    responder_mentoria,
    unirse_a_equipo,
)

########################################################################################

ADMIN_PERMISSIONS: dict[HTTPMethod, Sequence[str]] = {HTTPMethod.POST: (T_CHANGE_PERM,)}

# the service checks ownership: a participant acts on their own rows only
OPEN_PERMISSIONS: dict[HTTPMethod, Sequence[str]] = {HTTPMethod.POST: ()}

########################################################################################
# inscripción


class InscripcionDetailController(
    ModelReadOnlyDetailController[
        CustomPydanticFastSerializer,
        Inscripcion,
        InscripcionGet,
    ],
):
    pass


class InscripcionListController(
    ModelListController[
        CustomPydanticFastSerializer,
        Inscripcion,
        InscripcionFilterSet,
        InscripcionFilterQuery,
        InscripcionGet,
        InscripcionPost,
        Paginated[InscripcionGet],
    ],
):
    async def post(self, parsed_body: Body[InscripcionPost]) -> InscripcionGet:
        inscripcion: Inscripcion = await ejecutar(
            inscribir,
            actividad_id=parsed_body.actividad,
            creada_por=self.request.user,
            is_excepcion_cupo=parsed_body.is_excepcion_cupo,
            origen=InputSourceTypes.MODERN,
            persona_id=parsed_body.user,
            qs=self.qs,
        )

        return self.mapper(inscripcion, self.schema)


class InscribirmeController(
    ModelController[CustomPydanticFastSerializer, Inscripcion, InscripcionGet],
):
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = OPEN_PERMISSIONS

    async def post(self, parsed_body: Body[InscribirmePost]) -> InscripcionGet:
        persona = await ejecutar(persona_de, cuenta=self.request.user)

        inscripcion: Inscripcion = await ejecutar(
            inscribir,
            actividad_id=parsed_body.actividad_id,
            creada_por=None,
            origen=InputSourceTypes.SELF,
            persona_id=persona.pk,
            qs=self.qs,
        )

        return self.mapper(inscripcion, self.schema)


class ConfirmarInscripcionController(
    ModelController[CustomPydanticFastSerializer, Inscripcion, InscripcionGet],
):
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = ADMIN_PERMISSIONS

    @modify(status_code=HTTPStatus.OK)
    async def post(self, parsed_body: Body[InscripcionAccionPost]) -> InscripcionGet:
        inscripcion: Inscripcion = await ejecutar(
            transicionar,
            actor=ActorTypes.ADMIN,
            codigo="confirmada",
            confirmada_at=now(),
            entidad="inscripcion",
            pk=parsed_body.inscripcion_id,
            qs=self.qs,
        )

        return self.mapper(inscripcion, self.schema)


class RechazarInscripcionController(
    ModelController[CustomPydanticFastSerializer, Inscripcion, InscripcionGet],
):
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = ADMIN_PERMISSIONS

    @modify(status_code=HTTPStatus.OK)
    async def post(self, parsed_body: Body[InscripcionCierrePost]) -> InscripcionGet:
        inscripcion: Inscripcion = await ejecutar(
            cerrar_inscripcion,
            codigo="rechazada",
            cuenta=self.request.user,
            inscripcion_id=parsed_body.inscripcion_id,
            motivo_descripcion=parsed_body.motivo_descripcion,
            motivo_id=parsed_body.motivo_id,
            qs=self.qs,
        )

        return self.mapper(inscripcion, self.schema)


class CancelarInscripcionController(
    ModelController[CustomPydanticFastSerializer, Inscripcion, InscripcionGet],
):
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = OPEN_PERMISSIONS

    @modify(status_code=HTTPStatus.OK)
    async def post(self, parsed_body: Body[InscripcionCierrePost]) -> InscripcionGet:
        inscripcion: Inscripcion = await ejecutar(
            cerrar_inscripcion,
            codigo="cancelada",
            cuenta=self.request.user,
            inscripcion_id=parsed_body.inscripcion_id,
            motivo_descripcion=parsed_body.motivo_descripcion,
            motivo_id=parsed_body.motivo_id,
            qs=self.qs,
        )

        return self.mapper(inscripcion, self.schema)


########################################################################################
# participación


class ParticipacionDetailController(
    ModelReadUpdateDetailController[
        CustomPydanticFastSerializer,
        Participacion,
        ParticipacionGet,
        ParticipacionPut,
        ParticipacionPatch,
    ],
):
    update_operation: ClassVar[type[UpdateOperation]] = ForeignKeyUpdateOperation


class ParticipacionListController(
    ModelListController[
        CustomPydanticFastSerializer,
        Participacion,
        ParticipacionFilterSet,
        ParticipacionFilterQuery,
        ParticipacionGet,
        ParticipacionPost,
        Paginated[ParticipacionGet],
    ],
):
    create_operation: ClassVar[type[CreateOperation]] = ParticipacionCreateOperation


class ValidarParticipacionController(
    ModelController[CustomPydanticFastSerializer, Participacion, ParticipacionGet],
):
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = ADMIN_PERMISSIONS

    @modify(status_code=HTTPStatus.OK)
    async def post(
        self,
        parsed_body: Body[ParticipacionValidarPost],
    ) -> ParticipacionGet:
        # the points are `trg_participacion_otorgar_puntos`' job
        participacion: Participacion = await ejecutar(
            transicionar,
            actor=ActorTypes.ADMIN,
            campo="desenlace",
            codigo=parsed_body.desenlace,
            entidad="participacion",
            pk=parsed_body.participacion_id,
            qs=self.qs,
            validada_at=now(),
            validada_por_id=self.request.user.pk,
        )

        return self.mapper(participacion, self.schema)


class AnularParticipacionController(
    ModelController[CustomPydanticFastSerializer, Participacion, ParticipacionGet],
):
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = ADMIN_PERMISSIONS

    @modify(status_code=HTTPStatus.OK)
    async def post(
        self,
        parsed_body: Body[ParticipacionAnularPost],
    ) -> ParticipacionGet:
        # reverting points and annulling certificates are the triggers' job
        participacion: Participacion = await ejecutar(
            transicionar,
            actor=ActorTypes.ADMIN,
            anulada_at=now(),
            codigo="anulada",
            entidad="participacion",
            motivo_descripcion=parsed_body.motivo_descripcion,
            motivo_id=parsed_body.motivo_id,
            pk=parsed_body.participacion_id,
            qs=self.qs,
        )

        return self.mapper(participacion, self.schema)


class ReconocimientoDetailController(
    ScopedDetailController[
        CustomPydanticFastSerializer,
        Reconocimiento,
        ReconocimientoGet,
        ReconocimientoPut,
        ReconocimientoPatch,
        build_scoped_path(Reconocimiento, "participacion"),  # ty: ignore[invalid-type-form]
    ],
):
    parent_field: ClassVar[str] = "participacion"


class ReconocimientoListController(
    ScopedListController[
        CustomPydanticFastSerializer,
        Reconocimiento,
        ReconocimientoFilterSet,
        ReconocimientoFilterQuery,
        ReconocimientoGet,
        ReconocimientoPost,
        Paginated[ReconocimientoGet],
    ],
):
    parent_field: ClassVar[str] = "participacion"


########################################################################################
# equipos


class EquipoDetailController(
    OpenReadMixin,
    ModelReadUpdateDetailController[
        CustomPydanticFastSerializer,
        Equipo,
        EquipoGet,
        EquipoPut,
        EquipoPatch,
    ],
):
    pass


class EquipoListController(
    OpenReadMixin,
    ModelListController[
        CustomPydanticFastSerializer,
        Equipo,
        EquipoFilterSet,
        EquipoFilterQuery,
        EquipoGet,
        EquipoPost,
        Paginated[EquipoGet],
    ],
):
    # participants found their own teams (RF-P-20); the founder joins as leader
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = (
        OpenReadMixin.permissions | OPEN_PERMISSIONS
    )

    async def post(self, parsed_body: Body[EquipoPost]) -> EquipoGet:
        equipo: Equipo = await ejecutar(
            crear_equipo,
            actividad_id=parsed_body.actividad,
            cuenta=self.request.user,
            nombre=parsed_body.nombre,
            qs=self.qs,
        )

        return self.mapper(equipo, self.schema)


class EquipoListAllController(
    OpenReadMixin,
    ModelListAllController[
        CustomPydanticFastSerializer,
        Equipo,
        EquipoFilterSet,
        EquipoFilterAllQuery,
        EquipoGet,
        list[EquipoGet],
    ],
):
    pass


class UnirmeEquipoController(
    ModelController[CustomPydanticFastSerializer, Equipo, EquipoGet],
):
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = OPEN_PERMISSIONS

    @modify(status_code=HTTPStatus.OK)
    async def post(self, parsed_body: Body[UnirmeEquipoPost]) -> EquipoGet:
        equipo: Equipo = await ejecutar(
            unirse_a_equipo,
            codigo_union=parsed_body.codigo_union,
            cuenta=self.request.user,
            qs=self.qs,
        )

        return self.mapper(equipo, self.schema)


class EquipoMiembroDetailController(
    OpenReadMixin,
    ScopedDetailController[
        CustomPydanticFastSerializer,
        EquipoMiembro,
        EquipoMiembroGet,
        EquipoMiembroPut,
        EquipoMiembroPatch,
        build_scoped_path(EquipoMiembro, "equipo"),  # ty: ignore[invalid-type-form]
    ],
):
    parent_field: ClassVar[str] = "equipo"


class EquipoMiembroListController(
    OpenReadMixin,
    ScopedListController[
        CustomPydanticFastSerializer,
        EquipoMiembro,
        EquipoMiembroFilterSet,
        EquipoMiembroFilterQuery,
        EquipoMiembroGet,
        EquipoMiembroPost,
        Paginated[EquipoMiembroGet],
    ],
):
    parent_field: ClassVar[str] = "equipo"


########################################################################################
# asignación de mentores


class AsignacionMentorDetailController(
    OpenReadMixin,
    ModelReadUpdateDetailController[
        CustomPydanticFastSerializer,
        AsignacionMentor,
        AsignacionMentorGet,
        AsignacionMentorPut,
        AsignacionMentorPatch,
    ],
):
    pass


class AsignacionMentorListController(
    OpenReadMixin,
    ModelListController[
        CustomPydanticFastSerializer,
        AsignacionMentor,
        AsignacionMentorFilterSet,
        AsignacionMentorFilterQuery,
        AsignacionMentorGet,
        AsignacionMentorPost,
        Paginated[AsignacionMentorGet],
    ],
):
    create_operation: ClassVar[type[CreateOperation]] = AsignacionMentorCreateOperation


class AsignacionAccionController(
    ModelController[
        CustomPydanticFastSerializer,
        AsignacionMentor,
        AsignacionMentorGet,
    ],
):
    permissions: ClassVar[dict[HTTPMethod, Sequence[str]]] = OPEN_PERMISSIONS

    async def responder(
        self,
        body: AsignacionAccionPost,
        codigo: str,
        **cambios: object,
    ) -> AsignacionMentorGet:
        asignacion: AsignacionMentor = await ejecutar(
            responder_mentoria,
            asignacion_id=body.asignacion_id,
            codigo=codigo,
            cuenta=self.request.user,
            qs=self.qs,
            **cambios,
        )

        return self.mapper(asignacion, self.schema)


class AceptarMentoriaController(AsignacionAccionController):
    @modify(status_code=HTTPStatus.OK)
    async def post(
        self,
        parsed_body: Body[AsignacionAccionPost],
    ) -> AsignacionMentorGet:
        return await self.responder(parsed_body, "confirmada")


class FinalizarMentoriaController(AsignacionAccionController):
    @modify(status_code=HTTPStatus.OK)
    async def post(
        self,
        parsed_body: Body[AsignacionAccionPost],
    ) -> AsignacionMentorGet:
        return await self.responder(parsed_body, "finalizada")


class DeclinarMentoriaController(AsignacionAccionController):
    @modify(status_code=HTTPStatus.OK)
    async def post(
        self,
        parsed_body: Body[AsignacionCierrePost],
    ) -> AsignacionMentorGet:
        return await self.responder(
            parsed_body,
            "declinada",
            motivo_descripcion=parsed_body.motivo_descripcion,
            motivo_id=parsed_body.motivo_id,
        )


class CancelarMentoriaController(AsignacionAccionController):
    @modify(status_code=HTTPStatus.OK)
    async def post(
        self,
        parsed_body: Body[AsignacionCierrePost],
    ) -> AsignacionMentorGet:
        return await self.responder(
            parsed_body,
            "cancelada",
            motivo_descripcion=parsed_body.motivo_descripcion,
            motivo_id=parsed_body.motivo_id,
        )


########################################################################################

__all__ = (
    "AceptarMentoriaController",
    "AnularParticipacionController",
    "AsignacionMentorDetailController",
    "AsignacionMentorListController",
    "CancelarInscripcionController",
    "CancelarMentoriaController",
    "ConfirmarInscripcionController",
    "DeclinarMentoriaController",
    "EquipoDetailController",
    "EquipoListAllController",
    "EquipoListController",
    "EquipoMiembroDetailController",
    "EquipoMiembroListController",
    "FinalizarMentoriaController",
    "InscribirmeController",
    "InscripcionDetailController",
    "InscripcionListController",
    "ParticipacionDetailController",
    "ParticipacionListController",
    "RechazarInscripcionController",
    "ReconocimientoDetailController",
    "ReconocimientoListController",
    "UnirmeEquipoController",
    "ValidarParticipacionController",
)
