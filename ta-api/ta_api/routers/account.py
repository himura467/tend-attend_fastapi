from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ta_core.dtos.account import (
    CreateGuestAccountRequest,
    CreateGuestAccountResponse,
    CreateHostAccountRequest,
    CreateHostAccountResponse,
)
from ta_core.infrastructure.sqlalchemy.db import get_db_async
from ta_core.infrastructure.sqlalchemy.unit_of_work import SqlalchemyUnitOfWork
from ta_core.use_case.account import AccountUseCase

router = APIRouter()


@router.post(
    "/hosts", name="Create Host Account", response_model=CreateHostAccountResponse
)
async def create_host_account(
    req: CreateHostAccountRequest, session: AsyncSession = Depends(get_db_async)
) -> CreateHostAccountResponse:
    email = req.email
    password = req.password
    host_name = req.host_name

    uow = SqlalchemyUnitOfWork(session=session)
    use_case = AccountUseCase(uow=uow)

    return await use_case.create_host_account_async(
        email=email, password=password, host_name=host_name
    )


@router.post(
    "/guests", name="Create Guest Account", response_model=CreateGuestAccountResponse
)
async def create_guest_account(
    req: CreateGuestAccountRequest, session: AsyncSession = Depends(get_db_async)
) -> CreateGuestAccountResponse:
    email = req.email
    password = req.password
    guest_name = req.guest_name
    host_name = req.host_name

    uow = SqlalchemyUnitOfWork(session=session)
    use_case = AccountUseCase(uow=uow)

    return await use_case.create_guest_account_async(
        email=email, password=password, guest_name=guest_name, host_name=host_name
    )
