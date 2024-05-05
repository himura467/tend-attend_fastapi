from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ta_core.dtos.auth import CreateAccountRequest, CreateAccountResponse
from ta_core.infrastructure.sqlalchemy.db import get_db_async
from ta_core.infrastructure.sqlalchemy.models.commons.auth import Account
from ta_core.infrastructure.sqlalchemy.repositories.auth import AuthRepository
from ta_core.infrastructure.sqlalchemy.unit_of_work import SqlalchemyUnitOfWork
from ta_core.use_case.auth import AuthUseCase

router = APIRouter()


@router.post("/account", name="Create Account", response_model=CreateAccountResponse)
async def create_account(
    request: CreateAccountRequest, session: AsyncSession = Depends(get_db_async)
) -> CreateAccountResponse:
    login_id = request.login_id
    login_password = request.login_password

    auth_repository = AuthRepository(
        session=session,
        model=Account,
    )
    unit_of_work = SqlalchemyUnitOfWork(session=session)
    use_case = AuthUseCase(
        auth_repository=auth_repository,
        unit_of_work=unit_of_work,
    )

    return await use_case.create_account_async(
        login_id=login_id, login_password=login_password
    )
