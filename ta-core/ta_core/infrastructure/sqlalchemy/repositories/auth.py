from ta_core.domain.entities.auth import Account
from ta_core.features.auth import Group
from ta_core.infrastructure.sqlalchemy.repositories.base import AbstractRepository


class AuthRepository(AbstractRepository):
    async def create_account_async(
        self, entity_id: str, login_id: str, login_password_hashed: str, group: Group
    ) -> Account | None:
        account = Account.default(
            entity_id=entity_id,
            login_id=login_id,
            login_password_hashed=login_password_hashed,
            group=group,
        )
        return await self.create_async(account)

    async def read_account_by_login_id_or_none_async(
        self, login_id: str
    ) -> Account | None:
        return await self.read_one_or_none_async(self._model.login_id == login_id)  # type: ignore

    async def update_account_async(self, account: Account) -> Account | None:
        return await self.update_async(account)
