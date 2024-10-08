from pydantic.networks import EmailStr

from ta_core.domain.entities.account import GuestAccount as GuestAccountEntity
from ta_core.domain.entities.account import HostAccount as HostAccountEntity
from ta_core.infrastructure.sqlalchemy.models.commons.account import (
    GuestAccount,
    HostAccount,
)
from ta_core.infrastructure.sqlalchemy.repositories.base import AbstractRepository


class HostAccountRepository(AbstractRepository[HostAccountEntity, HostAccount]):
    @property
    def _model(self) -> type[HostAccount]:
        return HostAccount

    async def create_host_account_async(
        self,
        entity_id: str,
        host_name: str,
        hashed_password: str,
        email: EmailStr,
        refresh_token: str | None = None,
        user_id: int | None = None,
    ) -> HostAccountEntity | None:
        host_account = HostAccountEntity(
            entity_id=entity_id,
            host_name=host_name,
            hashed_password=hashed_password,
            refresh_token=refresh_token,
            email=email,
            user_id=user_id,
        )
        return await self.create_async(host_account)

    async def read_by_host_name_or_none_async(
        self, host_name: str
    ) -> HostAccountEntity | None:
        return await self.read_one_or_none_async(
            where=(self._model.host_name == host_name,)
        )

    async def read_by_email_or_none_async(
        self, email: EmailStr
    ) -> HostAccountEntity | None:
        return await self.read_one_or_none_async(where=(self._model.email == email,))


class GuestAccountRepository(AbstractRepository[GuestAccountEntity, GuestAccount]):
    @property
    def _model(self) -> type[GuestAccount]:
        return GuestAccount

    async def create_guest_account_async(
        self,
        entity_id: str,
        guest_first_name: str,
        guest_last_name: str,
        guest_nickname: str | None,
        hashed_password: str,
        user_id: int,
        host_id: str,
        refresh_token: str | None = None,
    ) -> GuestAccountEntity | None:
        guest_account = GuestAccountEntity(
            entity_id=entity_id,
            guest_first_name=guest_first_name,
            guest_last_name=guest_last_name,
            guest_nickname=guest_nickname,
            hashed_password=hashed_password,
            refresh_token=refresh_token,
            user_id=user_id,
            host_id=host_id,
        )
        return await self.create_async(guest_account)

    async def read_by_guest_name_and_host_id_or_none_async(
        self,
        guest_first_name: str,
        guest_last_name: str,
        guest_nickname: str | None,
        host_id: str,
    ) -> GuestAccountEntity | None:
        return await self.read_one_or_none_async(
            where=(
                self._model.guest_first_name == guest_first_name,
                self._model.guest_last_name == guest_last_name,
                self._model.guest_nickname == guest_nickname,
                self._model.host_id == host_id,
            )
        )
