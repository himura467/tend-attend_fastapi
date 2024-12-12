from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from ta_core.dtos.event import (
    AttendEventRequest,
    AttendEventResponse,
    CreateEventRequest,
    CreateEventResponse,
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
    path="/attend",
    name="Attend Event",
    response_model=AttendEventResponse,
)
async def attend_event(
    request: AttendEventRequest,
    session: AsyncSession = Depends(get_db_async),
    account: Account = Depends(AccessControl(permit={Role.GUEST})),
) -> AttendEventResponse:
    event_id = request.event_id
    status = request.status

    uow = SqlalchemyUnitOfWork(session=session)
    use_case = EventUseCase(uow=uow)

    return await use_case.attend_event_async(
        guest_id=account.account_id,
        event_id=event_id,
        status=status,
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
