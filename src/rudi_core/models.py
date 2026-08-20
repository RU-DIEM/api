from typing import TYPE_CHECKING

from django.db.models import BooleanField, DateTimeField, Index
from django.db.models.functions import Now
from django.utils.timezone import now
from pgtrigger import After, AnyChange, Delete, Protect, SoftDelete, Trigger, Update

from api_core.models.base import ApiModel
from api_utils.strings import normalize_trigger

from typing_extensions import disjoint_base

if TYPE_CHECKING:
    from collections.abc import Sequence

########################################################################################


@disjoint_base
class RudiModel(ApiModel):
    created_at = DateTimeField(db_default=Now(), default=now)
    updated_at = DateTimeField(db_default=Now(), default=now)

    class Meta(ApiModel.Meta):
        abstract: bool = True

        indexes: Sequence[Index] = (
            Index(fields=["created_at"], name="idx_%(class)s_createdat"),
            Index(fields=["updated_at"], name="idx_%(class)s_updatedat"),
        )

        ordering: Sequence[str] = ("-id",)

        triggers: Sequence[Trigger] = (
            *ApiModel.Meta.triggers,
            Trigger(
                condition=AnyChange(),
                name="trg_touch",
                operation=Update,
                when=After,
                func=normalize_trigger("""
                    NEW.updated_at = NOW();
                    RETURN NEW;
                """),
            ),
        )


########################################################################################


@disjoint_base
class RudiAppendOnlyModel(RudiModel):
    class Meta(RudiModel.Meta):
        abstract: bool = True

        triggers: Sequence[Trigger] = (
            *RudiModel.Meta.triggers,
            Protect(name="trg_append_only", operation=(Delete | Update)),
        )


########################################################################################


@disjoint_base
class RudiProtectedModel(RudiModel):
    class Meta(RudiModel.Meta):
        abstract: bool = True

        triggers: Sequence[Trigger] = (
            *RudiModel.Meta.triggers,
            Protect(name="trg_protect_delete", operation=Delete),
        )


########################################################################################


@disjoint_base
class RudiSoftDeleteModel(RudiModel):
    is_active = BooleanField(db_default=True, default=True)

    class Meta(RudiModel.Meta):
        abstract: bool = True

        triggers: Sequence[Trigger] = (
            *RudiModel.Meta.triggers,
            SoftDelete(field="is_active", name="trg_softdelete_isactive", value=False),
        )
