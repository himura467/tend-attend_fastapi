from sqlalchemy.ext.asyncio import AsyncSession

from ta_core.use_case.unit_of_work_base import IUnitOfWork


class SqlalchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit_async(self) -> None:
        await self._session.commit()

    async def rollback_async(self) -> None:
        await self._session.rollback()
