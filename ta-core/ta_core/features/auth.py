from enum import IntEnum, StrEnum


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


class Group(IntEnum):
    ADMIN = 0
    HOST = 1
    GUEST = 2


class Role(IntEnum):
    ADMIN = 0
    HOST = 1
    GUEST = 2


groupRoleMap: dict[Group, list[Role]] = {
    Group.ADMIN: [*Role],
    Group.HOST: [Role.HOST, Role.GUEST],
    Group.GUEST: [Role.GUEST],
}
