from typing import TYPE_CHECKING, override

from django.core.management.base import BaseCommand
from pglock import Skip, advisory

from rudi_analitica.services import cerrar_periodo

if TYPE_CHECKING:
    from argparse import ArgumentParser

########################################################################################


class Command(BaseCommand):
    help = "Congela los indicadores de un año terminado (RF-A-45)."

    @override
    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("anio", type=int)

    @advisory(lock_id="rudi_analitica.cerrar", side_effect=Skip, timeout=0)
    @override
    def handle(self, *args: str, **options: int) -> None:
        indicadores: list = cerrar_periodo(anio=options["anio"], cerrado_por=None)

        self.stdout.write(
            msg=f"Se congelaron {len(indicadores)} indicadores de {options['anio']}.",
        )
