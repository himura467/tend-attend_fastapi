from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from ta_core.dtos.auth import Account as AccountDto
from ta_core.infrastructure.sqlalchemy.db import get_db_async
from ta_core.infrastructure.sqlalchemy.models.commons.auth import Account
from ta_core.infrastructure.sqlalchemy.repositories.auth import AuthRepository
from ta_core.infrastructure.sqlalchemy.unit_of_work import SqlalchemyUnitOfWork
from ta_core.use_case.auth import AuthUseCase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_account(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_db_async)
) -> AccountDto:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    auth_repository = AuthRepository(
        session=session,
        model=Account,
    )
    unit_of_work = SqlalchemyUnitOfWork(session=session)
    use_case = AuthUseCase(
        auth_repository=auth_repository,
        unit_of_work=unit_of_work,
    )

    try:
        account = await use_case.get_account_by_token(token)
        if account is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    return account


async def get_current_active_account(
    current_account: AccountDto = Depends(get_current_account),
) -> AccountDto:
    if current_account.disabled:
        raise HTTPException(status_code=400, detail="Inactive account")
    return current_account
