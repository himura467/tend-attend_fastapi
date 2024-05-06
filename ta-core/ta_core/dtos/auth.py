from pydantic import BaseModel
from pydantic.fields import Field

from ta_core.dtos.base import BaseModelWithErrorCodes


class CreateAccountRequest(BaseModel):
    login_id: str = Field(..., title="Login ID")
    login_password: str = Field(..., title="Login Password")


class CreateAccountResponse(BaseModelWithErrorCodes):
    pass
