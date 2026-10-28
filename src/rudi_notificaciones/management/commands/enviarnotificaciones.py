from typing import override

from django.core.management.base import BaseCommand
from pglock import Skip, advisory

from rudi_notificaciones.services import enviar_pendientes

########################################################################################


class Command(BaseCommand):
    @advisory(lock_id="rudi_notificaciones.enviar", side_effect=Skip, timeout=0)
    @override
    def handle(self, *args: str, **options: str) -> None:
        enviadas: int = enviar_pendientes()

        self.stdout.write(msg=f"Se enviaron {enviadas} notificaciones.")
