from ta_core.domain.entities.auth import Account
from ta_core.infrastructure.sqlalchemy.repositories.base import AbstractRepository


class AuthRepository(AbstractRepository):
    async def create_account_async(
        self, entity_id: str, login_id: str, login_password_hashed: str
    ) -> Account | None:
        account = Account.default(
            entity_id=entity_id,
            login_id=login_id,
            login_password=login_password_hashed,
        )
        return await self.create_async(account)
