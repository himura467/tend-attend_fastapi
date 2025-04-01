from dataclasses import dataclass
from enum import Enum, IntEnum

from ta_core.utils.uuid import UUID


class Group(str, Enum):
    HOST = "host"
    GUEST = "guest"


class Role(IntEnum):
    HOST = 0
    GUEST = 1


groupRoleMap: dict[Group, list[Role]] = {
    Group.HOST: [Role.HOST, Role.GUEST],
    Group.GUEST: [Role.GUEST],
}


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


@dataclass(frozen=True)
class Account:
    account_id: UUID
    group: Group
    disabled: bool
