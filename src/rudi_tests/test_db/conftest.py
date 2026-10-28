from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date

import pytest

from django.db import DatabaseError, connection, transaction
from django.utils.timezone import now

from api_auth.models import ApiUser
from rudi_actividades.models import Actividad, ActividadResponsable
from rudi_auth.models import RudiUser
from rudi_catalogos.models import (
    Motivo,
    RolParticipacion,
    TipoActividad,
    TipoReconocimiento,
)
from rudi_estados.enums import InputSourceTypes
from rudi_estados.models import (
    EstadoActividad,
    EstadoAsignacionMentor,
    EstadoConstancia,
    EstadoInscripcion,
    EstadoParticipacion,
    EstadoPropuesta,
    EstadoRudiUser,
)
from rudi_participacion.models import Inscripcion, Participacion

########################################################################################


@contextmanager
def rejected(fragment: str = "") -> Generator[None]:
    """
    Expect the database to refuse the write, inside its own savepoint.
    """

    with pytest.raises(DatabaseError) as raised, transaction.atomic():
        yield

    assert fragment in str(raised.value)


def immediate() -> None:
    # deferred triggers and foreign keys otherwise wait for a commit that a test
    # transaction never reaches
    with connection.cursor() as cursor:
        cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")


########################################################################################


@dataclass
class Estados:
    borrador: EstadoActividad
    publicada: EstadoActividad
    cancelada: EstadoActividad

    confirmada: EstadoInscripcion
    pendiente: EstadoInscripcion
    en_espera: EstadoInscripcion
    inscripcion_cerrada: EstadoInscripcion

    registrada: EstadoParticipacion
    validada: EstadoParticipacion
    anulada: EstadoParticipacion

    emitida: EstadoConstancia
    constancia_anulada: EstadoConstancia

    propuesta_activa: EstadoPropuesta
    propuesta_cerrada: EstadoPropuesta

    mentoria_propuesta: EstadoAsignacionMentor
    mentoria_declinada: EstadoAsignacionMentor


def seeded() -> Estados:
    # the structural seeders (`rudi_estados/seeders.py`) run after `migrate`
    return Estados(
        anulada=EstadoParticipacion.objects.get(codigo="anulada"),
        borrador=EstadoActividad.objects.get(codigo="borrador"),
        cancelada=EstadoActividad.objects.get(codigo="cancelada"),
        confirmada=EstadoInscripcion.objects.get(codigo="confirmada"),
        constancia_anulada=EstadoConstancia.objects.get(codigo="anulada"),
        emitida=EstadoConstancia.objects.get(codigo="emitida"),
        en_espera=EstadoInscripcion.objects.get(codigo="en_espera"),
        inscripcion_cerrada=EstadoInscripcion.objects.get(codigo="cancelada"),
        mentoria_declinada=EstadoAsignacionMentor.objects.get(codigo="declinada"),
        mentoria_propuesta=EstadoAsignacionMentor.objects.get(codigo="propuesta"),
        pendiente=EstadoInscripcion.objects.get(codigo="pendiente"),
        propuesta_activa=EstadoPropuesta.objects.get(codigo="activa"),
        propuesta_cerrada=EstadoPropuesta.objects.get(codigo="cerrada"),
        publicada=EstadoActividad.objects.get(codigo="publicada"),
        registrada=EstadoParticipacion.objects.get(codigo="registrada"),
        validada=EstadoParticipacion.objects.get(codigo="finalizada"),
    )


########################################################################################


@dataclass
class Mundo:
    """
    A small, consistent domain to run the triggers against.

    States with their transitions, one entry per catalog, an admin account,
    and factories for everything else.
    """

    estados: Estados

    tipo: TipoActividad
    rol: RolParticipacion
    premio: TipoReconocimiento

    admin: ApiUser

    @staticmethod
    def persona(username: str) -> RudiUser:
        cuenta: ApiUser = ApiUser.objects.create_user(
            email=f"{username}@unit.example.com",
            password="x",
            username=username,
        )

        return RudiUser.objects.create(
            estado=EstadoRudiUser.objects.get(codigo="activa"),
            origen=InputSourceTypes.SELF,
            user=cuenta,
        )

    @staticmethod
    def motivo(ambito: str, *, require_descripcion: bool = False) -> Motivo:
        return Motivo.objects.create(
            ambito=ambito,
            codigo=f"motivo_{Motivo.objects.count()}",
            etiqueta="Motivo",
            require_descripcion=require_descripcion,
        )

    def actividad(
        self,
        *,
        publicar: bool = True,
        sin_responsable: bool = False,
        **fields: object,
    ) -> Actividad:
        fields = {
            "anio": 2026,
            "estado": self.estados.borrador,
            "fecha_inicio": date(2026, 3, 1),
            "nombre": f"Actividad {Actividad.objects.count()}",
            "tipo_actividad": self.tipo,
            **fields,
        }

        actividad: Actividad = Actividad.objects.create(**fields)

        if not sin_responsable:
            ActividadResponsable.objects.create(
                actividad=actividad,
                rol="coordinacion",
                user=self.persona(f"responsable_{actividad.pk.hex[-8:]}"),
            )

        if publicar:
            Actividad.objects.filter(pk=actividad.pk).update(
                estado=self.estados.publicada,
            )

        return Actividad.objects.get(pk=actividad.pk)

    def inscripcion(
        self,
        actividad: Actividad,
        persona: RudiUser,
        **fields: object,
    ) -> Inscripcion:
        fields = {
            "estado": self.estados.confirmada,
            "origen": InputSourceTypes.SELF,
            **fields,
        }

        return Inscripcion.objects.create(actividad=actividad, user=persona, **fields)

    def participacion(
        self,
        actividad: Actividad,
        persona: RudiUser,
        **fields: object,
    ) -> Participacion:
        fields = {
            "anio": actividad.anio,
            "estado": self.estados.registrada,
            "rol": self.rol,
            **fields,
        }

        return Participacion.objects.create(
            actividad=actividad,
            user=persona,
            **fields,
        )

    def validar(self, participacion: Participacion) -> None:
        Participacion.objects.filter(pk=participacion.pk).update(
            estado=self.estados.validada,
            validada_at=now(),
            validada_por=self.admin,
        )


@pytest.fixture
def mundo(db: None) -> Mundo:
    return Mundo(
        admin=ApiUser.objects.create_user(
            email="admin@unit.example.com",
            password="x",
            username="admin",
        ),
        estados=seeded(),
        premio=TipoReconocimiento.objects.create(codigo="premio", etiqueta="Premio"),
        rol=RolParticipacion.objects.create(codigo="participante", etiqueta="Rol"),
        tipo=TipoActividad.objects.create(codigo="hackathon", etiqueta="Hackathon"),
    )
