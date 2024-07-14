from dataclasses import dataclass
from datetime import timedelta
from logging import ERROR, getLogger

from passlib.context import CryptContext

from ta_core.cryptography.jwt import JWTCryptography
from ta_core.domain.entities.auth import Account
from ta_core.dtos.auth import Account as AccountDto
from ta_core.dtos.auth import (
    AuthenticateResponse,
    CreateAccountResponse,
    RefreshAuthTokenResponse,
)
from ta_core.error.error_code import ErrorCode
from ta_core.features.auth import Group, TokenType
from ta_core.ids.uuid import generate_uuid
from ta_core.infrastructure.db.transaction import rollbackable
from ta_core.infrastructure.sqlalchemy.repositories.auth import AuthRepository
from ta_core.use_case.unit_of_work_base import IUnitOfWork

# https://github.com/pyca/bcrypt/issues/684 への対応
getLogger("passlib").setLevel(ERROR)


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

    _jwt_cryptography = JWTCryptography(
        password_context=_password_context,
        secret_key=_SECRET_KEY,
        algorithm=_ALGORITHM,
        access_token_expires=_ACCESS_TOKEN_EXPIRES,
        refresh_token_expires=_REFRESH_TOKEN_EXPIRES,
    )

    def _get_hashed_password(self, plain_password: str) -> str:
        return self._password_context.hash(plain_password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self._password_context.verify(plain_password, hashed_password)

    async def get_account_by_token(
        self, token: str, token_type: TokenType
    ) -> AccountDto | None:
        login_id = self._jwt_cryptography.get_subject_from_token(token, token_type)
        if login_id is None:
            return None
        account = await self.auth_repository.read_account_by_login_id_or_none_async(
            login_id
        )
        if account is None:
            return None
        user_id = account.user_id if account.user_id is not None else 0
        return AccountDto(
            account_id=account.id,
            user_id=user_id,
            group=account.group,
            disabled=account.user_id is None,
        )

    @rollbackable
    async def create_account_async(
        self, login_id: str, login_password: str, group: Group
    ) -> CreateAccountResponse:
        account = await self.auth_repository.create_account_async(
            entity_id=generate_uuid(),
            login_id=login_id,
            login_password_hashed=self._get_hashed_password(login_password),
            group=group,
        )
        if account is None:
            return CreateAccountResponse(
                error_codes=(ErrorCode.LOGIN_ID_ALREADY_REGISTERED,)
            )
        return CreateAccountResponse(error_codes=())

    @rollbackable
    async def authenticate_async(
        self, login_id: str, login_password: str
    ) -> AuthenticateResponse:
        account = await self.auth_repository.read_account_by_login_id_or_none_async(
            login_id
        )
        if account is None:
            return AuthenticateResponse(
                error_codes=(ErrorCode.LOGIN_ID_NOT_EXIST,), auth_token=None
            )
        if not self._verify_password(login_password, account.login_password_hashed):
            return AuthenticateResponse(
                error_codes=(ErrorCode.LOGIN_PASSWORD_INCORRECT,), auth_token=None
            )

        token = self._jwt_cryptography.create_auth_token(account.login_id)

        account = account.set_refresh_token(token.refresh_token)

        if await self.auth_repository.update_account_async(account) is None:
            raise ValueError("Failed to update account")

        return AuthenticateResponse(error_codes=(), auth_token=token)

    @rollbackable
    async def refresh_auth_token_async(
        self, refresh_token: str
    ) -> RefreshAuthTokenResponse:
        account_dto = await self.get_account_by_token(refresh_token, TokenType.REFRESH)
        if account_dto is None:
            return RefreshAuthTokenResponse(
                error_codes=(ErrorCode.INVALID_REFRESH_TOKEN,), auth_token=None
            )

        account: Account = await self.auth_repository.read_by_id_async(
            account_dto.account_id
        )

        token = self._jwt_cryptography.create_auth_token(account.login_id)

        account = account.set_refresh_token(token.refresh_token)

        if await self.auth_repository.update_account_async(account) is None:
            raise ValueError("Failed to update account")

        return RefreshAuthTokenResponse(error_codes=(), auth_token=token)
