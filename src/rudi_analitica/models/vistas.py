from typing import TYPE_CHECKING, override

from django.db.models import (
    DO_NOTHING,
    CharField,
    ForeignKey,
    IntegerField,
    Model,
    OneToOneField,
    PositiveSmallIntegerField,
)

from rudi_actividades.models import Actividad
from rudi_auth.models import RudiUser
from rudi_profiles.models import Carrera

if TYPE_CHECKING:
    from typing import ClassVar

    from django.db.models import Manager

########################################################################################

# read-only models over the materialized views created by
# `rudi_analitica/migrations/0002_vistas.py`; `refrescar_vistas` rebuilds them


class MvParticipanteUnicoAnio(Model):
    anio = PositiveSmallIntegerField(primary_key=True)
    valor = IntegerField()

    objects: ClassVar[Manager]

    class Meta:
        db_table: str = "mv_participante_unico_anio"
        managed: bool = False

    @override
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(anio={self.anio})"


########################################################################################


class MvParticipacionActividad(Model):
    actividad = OneToOneField(
        db_constraint=False,
        on_delete=DO_NOTHING,
        primary_key=True,
        related_name="+",
        to=Actividad,
    )

    anio = PositiveSmallIntegerField()

    inscripciones = IntegerField()
    participaciones = IntegerField()
    validadas = IntegerField()

    objects: ClassVar[Manager]

    class Meta:
        db_table: str = "mv_participacion_actividad"
        managed: bool = False

    @override
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(actividad_id={self.pk})"


########################################################################################


class MvSaldoPuntosUser(Model):
    user = OneToOneField(
        db_constraint=False,
        on_delete=DO_NOTHING,
        primary_key=True,
        related_name="+",
        to=RudiUser,
    )

    saldo = IntegerField()
    automatico = IntegerField()
    manual = IntegerField()

    objects: ClassVar[Manager]

    class Meta:
        db_table: str = "mv_saldo_puntos_user"
        managed: bool = False

    @override
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(user_id={self.pk})"


########################################################################################


class MvCoberturaCarrera(Model):
    # `<anio>:<carrera_id>`, or `<anio>:total` for the row that is not a sum
    clave = CharField(max_length=50, primary_key=True)

    anio = PositiveSmallIntegerField()

    carrera = ForeignKey(
        db_constraint=False,
        null=True,
        on_delete=DO_NOTHING,
        related_name="+",
        to=Carrera,
    )

    estudiantes = IntegerField()
    doble_titulacion = IntegerField()

    objects: ClassVar[Manager]

    class Meta:
        db_table: str = "mv_cobertura_carrera"
        managed: bool = False

    @override
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(clave={self.clave})"
