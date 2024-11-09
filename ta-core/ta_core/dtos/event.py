from pydantic import BaseModel
from pydantic.fields import Field

from ta_core.dtos.base import BaseModelWithErrorCodes
from ta_core.features.event import Event


class CreateEventRequest(BaseModel):
    event: Event = Field(..., title="Event")


class CreateEventResponse(BaseModelWithErrorCodes):
    pass
