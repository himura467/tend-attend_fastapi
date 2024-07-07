from dataclasses import dataclass
from datetime import datetime, timedelta
from logging import ERROR, getLogger
from typing import Literal

from jose import jwt
from passlib.context import CryptContext

from ta_core.dtos.auth import AuthenticateResponse, AuthToken, CreateAccountResponse
from ta_core.error.error_code import ErrorCode
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

    def _get_hashed_password(self, plain_password: str) -> str:
        return self._password_context.hash(plain_password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self._password_context.verify(plain_password, hashed_password)

    def _create_token(
        self,
        subject: str,
        token_type: Literal["access", "refresh"],
        expires_delta: timedelta,
    ) -> str:
        registered_claims = {
            "sub": subject,
            "iat": datetime.utcnow(),
            "nbf": datetime.utcnow(),
            "jti": generate_uuid(),
            "exp": datetime.utcnow() + expires_delta,
        }
        private_claims = {"type": token_type}

        encoded_jwt: str = jwt.encode(
            claims={**registered_claims, **private_claims},
            key=self._SECRET_KEY,
            algorithm=self._ALGORITHM,
        )
        return encoded_jwt

    def create_auth_token(self, subject: str) -> AuthToken:
        access_token = self._create_token(
            subject=subject,
            token_type="access",
            expires_delta=self._ACCESS_TOKEN_EXPIRES,
        )
        refresh_token = self._create_token(
            subject=subject,
            token_type="refresh",
            expires_delta=self._REFRESH_TOKEN_EXPIRES,
        )
        return AuthToken(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    @rollbackable
    async def create_account_async(
        self, login_id: str, login_password: str
    ) -> CreateAccountResponse:
        account = await self.auth_repository.create_account_async(
            entity_id=generate_uuid(),
            login_id=login_id,
            login_password_hashed=self._get_hashed_password(login_password),
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

        token = self.create_auth_token(account.login_id)

        account = account.set_refresh_token(token.refresh_token)

        if await self.auth_repository.update_account_async(account) is None:
            raise ValueError("Failed to update account")

        return AuthenticateResponse(error_codes=(), auth_token=token)
