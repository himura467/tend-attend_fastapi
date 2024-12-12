from abc import abstractmethod
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import select, update
from sqlalchemy.sql.elements import UnaryExpression

from ta_core.domain.repositories.base import IRepository, TEntity, TModel
from ta_core.use_case.unit_of_work_base import IUnitOfWork


class AbstractRepository(IRepository[TEntity, TModel]):
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    @property
    @abstractmethod
    def _model(self) -> type[TModel]:
        raise NotImplementedError()

    async def create_async(self, entity: TEntity) -> TEntity | None:
        model = self._model.from_entity(entity)
        savepoint = self._uow.begin_nested()
        try:
            self._uow.add(model)
            await self._uow.flush_async()
            return entity
        except IntegrityError:
            await savepoint.rollback()
            return None

    async def read_by_id_async(self, record_id: str) -> TEntity:
        stmt = select(self._model).where(self._model.id == record_id)
        result = await self._uow.execute_async(stmt)
        return result.scalar_one().to_entity()

    async def read_by_id_or_none_async(self, record_id: str) -> TEntity | None:
        stmt = select(self._model).where(self._model.id == record_id)
        result = await self._uow.execute_async(stmt)
        record = result.scalar_one_or_none()
        return record.to_entity() if record is not None else None

    async def read_by_ids_async(self, record_ids: set[str]) -> tuple[TEntity, ...]:
        stmt = select(self._model).where(self._model.id.in_(record_ids))
        result = await self._uow.execute_async(stmt)
        return tuple(record.to_entity() for record in result.scalars().all())

    async def read_one_async(self, where: tuple[Any, ...]) -> TEntity:
        stmt = select(self._model).where(*where)
        result = await self._uow.execute_async(stmt)
        return result.scalar_one().to_entity()

    async def read_one_or_none_async(self, where: tuple[Any, ...]) -> TEntity | None:
        stmt = select(self._model).where(*where)
        result = await self._uow.execute_async(stmt)
        record = result.scalar_one_or_none()
        return record.to_entity() if record is not None else None

    async def read_all_async(self) -> tuple[TEntity, ...]:
        stmt = select(self._model)
        result = await self._uow.execute_async(stmt)
        return tuple(record.to_entity() for record in result.scalars().all())

    async def read_order_by_limit_async(
        self,
        where: tuple[Any, ...],
        order_by: UnaryExpression[Any],
        limit: int,
    ) -> tuple[TEntity, ...]:
        stmt = select(self._model).where(*where).order_by(order_by).limit(limit)
        result = await self._uow.execute_async(stmt)
        return tuple(record.to_entity() for record in result.scalars().all())

    async def update_async(self, entity: TEntity) -> TEntity:
        model = self._model.from_entity(entity)
        update_dict = {
            key: value for key, value in model.__dict__.items() if key != "id"
        }
        # Remove SQLAlchemy internal state
        if "_sa_instance_state" in update_dict:
            del update_dict["_sa_instance_state"]
        stmt = update(self._model).where(self._model.id == model.id).values(update_dict)
        await self._uow.execute_async(stmt)
        return entity

    async def create_or_update_async(self, entity: TEntity) -> TEntity:
        created = await self.create_async(entity)
        if created is not None:
            return created
        return await self.update_async(entity)

    async def delete_by_id_async(self, record_id: str) -> bool:
        stmt = select(self._model).where(self._model.id == record_id)
        result = await self._uow.execute_async(stmt)
        record = result.scalar_one_or_none()
        if record is None:
            return False
        await self._uow.delete_async(record)
        return True
