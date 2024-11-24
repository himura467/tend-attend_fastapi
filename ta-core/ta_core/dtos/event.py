from datetime import datetime

from pydantic import BaseModel
from pydantic.fields import Field

from ta_core.dtos.base import BaseModelWithErrorCodes


class CreateEventRequest(BaseModel):
    summary: str = Field(..., title="Summary")
    location: str | None = Field(None, title="Location")
    start: datetime = Field(..., title="Start")
    end: datetime = Field(..., title="End")
    recurrence_list: list[str] = Field([], title="Recurrence List")
    isAllDay: bool = Field(True, title="Is All Day")


class CreateEventResponse(BaseModelWithErrorCodes):
    pass
