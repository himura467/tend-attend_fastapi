from dataclasses import dataclass
from logging import ERROR, getLogger

from passlib.context import CryptContext

# https://github.com/pyca/bcrypt/issues/684 への対応
getLogger("passlib").setLevel(ERROR)


@dataclass(frozen=True)
class PasswordHasher:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)
