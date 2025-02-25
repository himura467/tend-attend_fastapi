from pydantic import BaseModel
from pydantic.fields import Field

from ta_core.dtos.base import BaseModelWithErrorCodes


class AuthToken(BaseModel):
    access_token: str = Field(..., title="Access Token")
    refresh_token: str = Field(..., title="Refresh Token")
    token_type: str = Field(..., title="Token Type")


class AuthTokenResponse(BaseModelWithErrorCodes):
    auth_token: AuthToken | None = Field(None, title="Auth Token")
    access_token_max_age: int | None = Field(None, title="Access Token Max Age")
    refresh_token_max_age: int | None = Field(None, title="Refresh Token Max Age")


class RefreshAuthTokenRequest(BaseModel):
    refresh_token: str = Field(..., title="Refresh Token")


class CreateAuthTokenResponse(BaseModelWithErrorCodes):
    pass


class RefreshAuthTokenResponse(BaseModelWithErrorCodes):
    pass
