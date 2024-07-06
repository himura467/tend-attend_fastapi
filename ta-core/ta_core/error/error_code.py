from enum import IntEnum


class ErrorCode(IntEnum):
    LOGIN_ID_ALREADY_REGISTERED = 1
    LOGIN_ID_NOT_EXIST = 2
    LOGIN_PASSWORD_INCORRECT = 3
