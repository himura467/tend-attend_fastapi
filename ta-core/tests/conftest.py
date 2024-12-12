from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio.engine import AsyncEngine, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker
from sqlalchemy.ext.horizontal_shard import ShardedSession
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text

from ta_core.infrastructure.sqlalchemy.models.base import AbstractBase
from ta_core.infrastructure.sqlalchemy.models.commons.account import (  # noqa: F401
    GuestAccount,
    HostAccount,
)
from ta_core.infrastructure.sqlalchemy.models.commons.verify import (  # noqa: F401
    HostVerification,
)
from ta_core.infrastructure.sqlalchemy.models.sequences.sequence import (  # noqa: F401
    SequenceUserId,
)
from ta_core.infrastructure.sqlalchemy.models.shards.event import (  # noqa: F401
    Event,
    EventAttendance,
    Recurrence,
    RecurrenceRule,
)
from tests.db_settings import CONNECTIONS
from tests.db_sharding import execute_chooser, identity_chooser, shard_chooser


@pytest.fixture(scope="session")
def db_connections() -> dict[str, str]:
    return CONNECTIONS


@pytest.fixture(scope="session")
def async_engines(db_connections: dict[str, str]) -> dict[str, AsyncEngine]:
    return {
        connection_key: create_async_engine(
            connection_string, echo=True, poolclass=NullPool
        )
        for connection_key, connection_string in CONNECTIONS.items()
    }


@pytest_asyncio.fixture(scope="session", autouse=True)
async def db_create_drop(
    async_engines: dict[str, AsyncEngine], db_connections: dict[str, str]
) -> AsyncGenerator[dict[str, AsyncEngine], None]:
    for engine_key in async_engines.keys():
        parsed_url = make_url(db_connections[engine_key])
        db_name = parsed_url.database
        db_engine = create_async_engine(
            url=parsed_url._replace(database=None),
            poolclass=NullPool,
        )

        async with db_engine.begin() as conn:
            await conn.execute(
                text(
                    f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET = 'utf8mb4'"
                )
            )
        async with async_engines[engine_key].connect() as conn:
            for table in AbstractBase.metadata.tables.values():
                shard_ids = table.info.get("shard_ids")
                if shard_ids is not None and engine_key in shard_ids:
                    await conn.run_sync(table.create)
    yield async_engines
    for engine_key in async_engines.keys():
        parsed_url = make_url(db_connections[engine_key])
        db_name = parsed_url.database
        db_engine = create_async_engine(
            url=parsed_url._replace(database=None),
            poolclass=NullPool,
        )

        async with async_engines[engine_key].connect() as conn:
            await conn.run_sync(AbstractBase.metadata.drop_all)
        async with db_engine.begin() as conn:
            await conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))


async def _truncate_all_tables(async_engines: dict[str, AsyncEngine]) -> None:
    for engine_key, engine_value in async_engines.items():
        async with engine_value.connect() as conn:
            await conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            for table in AbstractBase.metadata.sorted_tables:
                shard_ids = table.info.get("shard_ids")
                if shard_ids is not None and engine_key in shard_ids:
                    await conn.execute(text(f"TRUNCATE TABLE {table.name}"))
            await conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))


@pytest_asyncio.fixture()
async def test_session(
    async_engines: dict[str, AsyncEngine]
) -> AsyncGenerator[AsyncSession, None]:
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

    async_session.configure(
        shard_chooser=shard_chooser,
        identity_chooser=identity_chooser,
        execute_chooser=execute_chooser,
    )

    async with async_session() as session:
        await _truncate_all_tables(async_engines)
        yield session
