from abc import ABCMeta, abstractmethod

from ta_core.domain.entities.base import IEntity


class IRepository(metaclass=ABCMeta):
    @abstractmethod
    async def create_async(self, entity: IEntity) -> IEntity | None:
        raise NotImplementedError()

    @abstractmethod
    async def read_by_id_async(self, entity_id: int) -> IEntity:
        raise NotImplementedError()

    @abstractmethod
    async def read_by_id_or_none_async(self, entity_id: int) -> IEntity | None:
        raise NotImplementedError()

    @abstractmethod
    async def read_by_ids_async(self, entity_ids: set[int]) -> tuple[IEntity, ...]:
        raise NotImplementedError()

    @abstractmethod
    async def read_all_async(self) -> tuple[IEntity, ...]:
        raise NotImplementedError()

    @abstractmethod
    async def update_async(self, entity: IEntity) -> IEntity | None:
        raise NotImplementedError()

    @abstractmethod
    async def delete_by_id_async(self, entity_id: int) -> bool:
        raise NotImplementedError()
