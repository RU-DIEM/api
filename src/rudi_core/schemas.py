from uuid import UUID

from api_core.schemas.base import DTO
from api_core.schemas.path import UuidInstancePath

########################################################################################


class ProfileScopedPath(UuidInstancePath):
    profile_id: UUID


########################################################################################


class UserScopedPath(UuidInstancePath):
    user_id: UUID


########################################################################################


class UserPath(DTO):
    user_id: UUID
