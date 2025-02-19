from datetime import datetime

from pydantic.networks import EmailStr
from sqlalchemy.dialects.mysql import BIGINT, BINARY, BOOLEAN, DATETIME, ENUM, VARCHAR
from sqlalchemy.exc import StatementError
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm.base import Mapped
from sqlalchemy.sql.schema import ForeignKey

from ta_core.domain.entities.account import UserAccount as UserAccountEntity
from ta_core.features.account import Gender
from ta_core.infrastructure.sqlalchemy.models.commons.base import (
    AbstractCommonDynamicBase,
)
from ta_core.utils.uuid import bin_to_uuid, uuid_to_bin


class UserAccount(AbstractCommonDynamicBase):
    user_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), unique=True, nullable=False, comment="User ID"
    )
    username: Mapped[str] = mapped_column(
        VARCHAR(63), unique=True, nullable=False, comment="Username"
    )
    hashed_password: Mapped[str] = mapped_column(
        VARCHAR(512), nullable=False, comment="Hashed Password"
    )
    refresh_token: Mapped[str | None] = mapped_column(
        VARCHAR(512), nullable=True, comment="Refresh Token"
    )
    nickname: Mapped[str | None] = mapped_column(
        VARCHAR(63), nullable=True, comment="Nickname"
    )
    birth_date: Mapped[datetime] = mapped_column(
        DATETIME(timezone=True), nullable=False, comment="Birth Date"
    )
    gender: Mapped[Gender] = mapped_column(
        ENUM(Gender), nullable=False, comment="Gender"
    )
    email: Mapped[EmailStr] = mapped_column(
        VARCHAR(63), unique=True, nullable=False, comment="Email Address"
    )
    email_verified: Mapped[bool] = mapped_column(
        BOOLEAN, nullable=False, comment="Email Verified"
    )
    followee_id: Mapped[bytes] = mapped_column(
        BINARY(16), ForeignKey("user_account.id", ondelete="CASCADE"), nullable=False
    )
    followee: Mapped["UserAccount"] = relationship(
        back_populates="followers", uselist=False, remote_side="UserAccount.id"
    )
    followers: Mapped[list["UserAccount"]] = relationship(
        back_populates="followee", uselist=True
    )

    def to_entity(self, include_followers: bool = True) -> UserAccountEntity:
        try:
            followers = (
                [
                    follower.to_entity(include_followers=False)
                    for follower in self.followers
                ]
                if include_followers
                else []
            )
        except StatementError:
            followers = []

        return UserAccountEntity(
            entity_id=bin_to_uuid(self.id),
            user_id=self.user_id,
            username=self.username,
            hashed_password=self.hashed_password,
            refresh_token=self.refresh_token,
            nickname=self.nickname,
            birth_date=self.birth_date,
            gender=self.gender,
            email=self.email,
            email_verified=self.email_verified,
            followee_id=bin_to_uuid(self.followee_id),
            followers=followers,
        )

    @classmethod
    def from_entity(cls, entity: UserAccountEntity) -> "UserAccount":
        return cls(
            id=uuid_to_bin(entity.id),
            user_id=entity.user_id,
            username=entity.username,
            hashed_password=entity.hashed_password,
            refresh_token=entity.refresh_token,
            nickname=entity.nickname,
            birth_date=entity.birth_date,
            gender=entity.gender,
            email=entity.email,
            email_verified=entity.email_verified,
            followee_id=uuid_to_bin(entity.followee_id),
        )
