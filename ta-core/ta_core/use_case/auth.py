import logging
from dataclasses import dataclass
from datetime import timedelta

from passlib.context import CryptContext

from ta_core.dtos.auth import CreateAccountResponse
from ta_core.error.error_code import ErrorCode
from ta_core.infrastructure.db.transaction import rollbackable
from ta_core.infrastructure.sqlalchemy.repositories.auth import AuthRepository
from ta_core.use_case.unit_of_work_base import IUnitOfWork

# https://github.com/pyca/bcrypt/issues/684 への対応
logging.getLogger("passlib").setLevel(logging.ERROR)


@dataclass(frozen=True)
class AuthUseCase:
    auth_repository: AuthRepository
    unit_of_work: IUnitOfWork

    # TODO: should be hidden
    # openssl rand -hex 32
    _SECRET_KEY = "58ae582561d69d9cd9853c01a75e6b51553c304a76d3065aad67644a0d4d26a9"
    _ALGORITHM = "HS256"
    _ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    _REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    _password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def _get_hashed_password(self, plain_password: str) -> str:
        return self._password_context.hash(plain_password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self._password_context.verify(plain_password, hashed_password)

    @rollbackable
    async def create_account_async(
        self, login_id: str, login_password: str
    ) -> CreateAccountResponse:
        account = await self.auth_repository.create_account_async(
            entity_id=0,  # TODO: generate entity_id
            login_id=login_id,
            login_password_hashed=self._get_hashed_password(login_password),
        )
        if account is None:
            return CreateAccountResponse(
                error_codes=(ErrorCode.LOGIN_ID_ALREADY_REGISTERED,)
            )
        return CreateAccountResponse(error_codes=())
