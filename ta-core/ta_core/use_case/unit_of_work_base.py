from abc import ABCMeta, abstractmethod


class IUnitOfWork(metaclass=ABCMeta):
    @abstractmethod
    async def commit_async(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def rollback_async(self) -> None:
        raise NotImplementedError()
