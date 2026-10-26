from datetime import date, datetime, time, timedelta, timezone
from uuid import UUID

import hypothesis as ht
import hypothesis.strategies as st
import pytest

from pydantic_core import PydanticCustomError

from api_core.schemas.validators import (
    check_utc_offset,
    coerce_date,
    coerce_datetime,
    coerce_uuid,
    empty_or_url,
)

########################################################################################


@ht.given(st.dates())
def test_coerce_date_parses_iso_strings(value: date) -> None:
    assert coerce_date(value.isoformat()) == value


@ht.given(
    st.text(
        alphabet=st.characters(categories=("L",)),
        min_size=1,
        max_size=20,
    ),
)
def test_coerce_date_passes_through_unparseable_strings(garbage: str) -> None:
    assert coerce_date(garbage) == garbage


def test_coerce_date_ignores_non_strings() -> None:
    assert coerce_date(None) is None
    assert coerce_date(42) == 42


########################################################################################


@ht.given(st.datetimes())
def test_coerce_datetime_parses_iso_strings(value: datetime) -> None:
    assert coerce_datetime(value.isoformat()) == value


def test_coerce_datetime_passes_through_unparseable_strings() -> None:
    assert coerce_datetime("no-es-una-fecha") == "no-es-una-fecha"


def test_coerce_datetime_ignores_non_strings() -> None:
    assert coerce_datetime(None) is None


########################################################################################


@pytest.mark.parametrize(
    "value",
    [
        datetime(2026, 1, 1),  # ruff: ignore[call-datetime-without-tzinfo]
        datetime(2026, 1, 1, tzinfo=timezone(timedelta(hours=15, minutes=59))),
        datetime(2026, 1, 1, tzinfo=timezone(-timedelta(hours=15, minutes=59))),
        time(12, tzinfo=timezone(timedelta(hours=-15, minutes=-59))),
    ],
)
def test_check_utc_offset_accepts_offsets_postgres_can_store(
    value: datetime | time,
) -> None:
    assert check_utc_offset(value) is value


@pytest.mark.parametrize(
    "value",
    [
        datetime(2026, 1, 1, tzinfo=timezone(timedelta(hours=16))),
        datetime(2026, 1, 1, tzinfo=timezone(timedelta(hours=21, minutes=33))),
        datetime(2026, 1, 1, tzinfo=timezone(-timedelta(hours=16))),
        time(12, tzinfo=timezone(timedelta(hours=21, minutes=33))),
    ],
)
def test_check_utc_offset_rejects_offsets_postgres_cannot_store(
    value: datetime | time,
) -> None:
    with pytest.raises(PydanticCustomError):
        check_utc_offset(value)


########################################################################################


@ht.given(st.uuids())
def test_coerce_uuid_parses_canonical_strings(value: UUID) -> None:
    assert coerce_uuid(str(value)) == value


def test_coerce_uuid_passes_through_unparseable_strings() -> None:
    assert coerce_uuid("no-es-un-uuid") == "no-es-un-uuid"


def test_coerce_uuid_ignores_non_strings() -> None:
    assert coerce_uuid(None) is None


########################################################################################


def test_empty_or_url_accepts_the_empty_string() -> None:
    assert empty_or_url("") == ""  # ruff: ignore[compare-to-empty-string]


def test_empty_or_url_accepts_a_valid_url() -> None:
    assert empty_or_url("https://unit.example.com") == "https://unit.example.com"


def test_empty_or_url_rejects_an_invalid_url() -> None:
    with pytest.raises(PydanticCustomError) as raised:
        empty_or_url("no-es-un-url")

    assert raised.value.context["msg"] == "Debe ser un URL válido."  # ty: ignore[not-subscriptable]
