from collections.abc import Generator

import hypothesis as ht
import pytest
import schemathesis

from django.test.utils import override_settings
from pytest_django.live_server_helper import LiveServer
from schemathesis.checks import not_a_server_error
from schemathesis.config import (
    GenerationConfig,
    ProjectConfig,
    ProjectsConfig,
    SchemathesisConfig,
)
from schemathesis.generation import GenerationMode
from tracecov import CoverageMap
from tracecov.schemathesis import from_response

from api_auth.services.jwt import EncodedJwtPair
from api_tests.helpers import build_openapi_document

########################################################################################

pytestmark = pytest.mark.django_db(transaction=True)

########################################################################################


schema = schemathesis.openapi.from_dict(
    build_openapi_document(),
    config=SchemathesisConfig(
        projects=ProjectsConfig(
            default=ProjectConfig(
                generation=GenerationConfig(
                    modes=[GenerationMode.POSITIVE, GenerationMode.NEGATIVE],
                ),
            ),
        ),
    ),
)

########################################################################################


# session scoped, because `live_server` is: it has to start with the url already set
@pytest.fixture(autouse=True, scope="session")
def live_server_static_url() -> Generator[None]:
    # gracias django por:
    override = override_settings(STATIC_URL="/static/")

    override.enable()

    yield

    override.disable()


########################################################################################


@schema.parametrize()
@ht.settings(
    deadline=None,
    max_examples=20,
    suppress_health_check=(
        ht.HealthCheck.function_scoped_fixture,
        ht.HealthCheck.too_slow,
    ),
)
def test_api_surface_never_crashes(
    case: schemathesis.Case,
    live_server: LiveServer,
    superuser_tokens: EncodedJwtPair,
    tracecov_map: CoverageMap | None,
) -> None:
    response = case.call(
        base_url=live_server.url,
        headers={"Authorization": f"Bearer {superuser_tokens.access}"},
    )

    if tracecov_map is not None:
        tracecov_map.record_schemathesis_interactions(
            case.method,
            case.operation.full_path,
            [from_response(case.method, response)],
        )

    case.validate_response(response, checks=[not_a_server_error])
