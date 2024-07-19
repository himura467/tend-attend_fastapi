from pydantic import BaseModel
from pydantic.fields import Field

from ta_core.dtos.base import BaseModelWithErrorCodes
from ta_core.features.account import Group


class Account(BaseModel):
    account_id: str = Field(..., title="Account ID")
    group: Group = Field(..., title="Group")
    disabled: bool = Field(..., title="Is Disabled")


class CreateHostAccountRequest(BaseModel):
    email: str = Field(..., title="Email")
    password: str = Field(..., title="Password")
    host_name: str = Field(..., title="Host Name")


class CreateHostAccountResponse(BaseModelWithErrorCodes):
    pass


class CreateGuestAccountRequest(BaseModel):
    email: str = Field(..., title="Email")
    password: str = Field(..., title="Password")
    guest_name: str = Field(..., title="Guest Name")
    host_name: str = Field(..., title="Associated Host Name")


class CreateGuestAccountResponse(BaseModelWithErrorCodes):
    pass
