from pydantic import BaseModel
from pydantic.fields import Field

from ta_core.dtos.base import BaseModelWithErrorCodes
from ta_core.features.account import Group


class Account(BaseModel):
    account_id: str = Field(..., title="Account ID")
    group: Group = Field(..., title="Group")
    disabled: bool = Field(..., title="Is Disabled")


class CreateHostAccountRequest(BaseModel):
    host_name: str = Field(..., title="Host Name")
    password: str = Field(..., title="Password")
    email: str = Field(..., title="Email")


class CreateHostAccountResponse(BaseModelWithErrorCodes):
    pass


class CreateGuestAccountRequest(BaseModel):
    guest_first_name: str = Field(..., title="Guest First Name")
    guest_last_name: str = Field(..., title="Guest Last Name")
    guest_nickname: str | None = Field(None, title="Guest Nickname")
    password: str = Field(..., title="Password")
    host_name: str = Field(..., title="Associated Host Name")


class CreateGuestAccountResponse(BaseModelWithErrorCodes):
    pass
