from ta_core.domain.entities.account import GuestAccount, HostAccount
from ta_core.infrastructure.sqlalchemy.repositories.base import AbstractRepository


class HostAccountRepository(AbstractRepository):
    async def create_host_account_async(
        self,
        entity_id: str,
        host_name: str,
        hashed_password: str,
        email: str,
        refresh_token: str | None = None,
        user_id: int | None = None,
    ) -> HostAccount | None:
        host_account = HostAccount(
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
    ) -> HostAccount | None:
        return await self.read_one_or_none_async(self._model.host_name == host_name)  # type: ignore


class GuestAccountRepository(AbstractRepository):
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
    ) -> GuestAccount | None:
        guest_account = GuestAccount(
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
    ) -> GuestAccount | None:
        return await self.read_one_or_none_async(
            self._model.guest_first_name == guest_first_name,  # type: ignore
            self._model.guest_last_name == guest_last_name,  # type: ignore
            self._model.guest_nickname == guest_nickname,  # type: ignore
            self._model.host_id == host_id,  # type: ignore
        )
