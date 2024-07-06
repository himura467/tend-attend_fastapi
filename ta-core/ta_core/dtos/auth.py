from pydantic import BaseModel
from pydantic.fields import Field

from ta_core.dtos.base import BaseModelWithErrorCodes


class CreateAccountRequest(BaseModel):
    login_id: str = Field(..., title="Login ID")
    login_password: str = Field(..., title="Login Password")


class CreateAccountResponse(BaseModelWithErrorCodes):
    pass


class AuthToken(BaseModel):
    access_token: str = Field(..., title="Access Token")
    refresh_token: str = Field(..., title="Refresh Token")
    token_type: str = Field(..., title="Token Type")


class AuthenticateResponse(BaseModelWithErrorCodes):
    auth_token: AuthToken | None = Field(None, title="Auth Token")
