from pydantic import BaseModel
from pydantic.fields import Field


class BaseModelWithErrorCodes(BaseModel):
    error_codes: tuple[int, ...] = Field(..., title="Error Codes")
