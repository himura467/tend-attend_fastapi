from typing import Any

from sqlalchemy.engine.result import Result
from sqlalchemy.ext.asyncio.session import AsyncSession, AsyncSessionTransaction
from sqlalchemy.sql.base import Executable

from ta_core.use_case.unit_of_work_base import IUnitOfWork


class SqlalchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def begin_nested(self) -> AsyncSessionTransaction:
        return self._session.begin_nested()

    def add(self, model: object) -> None:
        self._session.add(model)

    async def flush_async(self) -> None:
        await self._session.flush()

    async def commit_async(self) -> None:
        await self._session.commit()

    async def rollback_async(self) -> None:
        await self._session.rollback()

    async def delete_async(self, record: object) -> None:
        await self._session.delete(record)

    async def execute_async(self, stmt: Executable) -> Result[Any]:
        return await self._session.execute(stmt)
