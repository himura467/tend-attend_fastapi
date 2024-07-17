from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from ta_core.dtos.auth import Account as AccountDto
from ta_core.features.auth import Role, TokenType, groupRoleMap
from ta_core.infrastructure.sqlalchemy.db import get_db_async
from ta_core.infrastructure.sqlalchemy.models.commons.auth import Account
from ta_core.infrastructure.sqlalchemy.repositories.auth import AuthRepository
from ta_core.infrastructure.sqlalchemy.unit_of_work import SqlalchemyUnitOfWork
from ta_core.use_case.auth import AuthUseCase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


@dataclass(frozen=True, eq=True)
class AccessControl:
    permit: set[Role]

    async def __call__(
        self,
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_db_async),
    ) -> AccountDto:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        uow = SqlalchemyUnitOfWork(session=session)
        auth_repository = AuthRepository(
            uow=uow,
            model=Account,
        )
        use_case = AuthUseCase(
            uow=uow,
            auth_repository=auth_repository,
        )

        try:
            account = await use_case.get_account_by_token(token, TokenType.ACCESS)
            if account is None:
                raise credentials_exception
        except Exception:
            raise credentials_exception

        if account.disabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive account"
            )

        if not self.has_compatible_role(account):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )

        return account

    def __hash__(self) -> int:
        return hash(",".join(sorted(map(str, list(self.permit)))))

    def has_compatible_role(self, account: AccountDto) -> bool:
        roles = set(groupRoleMap[account.group])
        return len(self.permit.intersection(roles)) > 0
