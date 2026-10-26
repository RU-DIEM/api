from typing import override

from django.apps import AppConfig

########################################################################################


class RudiAuth(AppConfig):
    name = "rudi_auth"
    label = "rudiauth"

    @override
    def ready(self) -> None:
        import rudi_auth.seeders  # ruff: ignore[import-outside-top-level, unused-import]
