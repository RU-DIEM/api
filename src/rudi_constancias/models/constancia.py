from typing import TYPE_CHECKING

from django.conf import settings
from django.db.models import (
    RESTRICT,
    CharField,
    CheckConstraint,
    DateTimeField,
    F,
    ForeignKey,
    Index,
    JSONField,
    PositiveSmallIntegerField,
    Q,
    TextField,
    URLField,
    UniqueConstraint,
)
from django.db.models.functions import Now
from django.utils.timezone import now
from pgtrigger import ReadOnly

from api_core.models.base import ApiAppendOnlyModel, ApiProtectedModel
from api_utils.db import track_table
from rudi_auth.models import RudiUser
from rudi_catalogos.models import Motivo
from rudi_estados.models import EstadoConstancia
from rudi_participacion.models import Participacion

from .plantilla import PlantillaConstancia

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pgtrigger import Trigger

########################################################################################


@track_table()
class Constancia(ApiProtectedModel):
    # assigned by `trg_constancia_folio_asignar`, whatever the caller sends
    folio = CharField(db_default="", default="", max_length=30)

    user = ForeignKey(
        on_delete=RESTRICT,
        related_name="constancias",
        to=RudiUser,
    )

    plantilla = ForeignKey(
        on_delete=RESTRICT,
        related_name="constancias",
        to=PlantillaConstancia,
    )

    estado = ForeignKey(
        on_delete=RESTRICT,
        related_name="constancias",
        to=EstadoConstancia,
    )

    codigo_verificacion = CharField(max_length=12)

    nombre_congelado = CharField(max_length=201)
    identificador_congelado = CharField(db_default="", default="", max_length=20)
    contenido_congelado = JSONField()
    texto_congelado = TextField()

    emitida_at = DateTimeField(db_default=Now(), default=now)
    emitida_por = ForeignKey(
        on_delete=RESTRICT,
        related_name="constancias_emitidas",
        to=settings.AUTH_USER_MODEL,
    )
    solicitada_at = DateTimeField(null=True)

    anulada_at = DateTimeField(null=True)

    motivo = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="constancias",
        to=Motivo,
    )
    motivo_descripcion = TextField(db_default="", default="")

    reemplaza_a = ForeignKey(
        null=True,
        on_delete=RESTRICT,
        related_name="+",
        to="self",
    )

    documento_url = URLField(db_default="", default="", max_length=500)

    class Meta(ApiProtectedModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(folio__regex=r"^DIEM-[0-9]{4}-[0-9]{6}$"),
                name="chk_%(class)s_folio_format",
            ),
            CheckConstraint(
                condition=Q(codigo_verificacion__regex=r"^[A-Z0-9]{8,12}$"),
                name="chk_%(class)s_verificacion_format",
            ),
            CheckConstraint(
                condition=(
                    Q(anulada_at__isnull=True, motivo__isnull=True)
                    | Q(anulada_at__isnull=False, motivo__isnull=False)
                ),
                name="chk_%(class)s_anulacion",
            ),
            CheckConstraint(
                condition=Q(reemplaza_a__isnull=True) | ~Q(reemplaza_a=F("id")),
                name="chk_%(class)s_no_autoreemplazo",
            ),
            CheckConstraint(
                condition=Q(contenido_congelado__typeof="object"),
                name="chk_%(class)s_contenido",
            ),
            UniqueConstraint(fields=["folio"], name="unq_%(class)s_folio"),
            UniqueConstraint(
                fields=["codigo_verificacion"],
                name="unq_%(class)s_verificacion",
            ),
            UniqueConstraint(
                condition=Q(reemplaza_a__isnull=False),
                fields=["reemplaza_a"],
                name="unq_%(class)s_reemplazo",
            ),
        )

        indexes: Sequence[Index] = (
            *ApiProtectedModel.Meta.indexes,
            Index(
                F("user"),
                F("emitida_at").desc(),
                name="idx_%(class)s_user",
            ),
        )

        # what a certificate says is frozen the moment it is issued (D-16)
        triggers: Sequence[Trigger] = (
            *ApiProtectedModel.Meta.triggers,
            ReadOnly(
                fields=[
                    "codigo_verificacion",
                    "contenido_congelado",
                    "emitida_at",
                    "emitida_por",
                    "folio",
                    "identificador_congelado",
                    "nombre_congelado",
                    "plantilla",
                    "texto_congelado",
                    "user",
                ],
                name="trg_readonly_snapshot",
            ),
        )


########################################################################################


class ConstanciaParticipacion(ApiAppendOnlyModel):
    constancia = ForeignKey(
        on_delete=RESTRICT,
        related_name="participaciones",
        to=Constancia,
    )

    participacion = ForeignKey(
        on_delete=RESTRICT,
        related_name="constancias",
        to=Participacion,
    )

    orden = PositiveSmallIntegerField()

    class Meta(ApiAppendOnlyModel.Meta):  # ty: ignore[invalid-attribute-override]
        constraints: Sequence[UniqueConstraint] = (
            UniqueConstraint(
                fields=["constancia", "participacion"],
                name="unq_%(class)s_par",
            ),
            UniqueConstraint(
                fields=["constancia", "orden"],
                name="unq_%(class)s_orden",
            ),
        )
