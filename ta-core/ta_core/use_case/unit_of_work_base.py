from abc import ABCMeta, abstractmethod
from typing import Any, Iterable


class IUnitOfWork(metaclass=ABCMeta):
    @abstractmethod
    def begin_nested(self) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def add(self, model: object) -> None:
        raise NotImplementedError()

    @abstractmethod
    def add_all(self, models: Iterable[object]) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def flush_async(self) -> None:
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
    async def execute_async(self, stmt: Any, params: Any = None) -> Any:
        raise NotImplementedError()
