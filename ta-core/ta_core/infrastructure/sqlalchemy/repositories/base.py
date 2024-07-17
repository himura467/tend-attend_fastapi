from typing import Any, Protocol, TypeVar

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped

from ta_core.domain.entities.base import IEntity
from ta_core.domain.repositories.base import IRepository
from ta_core.use_case.unit_of_work_base import IUnitOfWork

TEntity = TypeVar("TEntity", bound=IEntity)


class ModelProtocol(Protocol):
    id: Mapped[str]

    def to_entity(self) -> TEntity: ...  # type: ignore

    @staticmethod
    def from_entity(entity: TEntity) -> "ModelProtocol": ...


class AbstractRepository(IRepository):
    def __init__(self, uow: IUnitOfWork, model: type[ModelProtocol]) -> None:
        self._uow = uow
        self._model = model

    async def create_async(self, entity: TEntity) -> TEntity | None:
        model = self._model.from_entity(entity)
        try:
            self._uow.add(model)
            return entity
        except IntegrityError:
            await self._uow.rollback_async()
            return None

    async def read_by_id_async(self, record_id: str) -> TEntity:
        stmt = select(self._model).where(self._model.id == record_id)
        result = await self._uow.execute_async(stmt)
        return result.scalar_one().to_entity()

    async def read_by_id_or_none_async(self, record_id: str) -> TEntity | None:
        stmt = select(self._model).where(self._model.id == record_id)
        record = (await self._uow.execute_async(stmt)).scalar_one_or_none()
        return record.to_entity() if record is not None else None

    async def read_by_ids_async(self, record_ids: set[str]) -> tuple[TEntity, ...]:
        stmt = select(self._model).where(self._model.id.in_(record_ids))
        result = await self._uow.execute_async(stmt)
        return tuple(record.to_entity() for record in result.all())

    async def read_one_async(self, *args: Any) -> TEntity:
        stmt = select(self._model).where(*args)
        result = await self._uow.execute_async(stmt)
        return result.scalar_one().to_entity()

    async def read_one_or_none_async(self, *args: Any) -> TEntity | None:
        stmt = select(self._model).where(*args)
        record = (await self._uow.execute_async(stmt)).scalar_one_or_none()
        return record.to_entity() if record is not None else None

    async def read_all_async(self) -> tuple[TEntity, ...]:
        stmt = select(self._model)
        result = await self._uow.execute_async(stmt)
        return tuple(record.to_entity() for record in result.all())

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
