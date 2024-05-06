from sqlalchemy.dialects.mysql import BIGINT, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from ta_core.domain.entities.auth import Account as AccountEntity
from ta_core.infrastructure.sqlalchemy.models.commons.base import (
    AbstractCommonDynamicBase,
)


class Account(AbstractCommonDynamicBase):
    login_id: Mapped[str] = mapped_column(VARCHAR(64), unique=True, comment="Login ID")
    login_password: Mapped[str] = mapped_column(
        VARCHAR(512), comment="Hashed Login Password"
    )
    refresh_token: Mapped[str] = mapped_column(
        VARCHAR(512), nullable=True, comment="Refresh Token"
    )
    user_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), nullable=True, comment="User ID"
    )

    def to_entity(self) -> AccountEntity:
        return AccountEntity(
            entity_id=self.id,
            login_id=self.login_id,
            login_password=self.login_password,
            refresh_token=self.refresh_token,
            user_id=self.user_id,
        )

    @staticmethod
    def from_entity(entity: AccountEntity) -> "Account":
        return Account(
            id=entity.id,
            login_id=entity.login_id,
            login_password=entity.login_password,
            refresh_token=entity.refresh_token,
            user_id=entity.user_id,
        )
