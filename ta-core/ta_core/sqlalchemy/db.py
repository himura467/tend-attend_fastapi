from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.horizontal_shard import ShardedSession
from sqlalchemy.orm import DeclarativeBase

from ta_core.db.settings import CONNECTIONS

async_engines = {
    connection_key: create_async_engine(connection_string, echo=True)
    for connection_key, connection_string in CONNECTIONS.items()
}

async_session = async_sessionmaker(
    shards={
        connection_key: async_engines[connection_key].sync_engine
        for connection_key in CONNECTIONS.keys()
    },
    sync_session_class=ShardedSession,
    autocommit=False,
    autoflush=True,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db_async() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
