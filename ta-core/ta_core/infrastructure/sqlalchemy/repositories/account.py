from datetime import datetime

from pydantic.networks import EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.strategy_options import joinedload
from sqlalchemy.sql import select

from ta_core.domain.entities.account import UserAccount as UserAccountEntity
from ta_core.features.account import Gender
from ta_core.infrastructure.sqlalchemy.models.commons.account import UserAccount
from ta_core.infrastructure.sqlalchemy.repositories.base import AbstractRepository
from ta_core.utils.uuid import UUID, uuid_to_bin


class UserAccountRepository(AbstractRepository[UserAccountEntity, UserAccount]):
    @property
    def _model(self) -> type[UserAccount]:
        return UserAccount

    async def create_user_account_async(
        self,
        entity_id: UUID,
        user_id: int,
        username: str,
        hashed_password: str,
        birth_date: datetime,
        gender: Gender,
        email: EmailStr,
        followee_ids: set[UUID],
        follower_ids: set[UUID],
        refresh_token: str | None = None,
        nickname: str | None = None,
    ) -> UserAccountEntity | None:
        async def read_models_by_ids_async(record_ids: set[UUID]) -> list[UserAccount]:
            stmt = select(self._model).where(
                self._model.id.in_(uuid_to_bin(record_id) for record_id in record_ids)
            )
            result = await self._uow.execute_async(stmt)
            return result.scalars().all()

        followees = await read_models_by_ids_async(followee_ids)
        followers = await read_models_by_ids_async(follower_ids)

        user_account = UserAccount(
            id=uuid_to_bin(entity_id),
            user_id=user_id,
            username=username,
            hashed_password=hashed_password,
            refresh_token=refresh_token,
            nickname=nickname,
            birth_date=birth_date,
            gender=gender,
            email=email,
            email_verified=False,
        )

        async with self._uow.begin_nested() as savepoint:
            try:
                user_account.followees = followees
                user_account.followers = followers

                self._uow.add(user_account)
                await self._uow.flush_async()
                return user_account.to_entity()
            except IntegrityError:
                await savepoint.rollback()
                return None

    async def read_by_username_or_none_async(
        self, username: str
    ) -> UserAccountEntity | None:
        return await self.read_one_or_none_async(
            where=(self._model.username == username,)
        )

    async def read_by_usernames_async(
        self, usernames: set[str]
    ) -> tuple[UserAccountEntity, ...]:
        return await self.read_all_async(where=(self._model.username.in_(usernames),))

    async def read_by_email_or_none_async(
        self, email: EmailStr
    ) -> UserAccountEntity | None:
        return await self.read_one_or_none_async(where=(self._model.email == email,))

    async def read_with_followees_by_id_or_none_async(
        self, record_id: UUID
    ) -> UserAccountEntity | None:
        stmt = (
            select(self._model)
            .where(self._model.id == uuid_to_bin(record_id))
            .options(joinedload(UserAccount.followees))
        )
        result = await self._uow.execute_async(stmt)
        record = result.unique().scalar_one_or_none()
        return record.to_entity() if record is not None else None

    async def read_with_followers_by_id_or_none_async(
        self, record_id: UUID
    ) -> UserAccountEntity | None:
        stmt = (
            select(self._model)
            .where(self._model.id == uuid_to_bin(record_id))
            .options(joinedload(UserAccount.followers))
        )
        result = await self._uow.execute_async(stmt)
        record = result.unique().scalar_one_or_none()
        return record.to_entity() if record is not None else None
