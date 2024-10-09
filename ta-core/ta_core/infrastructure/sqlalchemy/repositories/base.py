from abc import abstractmethod
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import QueryableAttribute
from sqlalchemy.orm.strategy_options import joinedload
from sqlalchemy.sql import select
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
        try:
            self._uow.add(model)
            return entity
        except IntegrityError:
            await self._uow.rollback_async()
            return None

    async def read_by_id_async(
        self, record_id: str, joined_args: QueryableAttribute[Any] | None = None
    ) -> TEntity:
        stmt = select(self._model).where(self._model.id == record_id)
        if joined_args is not None:
            stmt = stmt.options(joinedload(joined_args))
        result = await self._uow.execute_async(stmt)
        return result.unique().scalar_one().to_entity()

    async def read_by_id_or_none_async(
        self, record_id: str, joined_args: QueryableAttribute[Any] | None = None
    ) -> TEntity | None:
        stmt = select(self._model).where(self._model.id == record_id)
        if joined_args is not None:
            stmt = stmt.options(joinedload(joined_args))
        record = (await self._uow.execute_async(stmt)).unique().scalar_one_or_none()
        return record.to_entity() if record is not None else None

    async def read_by_ids_async(
        self, record_ids: set[str], joined_args: QueryableAttribute[Any] | None = None
    ) -> tuple[TEntity, ...]:
        stmt = select(self._model).where(self._model.id.in_(record_ids))
        if joined_args is not None:
            stmt = stmt.options(joinedload(joined_args))
        result = await self._uow.execute_async(stmt)
        return tuple(record.to_entity() for record in result.unique().scalars().all())

    async def read_one_async(
        self, where: tuple[Any, ...], joined_args: QueryableAttribute[Any] | None = None
    ) -> TEntity:
        stmt = select(self._model).where(*where)
        if joined_args is not None:
            stmt = stmt.options(joinedload(joined_args))
        result = await self._uow.execute_async(stmt)
        return result.unique().scalar_one().to_entity()

    async def read_one_or_none_async(
        self, where: tuple[Any, ...], joined_args: QueryableAttribute[Any] | None = None
    ) -> TEntity | None:
        stmt = select(self._model).where(*where)
        if joined_args is not None:
            stmt = stmt.options(joinedload(joined_args))
        record = (await self._uow.execute_async(stmt)).unique().scalar_one_or_none()
        return record.to_entity() if record is not None else None

    async def read_all_async(
        self, joined_args: QueryableAttribute[Any] | None = None
    ) -> tuple[TEntity, ...]:
        stmt = select(self._model)
        if joined_args is not None:
            stmt = stmt.options(joinedload(joined_args))
        result = await self._uow.execute_async(stmt)
        return tuple(record.to_entity() for record in result.unique().scalars().all())

    async def read_order_by_limit_async(
        self,
        where: tuple[Any, ...],
        order_by: UnaryExpression[Any],
        limit: int,
        joined_args: QueryableAttribute[Any] | None = None,
    ) -> tuple[TEntity, ...]:
        stmt = select(self._model).where(*where).order_by(order_by).limit(limit)
        if joined_args is not None:
            stmt = stmt.options(joinedload(joined_args))
        result = await self._uow.execute_async(stmt)
        return tuple(record.to_entity() for record in result.unique().scalars().all())

    async def update_async(self, entity: TEntity) -> TEntity | None:
        stmt = select(self._model).where(self._model.id == entity.id)
        record = (await self._uow.execute_async(stmt)).scalar_one_or_none()
        if record is None:
            return None
        model = self._model.from_entity(entity)
        update_dict = {
            key: value for key, value in model.__dict__.items() if key != "id"
        }
        # Remove SQLAlchemy internal state
        if "_sa_instance_state" in update_dict:
            del update_dict["_sa_instance_state"]
        for key, value in update_dict.items():
            setattr(record, key, value)
        self._uow.add(record)
        return entity

    async def delete_by_id_async(self, record_id: str) -> bool:
        stmt = select(self._model).where(self._model.id == record_id)
        record = (await self._uow.execute_async(stmt)).scalar_one_or_none()
        if record is None:
            return False
        await self._uow.delete_async(record)
        return True
