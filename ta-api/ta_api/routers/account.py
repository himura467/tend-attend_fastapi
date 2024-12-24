from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from ta_core.dtos.account import (
    CreateGuestAccountRequest,
    CreateGuestAccountResponse,
    CreateHostAccountRequest,
    CreateHostAccountResponse,
    GetGuestsInfoResponse,
)
from ta_core.features.account import Account, Role
from ta_core.infrastructure.sqlalchemy.db import get_db_async
from ta_core.infrastructure.sqlalchemy.unit_of_work import SqlalchemyUnitOfWork
from ta_core.use_case.account import AccountUseCase

from ta_api.dependencies import AccessControl

router = APIRouter()


@router.post(
    path="/hosts", name="Create Host Account", response_model=CreateHostAccountResponse
)
async def create_host_account(
    req: CreateHostAccountRequest, session: AsyncSession = Depends(get_db_async)
) -> CreateHostAccountResponse:
    host_name = req.host_name
    password = req.password
    email = req.email

    uow = SqlalchemyUnitOfWork(session=session)
    use_case = AccountUseCase(uow=uow)

    return await use_case.create_host_account_async(
        host_name=host_name, password=password, email=email
    )


@router.post(
    path="/guests",
    name="Create Guest Account",
    response_model=CreateGuestAccountResponse,
)
async def create_guest_account(
    req: CreateGuestAccountRequest, session: AsyncSession = Depends(get_db_async)
) -> CreateGuestAccountResponse:
    guest_first_name = req.guest_first_name
    guest_last_name = req.guest_last_name
    guest_nickname = req.guest_nickname
    birth_date = req.birth_date
    gender = req.gender
    password = req.password
    host_name = req.host_name

    uow = SqlalchemyUnitOfWork(session=session)
    use_case = AccountUseCase(uow=uow)

    return await use_case.create_guest_account_async(
        guest_first_name=guest_first_name,
        guest_last_name=guest_last_name,
        guest_nickname=guest_nickname,
        birth_date=birth_date,
        gender=gender,
        password=password,
        host_name=host_name,
    )


@router.get(
    path="/guests", name="Get Guests Info", response_model=GetGuestsInfoResponse
)
async def get_guests_info(
    session: AsyncSession = Depends(get_db_async),
    account: Account = Depends(AccessControl(permit={Role.HOST})),
) -> GetGuestsInfoResponse:
    uow = SqlalchemyUnitOfWork(session=session)
    use_case = AccountUseCase(uow=uow)

    return await use_case.get_guests_info_async(host_id=account.account_id)
