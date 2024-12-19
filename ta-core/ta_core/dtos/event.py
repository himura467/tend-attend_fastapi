from datetime import datetime

from pydantic import BaseModel
from pydantic.fields import Field

from ta_core.dtos.base import BaseModelWithErrorCodes
from ta_core.features.event import AttendanceStatus


class Event(BaseModel):
    summary: str = Field(..., title="Summary")
    location: str | None = Field(None, title="Location")
    start: datetime = Field(..., title="Start")
    end: datetime = Field(..., title="End")
    is_all_day: bool = Field(True, title="Is All Day")
    recurrence_list: list[str] = Field(..., title="Recurrence List")
    timezone: str = Field(..., title="Timezone")


class EventWithId(Event):
    id: str = Field(..., title="Event ID")


class CreateEventRequest(BaseModel):
    event: Event = Field(..., title="Event")


class CreateEventResponse(BaseModelWithErrorCodes):
    pass


class AttendEventRequest(BaseModel):
    event_id: str = Field(..., title="Event ID")
    start: datetime = Field(..., title="Start")
    status: AttendanceStatus = Field(..., title="Attendance Status")


class AttendEventResponse(BaseModelWithErrorCodes):
    pass


class GetHostEventsResponse(BaseModelWithErrorCodes):
    events: list[EventWithId] = Field(..., title="Host Events")


class GetGuestEventsResponse(BaseModelWithErrorCodes):
    events: list[EventWithId] = Field(..., title="Guest Events")
