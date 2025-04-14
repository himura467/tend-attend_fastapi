from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from ta_core.dtos.event import (
    AttendEventRequest,
    AttendEventResponse,
    CreateEventRequest,
    CreateEventResponse,
    ForecastAttendanceTimeResponse,
    GetAttendancesResponse,
    GetFollowingEventsResponse,
    GetGuestCurrentAttendanceStatusResponse,
    GetMyEventsResponse,
    UpdateAttendancesRequest,
    UpdateAttendancesResponse,
)
from ta_core.features.account import Account, Role
from ta_core.infrastructure.sqlalchemy.db import get_db_async
from ta_core.infrastructure.sqlalchemy.unit_of_work import SqlalchemyUnitOfWork
from ta_core.use_case.event import EventUseCase

from ta_api.dependencies import AccessControl

router = APIRouter()


@router.post(
    path="/create",
    name="Create Event",
    response_model=CreateEventResponse,
)
async def create_event(
    req: CreateEventRequest,
    session: AsyncSession = Depends(get_db_async),
    account: Account = Depends(AccessControl(permit={Role.HOST})),
) -> CreateEventResponse:
    event = req.event

    uow = SqlalchemyUnitOfWork(session=session)
    use_case = EventUseCase(uow=uow)

    return await use_case.create_event_async(
        host_id=account.account_id,
        event_dto=event,
    )


@router.post(
    path="/attend/{event_id}/{start}",
    name="Attend Event",
    response_model=AttendEventResponse,
)
async def attend_event(
    event_id: str,
    start: datetime,
    req: AttendEventRequest,
    session: AsyncSession = Depends(get_db_async),
    account: Account = Depends(AccessControl(permit={Role.GUEST})),
) -> AttendEventResponse:
    action = req.action

    uow = SqlalchemyUnitOfWork(session=session)
    use_case = EventUseCase(uow=uow)

    return await use_case.attend_event_async(
        guest_id=account.account_id,
        event_id_str=event_id,
        start=start,
        action=action,
    )


@router.put(
    path="/attend/{event_id}/{start}",
    name="Update Guest Attendance History",
    response_model=UpdateAttendancesResponse,
)
async def update_attendances(
    event_id: str,
    start: datetime,
    req: UpdateAttendancesRequest,
    session: AsyncSession = Depends(get_db_async),
    account: Account = Depends(AccessControl(permit={Role.GUEST})),
) -> UpdateAttendancesResponse:
    attendances = req.attendances

    uow = SqlalchemyUnitOfWork(session=session)
    use_case = EventUseCase(uow=uow)

    return await use_case.update_attendances_async(
        guest_id=account.account_id,
        event_id_str=event_id,
        start=start,
        attendances=attendances,
    )


@router.get(
    path="/attend/{event_id}/{start}",
    name="Get Guest Attendance History",
    response_model=GetAttendancesResponse,
)
async def get_attendances(
    event_id: str,
    start: datetime,
    session: AsyncSession = Depends(get_db_async),
    account: Account = Depends(AccessControl(permit={Role.GUEST})),
) -> GetAttendancesResponse:
    uow = SqlalchemyUnitOfWork(session=session)
    use_case = EventUseCase(uow=uow)

    return await use_case.get_attendances_async(
        guest_id=account.account_id,
        event_id_str=event_id,
        start=start,
    )


@router.get(
    path="/mine",
    name="Get My Events",
    response_model=GetMyEventsResponse,
)
async def get_my_events(
    session: AsyncSession = Depends(get_db_async),
    account: Account = Depends(AccessControl(permit={Role.HOST})),
) -> GetMyEventsResponse:
    uow = SqlalchemyUnitOfWork(session=session)
    use_case = EventUseCase(uow=uow)

    return await use_case.get_my_events_async(account_id=account.account_id)


@router.get(
    path="/following",
    name="Get Following Events",
    response_model=GetFollowingEventsResponse,
)
async def get_following_events(
    session: AsyncSession = Depends(get_db_async),
    account: Account = Depends(AccessControl(permit={Role.GUEST})),
) -> GetFollowingEventsResponse:
    uow = SqlalchemyUnitOfWork(session=session)
    use_case = EventUseCase(uow=uow)

    return await use_case.get_following_events_async(follower_id=account.account_id)


@router.get(
    path="/attend/current/{event_id}/{start}",
    name="Get Guest Current Attendance Status",
    response_model=GetGuestCurrentAttendanceStatusResponse,
)
async def get_guest_current_attendance_status(
    event_id: str,
    start: datetime,
    session: AsyncSession = Depends(get_db_async),
    account: Account = Depends(AccessControl(permit={Role.GUEST})),
) -> GetGuestCurrentAttendanceStatusResponse:
    uow = SqlalchemyUnitOfWork(session=session)
    use_case = EventUseCase(uow=uow)

    return await use_case.get_guest_current_attendance_status_async(
        guest_id=account.account_id,
        event_id_str=event_id,
        start=start,
    )


@router.put(
    path="/attend/forecast",
    name="Forecast Attendance Time",
    response_model=ForecastAttendanceTimeResponse,
)
async def forecast_attendance_time(
    session: AsyncSession = Depends(get_db_async),
) -> ForecastAttendanceTimeResponse:
    uow = SqlalchemyUnitOfWork(session=session)
    use_case = EventUseCase(uow=uow)

    return await use_case.forecast_attendance_time_async()
