from typing import override

from django.core.management.base import BaseCommand
from pglock import Skip, advisory

from rudi_participacion.services import vencer_propuestas_mentoria

########################################################################################


class Command(BaseCommand):
    @advisory(lock_id="rudi_participacion.vencer", side_effect=Skip, timeout=0)
    @override
    def handle(self, *args: str, **options: str) -> None:
        vencidas: int = vencer_propuestas_mentoria()

        self.stdout.write(msg=f"Vencieron {vencidas} propuestas de mentoría.")
