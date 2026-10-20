from typing import TYPE_CHECKING

from django.db.models import (
    RESTRICT,
    CharField,
    CheckConstraint,
    F,
    ForeignKey,
    PositiveIntegerField,
    Q,
    UniqueConstraint,
    Value,
)
from django.db.models.functions import Concat

from api_auth.models import ApiUser
from api_core.models.base import ApiProtectedModel
from api_media.enums import MediaVisibility
from api_utils.db import track_table

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################


@track_table()
class ApiMedia(ApiProtectedModel):
    """
    A file uploaded to Bunny Storage.

    Rows are never deleted, so anything referencing a file keeps a valid
    target. The size limit lives in `MEDIA_CONFIG`, not in a constraint,
    so it can be tuned per deployment without a migration.
    """

    visibility = CharField(choices=MediaVisibility.choices, max_length=10)
    mime = CharField(max_length=100)
    size = PositiveIntegerField()

    width = PositiveIntegerField(null=True)
    height = PositiveIntegerField(null=True)

    storage_key = CharField(max_length=255)
    checksum = CharField(max_length=64)

    uploaded_by = ForeignKey(on_delete=RESTRICT, related_name="+", to=ApiUser)

    class Meta(ApiProtectedModel.Meta):
        constraints: Sequence[CheckConstraint | UniqueConstraint] = (
            CheckConstraint(
                condition=Q(size__gt=0),
                name="chk_%(class)s_size",
            ),
            CheckConstraint(
                condition=Q(visibility__in=MediaVisibility.values),
                name="chk_%(class)s_visibility",
            ),
            CheckConstraint(
                condition=(
                    Q(height__isnull=True, width__isnull=True)
                    | Q(height__gt=0, width__gt=0)
                ),
                name="chk_%(class)s_dimensions",
            ),
            CheckConstraint(
                condition=(~Q(mime__startswith="image/") | Q(width__isnull=False)),
                name="chk_%(class)s_image_dimensions",
            ),
            CheckConstraint(
                condition=Q(checksum__regex=r"^[0-9a-f]{64}$"),
                name="chk_%(class)s_checksum",
            ),
            CheckConstraint(
                condition=Q(mime__regex=r"^[a-z]+/[a-zA-Z0-9.+-]+$"),
                name="chk_%(class)s_mime",
            ),
            CheckConstraint(
                condition=Q(
                    storage_key__startswith=Concat(F("visibility"), Value("/"))
                ),
                name="chk_%(class)s_storagekey_prefix",
            ),
            UniqueConstraint(fields=["storage_key"], name="unq_%(class)s_storagekey"),
        )
