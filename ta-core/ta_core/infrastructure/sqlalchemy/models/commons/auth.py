from sqlalchemy.dialects.mysql import BIGINT, TINYINT, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from ta_core.domain.entities.auth import Account as AccountEntity
from ta_core.features.auth import Group
from ta_core.infrastructure.sqlalchemy.models.commons.base import (
    AbstractCommonDynamicBase,
)


class Account(AbstractCommonDynamicBase):
    login_id: Mapped[str] = mapped_column(VARCHAR(64), unique=True, comment="Login ID")
    login_password_hashed: Mapped[str] = mapped_column(
        VARCHAR(512), comment="Hashed Login Password"
    )
    refresh_token: Mapped[str] = mapped_column(
        VARCHAR(512), nullable=True, comment="Refresh Token"
    )
    user_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), nullable=True, comment="User ID"
    )
    group: Mapped[Group] = mapped_column(TINYINT(unsigned=True), comment="Group")

    def to_entity(self) -> AccountEntity:
        return AccountEntity(
            entity_id=self.id,
            login_id=self.login_id,
            login_password_hashed=self.login_password_hashed,
            refresh_token=self.refresh_token,
            user_id=self.user_id,
            group=self.group,
        )

    @staticmethod
    def from_entity(entity: AccountEntity) -> "Account":
        return Account(
            id=entity.id,
            login_id=entity.login_id,
            login_password_hashed=entity.login_password_hashed,
            refresh_token=entity.refresh_token,
            user_id=entity.user_id,
            group=entity.group,
        )
