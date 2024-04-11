from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from ta_core.settings import (
    CONNECTIONS,
    DB_COMMON_CONNECTION_KEY,
    DB_SEQUENCE_CONNECTION_KEY,
    DB_SHARD_COUNT,
)

common_engine = create_async_engine(CONNECTIONS[DB_COMMON_CONNECTION_KEY], echo=True)
sequence_engine = create_async_engine(
    CONNECTIONS[DB_SEQUENCE_CONNECTION_KEY], echo=True
)
shard_engines = tuple(
    create_async_engine(CONNECTIONS[f"shard{shard_id}"], echo=True)
    for shard_id in range(DB_SHARD_COUNT)
)

common_session = async_sessionmaker(
    autocommit=False, autoflush=False, bind=common_engine, class_=AsyncSession
)
sequence_session = async_sessionmaker(
    autocommit=False, autoflush=False, bind=sequence_engine, class_=AsyncSession
)
shard_sessions = tuple(
    async_sessionmaker(
        autocommit=False, autoflush=False, bind=shard_engine, class_=AsyncSession
    )
    for shard_engine in shard_engines
)

Base = declarative_base()


async def get_common_db() -> AsyncGenerator[AsyncSession, None]:
    async with common_session() as session:
        yield session


async def get_sequence_db() -> AsyncGenerator[AsyncSession, None]:
    async with sequence_session() as session:
        yield session


async def get_shard_db(shard_id: int) -> AsyncGenerator[AsyncSession, None]:
    async with shard_sessions[shard_id]() as session:
        yield session


async def reset_common_db() -> None:
    async with common_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def reset_sequence_db() -> None:
    async with sequence_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def reset_shard_db(shard_id: int) -> None:
    async with shard_engines[shard_id].begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
