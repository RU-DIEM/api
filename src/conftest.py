from datetime import date, timedelta
from typing import TYPE_CHECKING, Final

import pytest

from rudi_auth.models import PoliticaPrivacidad
from rudi_estados.enums import InputSourceTypes
from rudi_estados.models import EstadoConsentimiento, EstadoRudiUser

if TYPE_CHECKING:
    from collections.abc import Mapping

########################################################################################

# template tests whose endpoint rudi took over with a different contract. Each
# one has a rudi counterpart covering the same behavior, named in the reason.
# Deselecting here, instead of editing the template's test files, keeps factory
# merges free of conflicts in `api_tests`.

REPLACED_TEMPLATE_TESTS: Final[Mapping[str, str]] = dict.fromkeys(
    (
        "test_api/test_accounts.py::test_register_is_public",
        "test_api/test_accounts.py::test_register_hashes_the_password",
        "test_api/test_accounts.py::test_register_never_echoes_the_password",
        "test_api/test_accounts.py::test_register_rejects_mismatched_passwords",
        "test_api/test_accounts.py::test_register_rejects_weak_passwords",
        "test_api/test_accounts.py::test_register_rejects_duplicate_usernames",
        "test_api/test_accounts.py::test_register_rejects_invalid_email",
        "test_api/test_accounts.py::test_register_rejects_a_non_client_group",
        "test_api/test_accounts.py::test_register_normalizes_the_username",
        "test_api/test_email.py::test_registration_waits_for_the_confirmed_address",
    ),
    "/auth/register/ is rudi's registration; see test_api/test_rudi_register.py",
)

########################################################################################


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    replaced: list[pytest.Item] = [
        item
        for item in items
        if item.nodeid.removeprefix("src/api_tests/") in REPLACED_TEMPLATE_TESTS
    ]

    if not replaced:
        return

    config.hook.pytest_deselected(items=replaced)

    items[:] = [item for item in items if item not in replaced]


########################################################################################

# rudi's domain fixtures. The template's own fixtures live in `api_tests/conftest.py`.


@pytest.fixture
def sent_plantillas(monkeypatch: pytest.MonkeyPatch) -> list[dict]:
    # capture rudi's verification mail instead of sending it
    captured: list[dict] = []

    async def fake_send_plantilla(*, codigo: str, context: dict, to: str) -> None:  # ruff: ignore[unused-async]
        captured.append({"codigo": codigo, "context": context, "to": to})

    async def fake_read_duracion(codigo: str) -> timedelta:  # ruff: ignore[unused-async, unused-function-argument]
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


@pytest.fixture
def estado_inicial(db: None) -> EstadoRudiUser:  # ruff: ignore[unused-function-argument]
    return EstadoRudiUser.objects.create(
        codigo="pendiente",
        etiqueta="Pendiente",
        initial=True,
    )


@pytest.fixture
def estado_activo(db: None) -> EstadoRudiUser:  # ruff: ignore[unused-function-argument]
    return EstadoRudiUser.objects.create(
        allow_ingreso=True,
        codigo="activo",
        etiqueta="Activo",
    )


@pytest.fixture
def estado_suspendido(db: None) -> EstadoRudiUser:  # ruff: ignore[unused-function-argument]
    return EstadoRudiUser.objects.create(
        codigo="suspendido",
        etiqueta="Suspendido",
    )


@pytest.fixture
def consentimiento_inicial(db: None) -> EstadoConsentimiento:  # ruff: ignore[unused-function-argument]
    return EstadoConsentimiento.objects.create(
        allow_comunicacion=True,
        allow_reporte=True,
        codigo="otorgado",
        etiqueta="Otorgado",
        initial=True,
        source=InputSourceTypes.SELF,
    )


@pytest.fixture
def politica_vigente(db: None) -> PoliticaPrivacidad:  # ruff: ignore[unused-function-argument]
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
