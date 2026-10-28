from typing import override

from django.apps import AppConfig

########################################################################################


class RudiEstados(AppConfig):
    name = "rudi_estados"
    label = "rudiestados"

    @override
    def ready(self) -> None:
        import rudi_estados.seeders  # ruff: ignore[import-outside-top-level, unused-import]
