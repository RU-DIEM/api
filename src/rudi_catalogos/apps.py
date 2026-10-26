from typing import override

from django.apps import AppConfig

########################################################################################


class RudiCatalogos(AppConfig):
    name = "rudi_catalogos"
    label = "rudicatalogos"

    @override
    def ready(self) -> None:
        import rudi_catalogos.seeders  # ruff: ignore[import-outside-top-level, unused-import]
