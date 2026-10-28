from typing import override

from django.core.management.base import BaseCommand
from django.utils.timezone import localdate
from pglock import Skip, advisory

from rudi_actividades.services import transicionar_actividades

########################################################################################


class Command(BaseCommand):
    @advisory(lock_id="rudi_actividades.transicionar", side_effect=Skip, timeout=0)
    @override
    def handle(self, *args: str, **options: str) -> None:
        movidas: int = transicionar_actividades(localdate())

        self.stdout.write(msg=f"Se movieron {movidas} actividades.")
