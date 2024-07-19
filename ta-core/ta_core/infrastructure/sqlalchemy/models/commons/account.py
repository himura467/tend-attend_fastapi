from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.mysql import BIGINT, TINYINT, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ta_core.domain.entities.account import Account as AccountEntity
from ta_core.domain.entities.account import GuestAccount as GuestAccountEntity
from ta_core.domain.entities.account import HostAccount as HostAccountEntity
from ta_core.features.account import Group
from ta_core.infrastructure.sqlalchemy.models.commons.base import (
    AbstractCommonDynamicBase,
)


class Account(AbstractCommonDynamicBase):
    email: Mapped[str] = mapped_column(
        VARCHAR(64), unique=True, comment="Email Address"
    )
    hashed_password: Mapped[str] = mapped_column(
        VARCHAR(512), comment="Hashed Password"
    )
    refresh_token: Mapped[str] = mapped_column(
        VARCHAR(512), nullable=True, comment="Refresh Token"
    )
    group: Mapped[Group] = mapped_column(TINYINT(unsigned=True), comment="Group")
    hosts: Mapped[List["HostAccount"]] = relationship(back_populates="account")
    guests: Mapped[List["GuestAccount"]] = relationship(back_populates="account")

    def to_entity(self) -> AccountEntity:
        return AccountEntity(
            entity_id=self.id,
            email=self.email,
            hashed_password=self.hashed_password,
            refresh_token=self.refresh_token,
            group=self.group,
        )

    @staticmethod
    def from_entity(entity: AccountEntity) -> "Account":
        return Account(
            id=entity.id,
            email=entity.email,
            hashed_password=entity.hashed_password,
            refresh_token=entity.refresh_token,
            group=entity.group,
        )


class HostAccount(AbstractCommonDynamicBase):
    account_id: Mapped[str] = mapped_column(
        VARCHAR(36), ForeignKey("account.id", ondelete="CASCADE")
    )
    account: Mapped["Account"] = relationship(back_populates="hosts")
    user_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), nullable=True, comment="User ID"
    )
    host_name: Mapped[str] = mapped_column(
        VARCHAR(64), unique=True, comment="Host Name"
    )
    guests: Mapped[List["GuestAccount"]] = relationship(back_populates="host")

    def to_entity(self) -> HostAccountEntity:
        return HostAccountEntity(
            entity_id=self.id,
            account_id=self.account_id,
            user_id=self.user_id,
            host_name=self.host_name,
        )

    @staticmethod
    def from_entity(entity: HostAccountEntity) -> "HostAccount":
        return HostAccount(
            id=entity.id,
            account_id=entity.account_id,
            user_id=entity.user_id,
            host_name=entity.host_name,
        )


class GuestAccount(AbstractCommonDynamicBase):
    account_id: Mapped[str] = mapped_column(
        VARCHAR(36), ForeignKey("account.id", ondelete="CASCADE")
    )
    account: Mapped["Account"] = relationship(back_populates="guests")
    user_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), nullable=True, comment="User ID"
    )
    host_id: Mapped[str] = mapped_column(
        VARCHAR(36), ForeignKey("host_account.id", ondelete="CASCADE")
    )
    host: Mapped["HostAccount"] = relationship(back_populates="guests")
    guest_name: Mapped[str] = mapped_column(
        VARCHAR(64), unique=True, comment="Guest Name"
    )

    def to_entity(self) -> GuestAccountEntity:
        return GuestAccountEntity(
            entity_id=self.id,
            account_id=self.account_id,
            user_id=self.user_id,
            host_id=self.host_id,
            guest_name=self.guest_name,
        )

    @staticmethod
    def from_entity(entity: GuestAccountEntity) -> "GuestAccount":
        return GuestAccount(
            id=entity.id,
            account_id=entity.account_id,
            user_id=entity.user_id,
            host_id=entity.host_id,
            guest_name=entity.guest_name,
        )
