from datetime import datetime, timedelta
from typing import Final, override

from django.core.exceptions import ValidationError
from django_filters import DateTimeFromToRangeFilter
from django_filters.fields import DateTimeRangeField

########################################################################################

# postgres rejects utc offsets of 16 hours or more
MAX_UTC_OFFSET: Final[timedelta] = timedelta(hours=16)

########################################################################################


class PgDateTimeRangeField(DateTimeRangeField):
    @override
    def clean(self, value: object) -> slice | None:
        cleaned: slice | None = super().clean(value)

        if cleaned is None:
            return cleaned

        for bound in (cleaned.start, cleaned.stop):
            offset = bound.utcoffset() if isinstance(bound, datetime) else None

            if offset is not None and abs(offset) >= MAX_UTC_OFFSET:
                raise ValidationError(
                    "La zona horaria está fuera de rango.",
                    code="invalid",
                )

        return cleaned


class PgDateTimeFromToRangeFilter(DateTimeFromToRangeFilter):
    field_class = PgDateTimeRangeField
