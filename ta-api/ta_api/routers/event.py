from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from ta_core.dtos.event import (
    AttendEventRequest,
    AttendEventResponse,
    CreateEventRequest,
    CreateEventResponse,
    GetGuestCurrentAttendanceStatusResponse,
    GetGuestEventsResponse,
    GetHostEventsResponse,
)
from ta_core.features.account import Account, Role
from ta_core.infrastructure.sqlalchemy.db import get_db_async
from ta_core.infrastructure.sqlalchemy.unit_of_work import SqlalchemyUnitOfWork
from ta_core.use_case.event import EventUseCase

from ta_api.dependencies import AccessControl

router = APIRouter()


@router.post(
    path="/hosts",
    name="Create Event",
    response_model=CreateEventResponse,
)
async def create_event(
    request: CreateEventRequest,
    session: AsyncSession = Depends(get_db_async),
    account: Account = Depends(AccessControl(permit={Role.HOST})),
) -> CreateEventResponse:
    event = request.event

    uow = SqlalchemyUnitOfWork(session=session)
    use_case = EventUseCase(uow=uow)

    return await use_case.create_event_async(
        host_id=account.account_id,
        event_dto=event,
    )


@router.put(
    path="/attend/{event_id}/{start}",
    name="Attend Event",
    response_model=AttendEventResponse,
)
async def attend_event(
    event_id: str,
    start: datetime,
    request: AttendEventRequest,
    session: AsyncSession = Depends(get_db_async),
    account: Account = Depends(AccessControl(permit={Role.GUEST})),
) -> AttendEventResponse:
    event_id = event_id
    start = start
    action = request.action

    uow = SqlalchemyUnitOfWork(session=session)
    use_case = EventUseCase(uow=uow)

    return await use_case.attend_event_async(
        guest_id=account.account_id,
        event_id_str=event_id,
        start=start,
        action=action,
    )


@router.get(
    path="/hosts",
    name="Get Host Events",
    response_model=GetHostEventsResponse,
)
async def get_host_events(
    session: AsyncSession = Depends(get_db_async),
    account: Account = Depends(AccessControl(permit={Role.HOST})),
) -> GetHostEventsResponse:
    uow = SqlalchemyUnitOfWork(session=session)
    use_case = EventUseCase(uow=uow)

    return await use_case.get_host_events_async(host_id=account.account_id)


@router.get(
    path="/guests",
    name="Get Guest Events",
    response_model=GetGuestEventsResponse,
)
async def get_guest_events(
    session: AsyncSession = Depends(get_db_async),
    account: Account = Depends(AccessControl(permit={Role.GUEST})),
) -> GetGuestEventsResponse:
    uow = SqlalchemyUnitOfWork(session=session)
    use_case = EventUseCase(uow=uow)

    return await use_case.get_guest_events_async(guest_id=account.account_id)


@router.get(
    path="/attend/current/{event_id}/{start}",
    name="Get Guest Current Attendance Status",
    response_model=GetGuestCurrentAttendanceStatusResponse,
)
async def get_guest_current_attendance_status(
    event_id: str,
    start: datetime,
    session: AsyncSession = Depends(get_db_async),
    account: Account = Depends(AccessControl(permit={Role.HOST, Role.GUEST})),
) -> GetGuestCurrentAttendanceStatusResponse:
    uow = SqlalchemyUnitOfWork(session=session)
    use_case = EventUseCase(uow=uow)

    return await use_case.get_guest_current_attendance_status_async(
        guest_id=account.account_id,
        event_id_str=event_id,
        start=start,
    )
