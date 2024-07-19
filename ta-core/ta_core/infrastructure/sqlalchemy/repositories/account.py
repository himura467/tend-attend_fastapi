from ta_core.domain.entities.account import Account, GuestAccount, HostAccount
from ta_core.features.account import Group
from ta_core.infrastructure.sqlalchemy.repositories.base import AbstractRepository


class AccountRepository(AbstractRepository):
    async def create_account_async(
        self,
        entity_id: str,
        email: str,
        hashed_password: str,
        refresh_token: str | None,
        group: Group,
    ) -> Account | None:
        account = Account(
            entity_id=entity_id,
            email=email,
            hashed_password=hashed_password,
            refresh_token=refresh_token,
            group=group,
        )
        return await self.create_async(account)

    async def read_by_email_or_none_async(self, email: str) -> Account | None:
        return await self.read_one_or_none_async(self._model.email == email)  # type: ignore


class HostAccountRepository(AbstractRepository):
    async def create_host_account_async(
        self, entity_id: str, account_id: str, host_name: str
    ) -> HostAccount | None:
        host_account = HostAccount(
            entity_id=entity_id,
            account_id=account_id,
            user_id=None,
            host_name=host_name,
        )
        return await self.create_async(host_account)

    async def read_by_account_id_or_none_async(
        self, account_id: str
    ) -> HostAccount | None:
        return await self.read_one_or_none_async(self._model.account_id == account_id)  # type: ignore

    async def read_by_host_name_or_none_async(
        self, host_name: str
    ) -> HostAccount | None:
        return await self.read_one_or_none_async(self._model.host_name == host_name)  # type: ignore


class GuestAccountRepository(AbstractRepository):
    async def create_guest_account_async(
        self, entity_id: str, account_id: str, guest_name: str, host_id: str
    ) -> GuestAccount | None:
        guest_account = GuestAccount(
            entity_id=entity_id,
            account_id=account_id,
            user_id=None,
            host_id=host_id,
            guest_name=guest_name,
        )
        return await self.create_async(guest_account)

    async def read_by_account_id_or_none_async(
        self, account_id: str
    ) -> GuestAccount | None:
        return await self.read_one_or_none_async(self._model.account_id == account_id)  # type: ignore
