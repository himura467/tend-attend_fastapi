from datetime import datetime

from pydantic.networks import EmailStr
from sqlalchemy.dialects.mysql import BINARY, DATETIME, VARCHAR
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm.base import Mapped
from sqlalchemy.sql.schema import ForeignKey

from ta_core.domain.entities.verify import HostVerification as HostVerificationEntity
from ta_core.infrastructure.sqlalchemy.models.commons.base import (
    AbstractCommonDynamicBase,
)
from ta_core.utils.uuid import bin_to_uuid, uuid_to_bin


class HostVerification(AbstractCommonDynamicBase):
    host_email: Mapped[EmailStr] = mapped_column(
        VARCHAR(64),
        ForeignKey("host_account.email", ondelete="CASCADE"),
        nullable=False,
    )
    verification_token: Mapped[bytes] = mapped_column(
        BINARY(16), nullable=False, comment="Verification Token"
    )
    token_expires_at: Mapped[datetime] = mapped_column(
        DATETIME(timezone=True), index=True, nullable=False, comment="Token Expires At"
    )

    def to_entity(self) -> HostVerificationEntity:
        return HostVerificationEntity(
            entity_id=bin_to_uuid(self.id),
            host_email=self.host_email,
            verification_token=bin_to_uuid(self.verification_token),
            token_expires_at=self.token_expires_at,
        )

    @classmethod
    def from_entity(cls, entity: HostVerificationEntity) -> "HostVerification":
        return cls(
            id=uuid_to_bin(entity.id),
            host_email=entity.host_email,
            verification_token=uuid_to_bin(entity.verification_token),
            token_expires_at=entity.token_expires_at,
        )
