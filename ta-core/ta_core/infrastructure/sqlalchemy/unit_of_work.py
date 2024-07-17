from typing import Any

from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import Executable

from ta_core.use_case.unit_of_work_base import IUnitOfWork


class SqlalchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, model: object) -> None:
        self._session.add(model)

    async def commit_async(self) -> None:
        await self._session.commit()

    async def rollback_async(self) -> None:
        await self._session.rollback()

    async def delete_async(self, record: object) -> None:
        await self._session.delete(record)

    async def execute_async(self, stmt: Executable) -> Result[Any]:
        return await self._session.execute(stmt)
