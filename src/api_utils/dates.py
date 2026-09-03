import re

from datetime import timedelta
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from re import Pattern

########################################################################################

ISO_DURATION: Final[Pattern[str]] = re.compile(
    r"^P(?:(?P<days>\d+)D)?"
    r"(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?)?$",
)

########################################################################################


def parse_duration(value: str) -> timedelta:
    match = ISO_DURATION.fullmatch(value)

    if match is None or value in {"P", "PT"}:
        raise ValueError(f"'{value}' no es una duración ISO 8601 admitida.")

    parts: dict[str, int] = {
        unit: int(raw) for unit, raw in match.groupdict(default="0").items()
    }

    return timedelta(**parts)


########################################################################################


def format_duration(value: timedelta) -> str:
    total: int = int(value.total_seconds())

    days, rest = divmod(total, 86_400)
    hours, rest = divmod(rest, 3_600)
    minutes, seconds = divmod(rest, 60)

    date_part: str = f"{days}D" if days else ""

    time_part: str = "".join(
        f"{amount}{unit}"
        for amount, unit in ((hours, "H"), (minutes, "M"), (seconds, "S"))
        if amount
    )

    if not date_part and not time_part:
        return "PT0S"

    return f"P{date_part}" + (f"T{time_part}" if time_part else "")
