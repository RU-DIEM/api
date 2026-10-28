from datetime import date, timedelta

import pytest

# conftest fixtures only reach the tests below them, so rudi's suite pulls in
# the template's (database settings, autouse setup, accounts) explicitly
from api_tests.conftest import *  # ruff: ignore[undefined-local-with-import-star]
from rudi_auth.models import PoliticaPrivacidad
from rudi_estados.enums import InputSourceTypes
from rudi_estados.models import EstadoConsentimiento, EstadoRudiUser

########################################################################################


@pytest.fixture
def sent_plantillas(monkeypatch: pytest.MonkeyPatch) -> list[dict]:
    # capture rudi's verification mail instead of sending it
    captured: list[dict] = []

    async def fake_send_plantilla(*, codigo: str, context: dict, to: str) -> None:  # ruff: ignore[unused-async]
        captured.append({"codigo": codigo, "context": context, "to": to})

    async def fake_read_duracion(codigo: str) -> timedelta:  # ruff: ignore[unused-async]
        return timedelta(hours=2)

    monkeypatch.setattr(
        "rudi_auth.services.verificacion.send_plantilla",
        fake_send_plantilla,
    )

    monkeypatch.setattr(
        "rudi_auth.services.verificacion.read_duracion",
        fake_read_duracion,
    )

    return captured


# the estados are structural seeds (`rudi_estados/seeders.py`), present after `migrate`


@pytest.fixture
def estado_inicial(db: None) -> EstadoRudiUser:
    return EstadoRudiUser.objects.get(codigo="pendiente_verificacion")


@pytest.fixture
def estado_activo(db: None) -> EstadoRudiUser:
    return EstadoRudiUser.objects.get(codigo="verificada")


@pytest.fixture
def estado_suspendido(db: None) -> EstadoRudiUser:
    return EstadoRudiUser.objects.get(codigo="suspendida")


@pytest.fixture
def consentimiento_inicial(db: None) -> EstadoConsentimiento:
    return EstadoConsentimiento.objects.get(source=InputSourceTypes.SELF)


@pytest.fixture
def politica_vigente(db: None) -> PoliticaPrivacidad:
    # the structural seeders already publish one after `migrate`
    vigente: PoliticaPrivacidad | None = PoliticaPrivacidad.objects.filter(
        vigente_hasta__isnull=True,
    ).first()

    return vigente or PoliticaPrivacidad.objects.create(
        texto="Texto de prueba.",
        titulo="Política de prueba",
        version="prueba",
        vigente_desde=date(2026, 1, 1),
    )
