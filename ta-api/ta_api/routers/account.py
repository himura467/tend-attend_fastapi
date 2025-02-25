from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from ta_core.dtos.account import (
    CreateUserAccountRequest,
    CreateUserAccountResponse,
    GetFollowersInfoResponse,
)
from ta_core.features.account import Account, Role
from ta_core.infrastructure.sqlalchemy.db import get_db_async
from ta_core.infrastructure.sqlalchemy.unit_of_work import SqlalchemyUnitOfWork
from ta_core.use_case.account import AccountUseCase

from ta_api.dependencies import AccessControl

router = APIRouter()


@router.post(
    path="/create", name="Create User Account", response_model=CreateUserAccountResponse
)
async def create_user_account(
    req: CreateUserAccountRequest, session: AsyncSession = Depends(get_db_async)
) -> CreateUserAccountResponse:
    username = req.username
    password = req.password
    nickname = req.nickname
    birth_date = req.birth_date
    gender = req.gender
    email = req.email
    followee_usernames = req.followee_usernames

    uow = SqlalchemyUnitOfWork(session=session)
    use_case = AccountUseCase(uow=uow)

    return await use_case.create_user_account_async(
        username=username,
        password=password,
        nickname=nickname,
        birth_date=birth_date,
        gender=gender,
        email=email,
        followee_usernames=set(followee_usernames),
    )


@router.get(
    path="/followers",
    name="Get Followers Info",
    response_model=GetFollowersInfoResponse,
)
async def get_followers_info(
    session: AsyncSession = Depends(get_db_async),
    account: Account = Depends(AccessControl(permit={Role.HOST})),
) -> GetFollowersInfoResponse:
    uow = SqlalchemyUnitOfWork(session=session)
    use_case = AccountUseCase(uow=uow)

    return await use_case.get_followers_info_async(followee_id=account.account_id)
