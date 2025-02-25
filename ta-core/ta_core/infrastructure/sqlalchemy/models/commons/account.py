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
    AbstractCommonBase,
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
    followees: Mapped[list["UserAccount"]] = relationship(
        secondary="follow_association",
        primaryjoin="UserAccount.id == FollowAssociation.follower_id",
        secondaryjoin="UserAccount.id == FollowAssociation.followee_id",
        back_populates="followers",
    )
    followers: Mapped[list["UserAccount"]] = relationship(
        secondary="follow_association",
        primaryjoin="UserAccount.id == FollowAssociation.followee_id",
        secondaryjoin="UserAccount.id == FollowAssociation.follower_id",
        back_populates="followees",
    )

    def to_entity(self, depth: int = 1) -> UserAccountEntity:
        try:
            followees = (
                [followee.to_entity(depth=depth - 1) for followee in self.followees]
                if depth > 0
                else []
            )
        except StatementError:
            followees = []
        try:
            followers = (
                [follower.to_entity(depth=depth - 1) for follower in self.followers]
                if depth > 0
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
            followee_ids=[followee.id for followee in followees],
            followees=followees,
            follower_ids=[follower.id for follower in followers],
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
        )


class FollowAssociation(AbstractCommonBase):
    followee_id: Mapped[bytes] = mapped_column(
        BINARY(16), ForeignKey("user_account.id", ondelete="CASCADE"), primary_key=True
    )
    follower_id: Mapped[bytes] = mapped_column(
        BINARY(16), ForeignKey("user_account.id", ondelete="CASCADE"), primary_key=True
    )
