from dataclasses import dataclass
from datetime import datetime, timedelta

from jose import JWTError, jwt

from ta_core.dtos.auth import AuthToken
from ta_core.features.auth import TokenType
from ta_core.utils.uuid import generate_uuid


@dataclass(frozen=True)
class JWTCryptography:
    secret_key: str
    algorithm: str
    access_token_expires: timedelta
    refresh_token_expires: timedelta

    def _create_token(
        self,
        subject: str,
        token_type: TokenType,
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
            key=self.secret_key,
            algorithm=self.algorithm,
        )
        return encoded_jwt

    def create_auth_token(self, subject: str) -> AuthToken:
        access_token = self._create_token(
            subject=subject,
            token_type=TokenType.ACCESS,
            expires_delta=self.access_token_expires,
        )
        refresh_token = self._create_token(
            subject=subject,
            token_type=TokenType.REFRESH,
            expires_delta=self.refresh_token_expires,
        )
        return AuthToken(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    def get_subject_from_token(self, token: str, token_type: TokenType) -> str | None:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != token_type:
                return None
            subject: str = payload.get("sub")
            if subject is None:
                return None
        except JWTError:
            return None
        return subject
