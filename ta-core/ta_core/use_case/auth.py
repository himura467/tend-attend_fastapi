import json
from dataclasses import dataclass
from datetime import timedelta

from ta_core.cryptography.hash import PasswordHasher
from ta_core.cryptography.jwt import JWTCryptography
from ta_core.domain.entities.account import GuestAccount as GuestAccountEntity
from ta_core.domain.entities.account import HostAccount as HostAccountEntity
from ta_core.dtos.auth import AuthTokenResponse
from ta_core.error.error_code import ErrorCode
from ta_core.features.account import Account, Group
from ta_core.features.auth import TokenType
from ta_core.infrastructure.db.transaction import rollbackable
from ta_core.infrastructure.sqlalchemy.repositories.account import (
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
    ) -> Account | None:
        token_info = self._jwt_cryptography.get_subject_and_group_from_token(
            token, token_type
        )
        if token_info is None:
            return None
        account_id, group = token_info

        if group == Group.HOST:
            host_account_repository = HostAccountRepository(self.uow)

            host_account = await host_account_repository.read_by_id_or_none_async(
                account_id
            )
            if host_account is None:
                raise ValueError("Host account not found")

            user_id = host_account.user_id
        elif group == Group.GUEST:
            guest_account_repository = GuestAccountRepository(self.uow)

            guest_account = await guest_account_repository.read_by_id_or_none_async(
                account_id
            )
            if guest_account is None:
                raise ValueError("Guest account not found")

            user_id = guest_account.user_id
        else:
            raise NotImplementedError()

        return Account(
            account_id=account_id,
            group=group,
            disabled=user_id is None,
        )

    async def auth_host_async(self, host_name: str, password: str) -> AuthTokenResponse:
        host_account_repository = HostAccountRepository(self.uow)

        host_account = await host_account_repository.read_by_host_name_or_none_async(
            host_name
        )
        if host_account is None:
            return AuthTokenResponse(
                error_codes=(ErrorCode.HOST_NAME_NOT_EXIST,),
                auth_token=None,
                access_token_max_age=None,
                refresh_token_max_age=None,
            )
        if not self._password_hasher.verify_password(
            password, host_account.hashed_password
        ):
            return AuthTokenResponse(
                error_codes=(ErrorCode.PASSWORD_INCORRECT,),
                auth_token=None,
                access_token_max_age=None,
                refresh_token_max_age=None,
            )
        token = self._jwt_cryptography.create_auth_token(host_account.id, Group.HOST)
        host_account = host_account.set_refresh_token(token.refresh_token)
        await host_account_repository.update_async(host_account)
        return AuthTokenResponse(
            error_codes=(),
            auth_token=token,
            access_token_max_age=int(self._ACCESS_TOKEN_EXPIRES.total_seconds()),
            refresh_token_max_age=int(self._REFRESH_TOKEN_EXPIRES.total_seconds()),
        )

    async def auth_guest_async(
        self,
        guest_first_name: str,
        guest_last_name: str,
        guest_nickname: str | None,
        password: str,
        host_name: str,
    ) -> AuthTokenResponse:
        host_account_repository = HostAccountRepository(self.uow)
        guest_account_repository = GuestAccountRepository(self.uow)

        host_account = await host_account_repository.read_by_host_name_or_none_async(
            host_name
        )
        if host_account is None:
            return AuthTokenResponse(
                error_codes=(ErrorCode.HOST_NAME_NOT_EXIST,),
                auth_token=None,
                access_token_max_age=None,
                refresh_token_max_age=None,
            )
        guest_account = (
            await guest_account_repository.read_by_guest_name_and_host_id_or_none_async(
                guest_first_name, guest_last_name, guest_nickname, host_account.id
            )
        )
        if guest_account is None:
            return AuthTokenResponse(
                error_codes=(ErrorCode.GUEST_NAME_NOT_EXIST,),
                auth_token=None,
                access_token_max_age=None,
                refresh_token_max_age=None,
            )
        if not self._password_hasher.verify_password(
            password, guest_account.hashed_password
        ):
            return AuthTokenResponse(
                error_codes=(ErrorCode.PASSWORD_INCORRECT,),
                auth_token=None,
                access_token_max_age=None,
                refresh_token_max_age=None,
            )
        token = self._jwt_cryptography.create_auth_token(guest_account.id, Group.GUEST)
        guest_account = guest_account.set_refresh_token(token.refresh_token)
        await guest_account_repository.update_async(guest_account)
        return AuthTokenResponse(
            error_codes=(),
            auth_token=token,
            access_token_max_age=int(self._ACCESS_TOKEN_EXPIRES.total_seconds()),
            refresh_token_max_age=int(self._REFRESH_TOKEN_EXPIRES.total_seconds()),
        )

    @rollbackable
    async def authenticate_async(
        self, auth_info_json: str, password: str
    ) -> AuthTokenResponse:
        auth_info = json.loads(auth_info_json)

        if auth_info["group"] == Group.HOST:
            return await self.auth_host_async(auth_info["host_name"], password)
        elif auth_info["group"] == Group.GUEST:
            guest_nickname = (
                auth_info["guest_nickname"]
                if auth_info["guest_nickname"] != ""
                else None
            )
            return await self.auth_guest_async(
                auth_info["guest_first_name"],
                auth_info["guest_last_name"],
                guest_nickname,
                password,
                auth_info["host_name"],
            )
        else:
            raise NotImplementedError()

    @rollbackable
    async def refresh_auth_token_async(self, refresh_token: str) -> AuthTokenResponse:
        account = await self.get_account_by_token(refresh_token, TokenType.REFRESH)
        if account is None:
            return AuthTokenResponse(
                error_codes=(ErrorCode.REFRESH_TOKEN_INVALID,),
                auth_token=None,
                access_token_max_age=None,
                refresh_token_max_age=None,
            )

        if account.disabled:
            return AuthTokenResponse(
                error_codes=(ErrorCode.ACCOUNT_DISABLED,),
                auth_token=None,
                access_token_max_age=None,
                refresh_token_max_age=None,
            )

        if account.group == Group.HOST:
            host_account_repository = HostAccountRepository(self.uow)

            host_account: HostAccountEntity = (
                await host_account_repository.read_by_id_async(account.account_id)
            )
            token = self._jwt_cryptography.create_auth_token(
                host_account.id, Group.HOST
            )
            host_account = host_account.set_refresh_token(token.refresh_token)
            await host_account_repository.update_async(host_account)
            return AuthTokenResponse(
                error_codes=(),
                auth_token=token,
                access_token_max_age=int(self._ACCESS_TOKEN_EXPIRES.total_seconds()),
                refresh_token_max_age=int(self._REFRESH_TOKEN_EXPIRES.total_seconds()),
            )
        elif account.group == Group.GUEST:
            guest_account_repository = GuestAccountRepository(self.uow)

            guest_account: GuestAccountEntity = (
                await guest_account_repository.read_by_id_async(account.account_id)
            )
            token = self._jwt_cryptography.create_auth_token(
                guest_account.id, Group.GUEST
            )
            guest_account = guest_account.set_refresh_token(token.refresh_token)
            await guest_account_repository.update_async(guest_account)
            return AuthTokenResponse(
                error_codes=(),
                auth_token=token,
                access_token_max_age=int(self._ACCESS_TOKEN_EXPIRES.total_seconds()),
                refresh_token_max_age=int(self._REFRESH_TOKEN_EXPIRES.total_seconds()),
            )
        else:
            NotImplementedError()
