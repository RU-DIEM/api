from datetime import timedelta

import pytest

from django.utils.timezone import now

from api_auth.models import ApiUser
from api_core.models.base import (
    TOUCH_UPDATEDAT,
    ApiTimestampedModel,
    remove_default_touch,
    touch_updatedat_trigger,
)

########################################################################################


def test_touch_trigger_excludes_updatedat_and_generated() -> None:
    trigger = touch_updatedat_trigger(exclude_generated=["total"])

    assert trigger.name == TOUCH_UPDATEDAT
    assert set(trigger.condition.exclude) == {"updated_at", "total"}  # ty: ignore[unresolved-attribute]


def test_remove_default_touch() -> None:
    triggers = ApiTimestampedModel.Meta.triggers

    remaining = remove_default_touch(triggers)

    assert len(remaining) == len(triggers) - 1
    assert TOUCH_UPDATEDAT not in {t.name for t in remaining}


@pytest.mark.django_db
def test_touch_trigger_keeps_explicit_updatedat(client_user: ApiUser) -> None:
    past = now() - timedelta(days=1)

    ApiUser.objects.filter(pk=client_user.pk).update(updated_at=past)
    client_user.refresh_from_db()

    assert client_user.updated_at == past

    ApiUser.objects.filter(pk=client_user.pk).update(first_name="Touched")
    client_user.refresh_from_db()

    assert client_user.updated_at > past
