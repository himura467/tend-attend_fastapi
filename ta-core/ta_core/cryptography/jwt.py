from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from jose import JWTError, jwt

from ta_core.dtos.auth import AuthToken as AuthTokenDto
from ta_core.features.account import Group
from ta_core.features.auth import TokenType
from ta_core.utils.uuid import UUID, generate_uuid, str_to_uuid, uuid_to_str


@dataclass(frozen=True)
class JWTCryptography:
    secret_key: str
    algorithm: str
    access_token_expires: timedelta
    refresh_token_expires: timedelta

    def _create_token(
        self,
        subject: UUID,
        group: Group,
        token_type: TokenType,
        expires_delta: timedelta,
    ) -> str:
        registered_claims = {
            "sub": uuid_to_str(subject),
            "iat": datetime.now(ZoneInfo("UTC")),
            "nbf": datetime.now(ZoneInfo("UTC")),
            "jti": uuid_to_str(generate_uuid()),
            "exp": datetime.now(ZoneInfo("UTC")) + expires_delta,
        }
        private_claims = {"group": group, "type": token_type}

        encoded_jwt: str = jwt.encode(
            claims={**registered_claims, **private_claims},
            key=self.secret_key,
            algorithm=self.algorithm,
        )
        return encoded_jwt

    def create_auth_token(self, subject: UUID, group: Group) -> AuthTokenDto:
        access_token = self._create_token(
            subject=subject,
            group=group,
            token_type=TokenType.ACCESS,
            expires_delta=self.access_token_expires,
        )
        refresh_token = self._create_token(
            subject=subject,
            group=group,
            token_type=TokenType.REFRESH,
            expires_delta=self.refresh_token_expires,
        )
        return AuthTokenDto(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    def get_subject_and_group_from_token(
        self, token: str, token_type: TokenType
    ) -> tuple[UUID, Group] | None:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != token_type:
                return None
            subject: UUID = str_to_uuid(payload.get("sub"))
            group: Group = payload.get("group")
            if not subject or not group:
                return None
        except JWTError:
            return None
        return subject, group
