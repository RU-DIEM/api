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
from rudi_estados.enums import ActorTypes, InputSourceTypes
from rudi_estados.models import (
    EstadoActividad,
    EstadoAsignacionMentor,
    EstadoConstancia,
    EstadoInscripcion,
    EstadoParticipacion,
    EstadoPropuesta,
    EstadoRudiUser,
    TransicionEstadoActividad,
    TransicionEstadoInscripcion,
    TransicionEstadoParticipacion,
    TransicionEstadoPropuesta,
)
from rudi_estados.models.base import RudiTransicion
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


def transicion(
    model: type[RudiTransicion],
    desde: object,
    hasta: object,
    *actores: ActorTypes,
) -> None:
    for actor in actores or (ActorTypes.ADMIN,):
        model.objects.create(actor=actor, from_estado=desde, to_estado=hasta)


########################################################################################


@dataclass
class Estados:
    borrador: EstadoActividad
    publicada: EstadoActividad
    cancelada: EstadoActividad

    confirmada: EstadoInscripcion
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


def estados_actividad() -> dict:
    borrador = EstadoActividad.objects.create(
        codigo="borrador",
        etiqueta="Borrador",
        initial=True,
    )
    publicada = EstadoActividad.objects.create(
        allow_inscripcion=True,
        allow_validacion=True,
        codigo="publicada",
        etiqueta="Publicada",
        public=True,
    )
    cancelada = EstadoActividad.objects.create(
        codigo="cancelada",
        etiqueta="Cancelada",
        terminal=True,
    )

    transicion(TransicionEstadoActividad, borrador, publicada)
    transicion(TransicionEstadoActividad, publicada, cancelada)

    return {"borrador": borrador, "cancelada": cancelada, "publicada": publicada}


def estados_inscripcion() -> dict:
    confirmada = EstadoInscripcion.objects.create(
        allow_participacion=True,
        codigo="confirmada",
        consume_cupo=True,
        etiqueta="Confirmada",
        initial=True,
        source=InputSourceTypes.SELF,
    )
    en_espera = EstadoInscripcion.objects.create(
        codigo="en_espera",
        etiqueta="En espera",
    )
    cerrada = EstadoInscripcion.objects.create(
        codigo="cancelada",
        etiqueta="Cancelada",
        terminal=True,
    )

    sistema, persona = ActorTypes.SYS, ActorTypes.USER

    transicion(TransicionEstadoInscripcion, en_espera, confirmada, sistema)
    transicion(TransicionEstadoInscripcion, confirmada, cerrada, sistema, persona)
    transicion(TransicionEstadoInscripcion, en_espera, cerrada, sistema)

    return {
        "confirmada": confirmada,
        "en_espera": en_espera,
        "inscripcion_cerrada": cerrada,
    }


def estados_participacion() -> dict:
    registrada = EstadoParticipacion.objects.create(
        codigo="registrada",
        etiqueta="Registrada",
        initial=True,
    )
    validada = EstadoParticipacion.objects.create(
        allow_constancia=True,
        allow_puntos=True,
        codigo="finalizada",
        efectiva=True,
        etiqueta="Finalizada",
    )
    anulada = EstadoParticipacion.objects.create(
        codigo="anulada",
        etiqueta="Anulada",
        terminal=True,
    )

    transicion(TransicionEstadoParticipacion, registrada, validada)
    transicion(TransicionEstadoParticipacion, validada, anulada)

    return {"anulada": anulada, "registrada": registrada, "validada": validada}


def estados_resto() -> dict:
    activa = EstadoPropuesta.objects.create(
        allow_portafolio=True,
        codigo="activa",
        etiqueta="Activa",
        initial=True,
        vigente=True,
    )
    cerrada = EstadoPropuesta.objects.create(
        codigo="cerrada",
        etiqueta="Cerrada",
        terminal=True,
    )

    transicion(TransicionEstadoPropuesta, activa, cerrada)

    return {
        "constancia_anulada": EstadoConstancia.objects.create(
            codigo="anulada",
            etiqueta="Anulada",
            require_motivo=True,
            terminal=True,
        ),
        "emitida": EstadoConstancia.objects.create(
            codigo="emitida",
            etiqueta="Emitida",
            initial=True,
            valid=True,
        ),
        "mentoria_declinada": EstadoAsignacionMentor.objects.create(
            codigo="declinada",
            etiqueta="Declinada",
            require_motivo=True,
            terminal=True,
        ),
        "mentoria_propuesta": EstadoAsignacionMentor.objects.create(
            codigo="propuesta",
            etiqueta="Propuesta",
            initial=True,
        ),
        "propuesta_activa": activa,
        "propuesta_cerrada": cerrada,
    }


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
    EstadoRudiUser.objects.create(codigo="activa", etiqueta="Activa", initial=True)

    return Mundo(
        admin=ApiUser.objects.create_user(
            email="admin@unit.example.com",
            password="x",
            username="admin",
        ),
        estados=Estados(
            **estados_actividad(),
            **estados_inscripcion(),
            **estados_participacion(),
            **estados_resto(),
        ),
        premio=TipoReconocimiento.objects.create(codigo="premio", etiqueta="Premio"),
        rol=RolParticipacion.objects.create(codigo="participante", etiqueta="Rol"),
        tipo=TipoActividad.objects.create(codigo="hackathon", etiqueta="Hackathon"),
    )
