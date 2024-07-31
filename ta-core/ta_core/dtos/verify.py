from pydantic import BaseModel
from pydantic.networks import EmailStr

from ta_core.dtos.base import BaseModelWithErrorCodes


class RequestEmailVerificationRequest(BaseModel):
    host_email: EmailStr


class RequestEmailVerificationResponse(BaseModelWithErrorCodes):
    pass
