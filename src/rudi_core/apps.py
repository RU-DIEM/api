from typing import override

from django.apps import AppConfig
from django.db.models import JSONField

from .json import JsonTypeof

########################################################################################


class RudiCore(AppConfig):
    name = "rudi_core"
    label = "rudicore"

    @override
    def ready(self) -> None:
        JSONField.register_lookup(JsonTypeof)
