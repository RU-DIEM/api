from django.db.models import BooleanField

from api_utils.db import track_table

from .base import RudiSourceAwareEstado

########################################################################################


@track_table()
class EstadoConsentimiento(RudiSourceAwareEstado):
    allow_reporte = BooleanField(db_default=False, default=False)
    allow_comunicacion = BooleanField(db_default=False, default=False)
