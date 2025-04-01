from pydantic import BaseModel
from pydantic.fields import Field

from ta_core.dtos.base import BaseModelWithErrorCodes


class StampRevisionRequest(BaseModel):
    revision: str = Field("head", title="Revision")


class StampRevisionResponse(BaseModelWithErrorCodes):
    pass


class UpgradeDbResponse(BaseModelWithErrorCodes):
    pass
