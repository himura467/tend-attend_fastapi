from abc import ABCMeta, abstractmethod
from typing import Any

from ta_core.domain.entities.base import IEntity


class IRepository(metaclass=ABCMeta):
    @abstractmethod
    async def create_async(self, entity: IEntity) -> IEntity | None:
        raise NotImplementedError()

    @abstractmethod
    async def read_by_id_async(
        self, record_id: str, joined_args: Any = None
    ) -> IEntity:
        raise NotImplementedError()

    @abstractmethod
    async def read_by_id_or_none_async(
        self, record_id: str, joined_args: Any = None
    ) -> IEntity | None:
        raise NotImplementedError()

    @abstractmethod
    async def read_by_ids_async(
        self, record_ids: set[str], joined_args: Any = None
    ) -> tuple[IEntity, ...]:
        raise NotImplementedError()

    @abstractmethod
    async def read_all_async(self, joined_args: Any = None) -> tuple[IEntity, ...]:
        raise NotImplementedError()

    @abstractmethod
    async def update_async(self, entity: IEntity) -> IEntity | None:
        raise NotImplementedError()

    @abstractmethod
    async def delete_by_id_async(self, record_id: str) -> bool:
        raise NotImplementedError()
