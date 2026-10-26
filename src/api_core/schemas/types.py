from datetime import datetime, time
from typing import Annotated

from pydantic import AfterValidator

from .validators import check_utc_offset

########################################################################################

type PgDateTime = Annotated[datetime, AfterValidator(check_utc_offset)]
type PgTime = Annotated[time, AfterValidator(check_utc_offset)]
