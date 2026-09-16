from datetime import date, datetime
from enum import Enum
from typing import Annotated
from uuid import UUID

from pydantic import BeforeValidator, Field, PositiveInt

from .base import DTO
from .validators import coerce_date, coerce_datetime, coerce_uuid

########################################################################################

type PrimaryKey = UUID | PositiveInt

type IsoDate = Annotated[date, BeforeValidator(func=coerce_date)]

type IsoDateTime = Annotated[datetime, BeforeValidator(func=coerce_datetime)]

type LaxEnum[E: Enum] = Annotated[E, Field(strict=False)]

type RelatedId = Annotated[UUID, BeforeValidator(func=coerce_uuid)]

########################################################################################


class BaseGet[PK: PrimaryKey = UUID](DTO):
    id: PK
