from dataclasses import dataclass
from enum import IntEnum, StrEnum


class Group(StrEnum):
    HOST = "host"
    GUEST = "guest"


class Role(IntEnum):
    HOST = 0
    GUEST = 1


groupRoleMap: dict[Group, list[Role]] = {
    Group.HOST: [Role.HOST, Role.GUEST],
    Group.GUEST: [Role.GUEST],
}


@dataclass(frozen=True)
class Account:
    account_id: str
    group: Group
    disabled: bool
