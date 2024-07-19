from dataclasses import dataclass
from datetime import timedelta

from ta_core.cryptography.hash import PasswordHasher
from ta_core.cryptography.jwt import JWTCryptography
from ta_core.domain.entities.account import Account as AccountEntity
from ta_core.dtos.account import Account as AccountDto
from ta_core.dtos.auth import AuthTokenResponse
from ta_core.error.error_code import ErrorCode
from ta_core.features.account import Group
from ta_core.features.auth import TokenType
from ta_core.infrastructure.db.transaction import rollbackable
from ta_core.infrastructure.sqlalchemy.models.commons.account import (
    Account,
    GuestAccount,
    HostAccount,
)
from ta_core.infrastructure.sqlalchemy.repositories.account import (
    AccountRepository,
    GuestAccountRepository,
    HostAccountRepository,
)
from ta_core.use_case.unit_of_work_base import IUnitOfWork


@dataclass(frozen=True)
class AuthUseCase:
    uow: IUnitOfWork

    # TODO: should be hidden
    # openssl rand -hex 32
    _SECRET_KEY = "58ae582561d69d9cd9853c01a75e6b51553c304a76d3065aad67644a0d4d26a9"
    _ALGORITHM = "HS256"
    _ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    _REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    _password_hasher = PasswordHasher()
    _jwt_cryptography = JWTCryptography(
        secret_key=_SECRET_KEY,
        algorithm=_ALGORITHM,
        access_token_expires=_ACCESS_TOKEN_EXPIRES,
        refresh_token_expires=_REFRESH_TOKEN_EXPIRES,
    )

    async def get_account_by_token(
        self, token: str, token_type: TokenType
    ) -> AccountDto | None:
        account_repository = AccountRepository(self.uow, Account)  # type: ignore

        email = self._jwt_cryptography.get_subject_from_token(token, token_type)
        if email is None:
            return None
        account = await account_repository.read_by_email_or_none_async(email)
        if account is None:
            return None

        if account.group == Group.HOST:
            host_account_repository = HostAccountRepository(self.uow, HostAccount)  # type: ignore
            host_account = (
                await host_account_repository.read_by_account_id_or_none_async(
                    account.id
                )
            )
            if host_account is None:
                raise ValueError("Host account not found")
            user_id = host_account.user_id
        elif account.group == Group.GUEST:
            guest_account_repository = GuestAccountRepository(self.uow, GuestAccount)  # type: ignore
            guest_account = (
                await guest_account_repository.read_by_account_id_or_none_async(
                    account.id
                )
            )
            if guest_account is None:
                raise ValueError("Guest account not found")
            user_id = guest_account.user_id
        else:
            raise NotImplementedError()

        return AccountDto(
            account_id=account.id,
            group=account.group,
            disabled=user_id is None,
        )

    @rollbackable
    async def authenticate_async(self, email: str, password: str) -> AuthTokenResponse:
        account_repository = AccountRepository(self.uow, Account)  # type: ignore

        account = await account_repository.read_by_email_or_none_async(email)
        if account is None:
            return AuthTokenResponse(
                error_codes=(ErrorCode.EMAIL_NOT_EXIST,),
                auth_token=None,
                access_token_max_age=None,
                refresh_token_max_age=None,
            )
        if not self._password_hasher.verify_password(password, account.hashed_password):
            return AuthTokenResponse(
                error_codes=(ErrorCode.PASSWORD_INCORRECT,),
                auth_token=None,
                access_token_max_age=None,
                refresh_token_max_age=None,
            )

        token = self._jwt_cryptography.create_auth_token(account.email)

        account = account.set_refresh_token(token.refresh_token)

        if await account_repository.update_async(account) is None:
            raise ValueError("Failed to update account")

        return AuthTokenResponse(
            error_codes=(),
            auth_token=token,
            access_token_max_age=int(self._ACCESS_TOKEN_EXPIRES.total_seconds()),
            refresh_token_max_age=int(self._REFRESH_TOKEN_EXPIRES.total_seconds()),
        )

    @rollbackable
    async def refresh_auth_token_async(self, refresh_token: str) -> AuthTokenResponse:
        account_repository = AccountRepository(self.uow, Account)  # type: ignore

        account_dto = await self.get_account_by_token(refresh_token, TokenType.REFRESH)
        if account_dto is None:
            return AuthTokenResponse(
                error_codes=(ErrorCode.REFRESH_TOKEN_INVALID,),
                auth_token=None,
                access_token_max_age=None,
                refresh_token_max_age=None,
            )

        account: AccountEntity = await account_repository.read_by_id_async(
            account_dto.account_id
        )

        token = self._jwt_cryptography.create_auth_token(account.email)

        account = account.set_refresh_token(token.refresh_token)

        if await account_repository.update_async(account) is None:
            raise ValueError("Failed to update account")

        return AuthTokenResponse(
            error_codes=(),
            auth_token=token,
            access_token_max_age=int(self._ACCESS_TOKEN_EXPIRES.total_seconds()),
            refresh_token_max_age=int(self._REFRESH_TOKEN_EXPIRES.total_seconds()),
        )
