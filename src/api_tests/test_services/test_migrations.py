import pytest

from django.core.management import call_command

########################################################################################


@pytest.mark.django_db
def test_models_match_their_migrations() -> None:
    try:
        call_command("makemigrations", "--check", "--dry-run", verbosity=0)
    except SystemExit:
        pytest.fail("models have changes that no migration records")
