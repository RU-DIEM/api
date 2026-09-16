from datetime import datetime

from api_core.schemas.get import BaseGet
from rudi_auth.schemas.user import RudiUserInlineGet

########################################################################################


class RudiProfileInlineGet(BaseGet):
    user: RudiUserInlineGet

    verificado_at: datetime | None


########################################################################################


class RudiProfileGet(RudiProfileInlineGet):
    created_at: datetime
    updated_at: datetime
