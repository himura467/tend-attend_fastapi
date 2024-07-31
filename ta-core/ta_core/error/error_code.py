from enum import IntEnum


class ErrorCode(IntEnum):
    ENVIRONMENT_VARIABLE_NOT_SET = 1
    HOST_NAME_OR_EMAIL_ALREADY_REGISTERED = 2
    GUEST_NAME_ALREADY_REGISTERED = 3
    HOST_NAME_NOT_EXIST = 4
    GUEST_NAME_NOT_EXIST = 5
    HOST_EMAIL_NOT_EXIST = 6
    PASSWORD_INCORRECT = 7
    REFRESH_TOKEN_INVALID = 8
    ACCOUNT_DISABLED = 9
    SMTP_ERROR = 10
