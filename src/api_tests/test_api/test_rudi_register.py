from http import HTTPStatus

import pytest

from dmr.test import DMRClient

from api_auth.enums import ApiUserTypes
from api_auth.models import ApiUser
from api_tests.conftest import PASSWORD
from api_tests.helpers import PatchedHttpResponse, assert_field_error, route
from rudi_auth.models import ConsentimientoDatos, RudiUser
from rudi_estados.models import EstadoRudiUser

########################################################################################

# rudi's counterparts of the template's registration tests, which `src/conftest.py`
# deselects because `/auth/register/` now takes rudi's body

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures(
        "seeded_groups",
        "estado_inicial",
        "estado_activo",
        "consentimiento_inicial",
        "politica_vigente",
        "sent_plantillas",
    ),
]

TELEFONO: str = "+505 8123 4567"

########################################################################################


def registration_body(**overrides: str | bool) -> dict:
    return {
        "acepta_politica": True,
        "email": "registrado@pruebas.example.com",
        "first_name": "Nuevo",
        "last_name": "Usuario",
        "password1": PASSWORD,
        "password2": PASSWORD,
        "telefono": TELEFONO,
        "username": "registrado",
    } | overrides


def register(dmr_client: DMRClient, **overrides: str | bool) -> PatchedHttpResponse:
    return dmr_client.post(route("auth-register"), data=registration_body(**overrides))


########################################################################################


def test_register_lives_at_the_templates_path() -> None:
    assert route("auth-register") == "/auth/register/"


def test_register_is_public_and_creates_the_persona(
    dmr_client: DMRClient,
    estado_inicial: EstadoRudiUser,
) -> None:
    response: PatchedHttpResponse = register(dmr_client)

    assert response.status_code == HTTPStatus.CREATED

    payload: dict = response.json()

    assert payload["user"]["username"] == "registrado"
    assert payload["user"]["email"] == "registrado@pruebas.example.com"
    assert payload["estado"]["id"] == str(estado_inicial.pk)
    assert payload["telefono"] == TELEFONO

    persona: RudiUser = RudiUser.objects.select_related("user").get(
        user__username="registrado",
    )

    # same client group the template's registration assigns
    assert [group.name for group in persona.user.groups.all()] == [  # ty: ignore[unresolved-attribute]
        ApiUserTypes.CLIENT.value,
    ]

    assert ConsentimientoDatos.objects.filter(user=persona).exists()


def test_register_hashes_the_password(
    dmr_client: DMRClient,
) -> None:
    register(dmr_client)

    user: ApiUser = ApiUser.objects.get(username="registrado")

    assert user.password != PASSWORD
    assert user.check_password(PASSWORD)


def test_register_never_echoes_the_password(
    dmr_client: DMRClient,
) -> None:
    response: PatchedHttpResponse = register(dmr_client)

    assert PASSWORD not in response.content.decode()


def test_register_rejects_mismatched_passwords(
    dmr_client: DMRClient,
) -> None:
    response: PatchedHttpResponse = register(dmr_client, password2="Otra-Contrasena-99")

    assert response.status_code == HTTPStatus.BAD_REQUEST

    assert (
        assert_field_error(response, "body.password1")
        == "Las contraseñas ingresadas no son iguales."
    )

    assert_field_error(response, "body.password2")


def test_register_rejects_weak_passwords(
    dmr_client: DMRClient,
) -> None:
    response: PatchedHttpResponse = register(
        dmr_client,
        password1="12345678",
        password2="12345678",
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST

    message: str = assert_field_error(response, "body.password1")

    assert message.endswith(".")
    assert message[0].isupper()


def test_register_rejects_duplicate_usernames(
    dmr_client: DMRClient,
    client_user: ApiUser,
) -> None:
    response: PatchedHttpResponse = register(
        dmr_client,
        username=client_user.username,  # ty: ignore[invalid-argument-type]
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert assert_field_error(response, "body.username")


def test_register_rejects_the_email_of_a_pending_persona(
    dmr_client: DMRClient,
) -> None:
    # pending personas are inactive, which the template's partial unique
    # indexes ignore; rudi still has to treat their address as taken
    register(dmr_client)

    response: PatchedHttpResponse = register(dmr_client, username="otro")

    assert response.status_code == HTTPStatus.CONFLICT
    assert assert_field_error(response, "body.email")


def test_register_rejects_invalid_email(
    dmr_client: DMRClient,
) -> None:
    response: PatchedHttpResponse = register(dmr_client, email="no-es-un-correo")

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert assert_field_error(response, "body.email")


def test_register_requires_accepting_the_policy(
    dmr_client: DMRClient,
) -> None:
    response: PatchedHttpResponse = register(dmr_client, acepta_politica=False)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert assert_field_error(response, "body.acepta_politica")


def test_register_normalizes_the_username(
    dmr_client: DMRClient,
) -> None:
    register(dmr_client, username="  eco  ")

    assert ApiUser.objects.filter(username="eco").exists()


def test_registration_waits_for_the_confirmed_address(
    dmr_client: DMRClient,
    sent_plantillas: list[dict],
) -> None:
    credentials: dict[str, str] = {"username": "registrado", "password": PASSWORD}

    assert register(dmr_client).status_code == HTTPStatus.CREATED
    assert len(sent_plantillas) == 1
    assert sent_plantillas[0]["codigo"] == "verificacion_email"

    before: PatchedHttpResponse = dmr_client.post(
        route("auth-mobile-login"),
        data=credentials,
    )

    assert before.status_code == HTTPStatus.UNAUTHORIZED

    confirm: PatchedHttpResponse = dmr_client.post(
        route("auth-email-confirm"),
        data={"token": sent_plantillas[0]["context"]["token"]},
    )

    assert confirm.status_code == HTTPStatus.NO_CONTENT

    after: PatchedHttpResponse = dmr_client.post(
        route("auth-mobile-login"),
        data=credentials,
    )

    assert after.status_code == HTTPStatus.OK
