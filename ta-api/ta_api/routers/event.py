from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from ta_core.dtos.event import (
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
    path="/",
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
