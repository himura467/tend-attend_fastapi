from abc import ABCMeta, abstractmethod
from typing import Any, Generic, Protocol, Type, TypeVar

from sqlalchemy.orm import Mapped

from ta_core.domain.entities.base import IEntity

TEntity = TypeVar("TEntity", bound=IEntity)
TModel = TypeVar("TModel", bound="ModelProtocol[Any]")


class ModelProtocol(Protocol[TEntity]):
    id: Mapped[str]

    def to_entity(self) -> TEntity: ...

    @classmethod
    def from_entity(cls: Type[TModel], entity: TEntity) -> TModel: ...


class IRepository(Generic[TEntity, TModel], metaclass=ABCMeta):
    @abstractmethod
    async def create_async(self, entity: TEntity) -> TEntity | None:
        raise NotImplementedError()

    @abstractmethod
    async def read_by_id_async(
        self, record_id: str, joined_args: Any = None
    ) -> TEntity:
        raise NotImplementedError()

    @abstractmethod
    async def read_by_id_or_none_async(
        self, record_id: str, joined_args: Any = None
    ) -> TEntity | None:
        raise NotImplementedError()

    @abstractmethod
    async def read_by_ids_async(
        self, record_ids: set[str], joined_args: Any = None
    ) -> tuple[TEntity, ...]:
        raise NotImplementedError()

    @abstractmethod
    async def read_all_async(self, joined_args: Any = None) -> tuple[TEntity, ...]:
        raise NotImplementedError()

    @abstractmethod
    async def update_async(self, entity: TEntity) -> TEntity | None:
        raise NotImplementedError()

    @abstractmethod
    async def delete_by_id_async(self, record_id: str) -> bool:
        raise NotImplementedError()
