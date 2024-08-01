from datetime import datetime

from pydantic.networks import EmailStr
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.mysql import DATETIME, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ta_core.domain.entities.verify import HostVerification as HostVerificationEntity
from ta_core.infrastructure.sqlalchemy.models.commons.account import HostAccount
from ta_core.infrastructure.sqlalchemy.models.shards.base import (
    AbstractShardDynamicBase,
)


class HostVerification(AbstractShardDynamicBase):
    host_email: Mapped[EmailStr] = mapped_column(
        VARCHAR(64), ForeignKey("host_account.email", ondelete="CASCADE")
    )
    host: Mapped[HostAccount] = relationship(back_populates="host_verifications")
    verification_token: Mapped[str] = mapped_column(
        VARCHAR(36), comment="Verification Token"
    )
    token_expires_at: Mapped[datetime] = mapped_column(
        DATETIME(timezone=True), comment="Token Expires At"
    )

    def to_entity(self) -> HostVerificationEntity:
        return HostVerificationEntity(
            entity_id=self.id,
            host_email=self.host_email,
            verification_token=self.verification_token,
            token_expires_at=self.token_expires_at,
        )

    @staticmethod
    def from_entity(entity: HostVerificationEntity) -> "HostVerification":
        return HostVerification(
            id=entity.id,
            host_email=entity.host_email,
            verification_token=entity.verification_token,
            token_expires_at=entity.token_expires_at,
        )
