from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest

from asgiref.sync import async_to_sync

from api_auth.enums import VerificationPurposes
from api_auth.models import ApiUser, VerificationCode
from api_tests.conftest import PASSWORD
from api_tests.helpers import PatchedHttpResponse, route
from rudi_auth.models import RudiUser
from rudi_auth.services.verificacion import issue_codigo
from rudi_estados.enums import InputSourceTypes

if TYPE_CHECKING:
    from dmr.test import DMRClient

    from rudi_estados.models import EstadoRudiUser

########################################################################################

pytestmark = pytest.mark.django_db

NEW_PASSWORD: str = "OTRA-CLAVE-456?"

########################################################################################


def make_persona(username: str, estado: EstadoRudiUser) -> RudiUser:
    cuenta: ApiUser = ApiUser.objects.create_user(
        email=f"{username}@unit.example.com",
        is_active=False,
        password=PASSWORD,
        username=username,
    )

    return RudiUser.objects.create(
        estado=estado,
        origen=InputSourceTypes.SELF,
        user=cuenta,
    )


@pytest.fixture
def persona(estado_inicial: EstadoRudiUser, estado_activo: EstadoRudiUser) -> RudiUser:
    return make_persona("persona", estado_inicial)


def email_of(persona: RudiUser) -> str:
    return persona.user.email  # ty: ignore[unresolved-attribute]


def issue(
    dmr_client: DMRClient,
    sent_plantillas: list[dict],
    name: str,
    email: str,
) -> str:
    response: PatchedHttpResponse = dmr_client.post(route(name), data={"email": email})

    assert response.status_code == HTTPStatus.ACCEPTED

    return sent_plantillas[-1]["context"]["token"]


########################################################################################


def test_email_flow_lives_under_auth_email() -> None:
    assert route("auth-email-confirm") == "/auth/email/confirm/"
    assert route("auth-email-resend") == "/auth/email/resend/"


def test_resend_mails_rudis_template_for_a_pending_persona(
    dmr_client: DMRClient,
    persona: RudiUser,
    sent_plantillas: list[dict],
) -> None:
    issue(dmr_client, sent_plantillas, "auth-email-resend", email_of(persona))

    assert len(sent_plantillas) == 1
    assert sent_plantillas[0]["codigo"] == "verificacion_email"
    assert "/verificar?token=" in sent_plantillas[0]["context"]["enlace"]

    code: VerificationCode = VerificationCode.objects.get(api_user=persona.user)

    assert code.purpose == VerificationPurposes.EMAIL


def test_confirm_verifies_the_account_and_activates_the_persona(
    dmr_client: DMRClient,
    estado_activo: EstadoRudiUser,
    persona: RudiUser,
    sent_plantillas: list[dict],
) -> None:
    token = issue(dmr_client, sent_plantillas, "auth-email-resend", email_of(persona))

    response: PatchedHttpResponse = dmr_client.post(
        route("auth-email-confirm"),
        data={"token": token},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    persona.refresh_from_db()
    cuenta: ApiUser = ApiUser.objects.get(pk=persona.user_id)  # ty: ignore[unresolved-attribute]

    assert persona.estado_id == estado_activo.pk  # ty: ignore[unresolved-attribute]
    assert cuenta.email_verified_at is not None
    assert cuenta.is_active


def test_confirm_leaves_a_persona_outside_its_initial_state_alone(
    dmr_client: DMRClient,
    estado_inicial: EstadoRudiUser,
    estado_activo: EstadoRudiUser,
    estado_suspendido: EstadoRudiUser,
    sent_plantillas: list[dict],
) -> None:
    suspendida: RudiUser = make_persona("suspendida", estado_suspendido)

    token = issue(
        dmr_client, sent_plantillas, "auth-email-resend", email_of(suspendida)
    )

    response: PatchedHttpResponse = dmr_client.post(
        route("auth-email-confirm"),
        data={"token": token},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    suspendida.refresh_from_db()

    assert suspendida.estado_id == estado_suspendido.pk  # ty: ignore[unresolved-attribute]
    assert ApiUser.objects.get(pk=suspendida.user_id).email_verified_at is not None  # ty: ignore[unresolved-attribute]


def test_resend_ignores_a_verified_persona(
    dmr_client: DMRClient,
    persona: RudiUser,
    sent_plantillas: list[dict],
) -> None:
    token = issue(dmr_client, sent_plantillas, "auth-email-resend", email_of(persona))

    dmr_client.post(route("auth-email-confirm"), data={"token": token})

    response: PatchedHttpResponse = dmr_client.post(
        route("auth-email-resend"),
        data={"email": email_of(persona)},
    )

    assert response.status_code == HTTPStatus.ACCEPTED
    assert len(sent_plantillas) == 1


def test_password_reset_keeps_the_code_when_the_password_is_rejected(
    dmr_client: DMRClient,
    persona: RudiUser,
    sent_plantillas: list[dict],
) -> None:
    token = issue(
        dmr_client, sent_plantillas, "auth-register-recover", email_of(persona)
    )

    assert sent_plantillas[-1]["codigo"] == "recuperacion_password"

    weak: PatchedHttpResponse = dmr_client.post(
        route("auth-register-recover-confirm"),
        data={"password1": "123", "password2": "123", "token": token},
    )

    assert weak.status_code == HTTPStatus.BAD_REQUEST

    response: PatchedHttpResponse = dmr_client.post(
        route("auth-register-recover-confirm"),
        data={"password1": NEW_PASSWORD, "password2": NEW_PASSWORD, "token": token},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert ApiUser.objects.get(pk=persona.user_id).check_password(NEW_PASSWORD)  # ty: ignore[unresolved-attribute]

    persona.refresh_from_db()

    # a password reset is not an email confirmation
    assert ApiUser.objects.get(pk=persona.user_id).email_verified_at is None  # ty: ignore[unresolved-attribute]


def test_accepting_an_invitation_verifies_and_activates(
    dmr_client: DMRClient,
    estado_activo: EstadoRudiUser,
    persona: RudiUser,
    sent_plantillas: list[dict],
) -> None:
    token: str = async_to_sync(issue_codigo)(
        proposito=VerificationPurposes.INVITATION,
        user=persona.user,
    )

    assert sent_plantillas[-1]["codigo"] == "invitacion_administrativa"

    response: PatchedHttpResponse = dmr_client.post(
        route("auth-register-invite-accept"),
        data={"password1": NEW_PASSWORD, "password2": NEW_PASSWORD, "token": token},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    persona.refresh_from_db()
    cuenta: ApiUser = ApiUser.objects.get(pk=persona.user_id)  # ty: ignore[unresolved-attribute]

    assert persona.estado_id == estado_activo.pk  # ty: ignore[unresolved-attribute]
    assert cuenta.email_verified_at is not None
    assert cuenta.check_password(NEW_PASSWORD)
