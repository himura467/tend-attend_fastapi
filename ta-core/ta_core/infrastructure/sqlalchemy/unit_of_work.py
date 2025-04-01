from typing import Any, Iterable, Mapping, Sequence

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

    def add_all(self, models: Iterable[object]) -> None:
        self._session.add_all(models)

    async def flush_async(self) -> None:
        await self._session.flush()

    async def commit_async(self) -> None:
        await self._session.commit()

    async def rollback_async(self) -> None:
        await self._session.rollback()

    async def delete_async(self, record: object) -> None:
        await self._session.delete(record)

    async def execute_async(
        self,
        stmt: Executable,
        params: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None,
    ) -> Result[Any]:
        return await self._session.execute(stmt, params)
