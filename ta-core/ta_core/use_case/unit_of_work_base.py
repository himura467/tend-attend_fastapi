from abc import ABCMeta, abstractmethod
from typing import Any


class IUnitOfWork(metaclass=ABCMeta):
    @abstractmethod
    def add(self, model: object) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def commit_async(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def rollback_async(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def delete_async(self, record: object) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def execute_async(self, stmt: Any) -> Any:
        raise NotImplementedError()
