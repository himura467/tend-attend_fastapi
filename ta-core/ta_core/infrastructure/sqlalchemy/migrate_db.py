from typing import Any

from sqlalchemy import create_mock_engine
from sqlalchemy.sql.ddl import ExecutableDDLElement

from ta_core.aws.aurora import execute
from ta_core.constants.constants import (
    AURORA_COMMON_DBNAME,
    AURORA_SEQUENCE_DBNAME,
    AURORA_SHARD_DBNAME_PREFIX,
    DB_SHARD_COUNT,
)
from ta_core.infrastructure.sqlalchemy.db import async_engines
from ta_core.infrastructure.sqlalchemy.models.base import AbstractBase
from ta_core.infrastructure.sqlalchemy.models.commons.base import (  # noqa: F401
    AbstractCommonBase,
)
from ta_core.infrastructure.sqlalchemy.models.sequences.base import (  # noqa: F401
    AbstractSequenceBase,
)
from ta_core.infrastructure.sqlalchemy.models.shards.base import (  # noqa: F401
    AbstractShardBase,
)


def generate_ddl() -> list[str]:
    ddl_statements: list[str] = []

    def executor(sql: ExecutableDDLElement, *multiparams: Any, **params: Any) -> None:
        ddl_statements.append(
            str(sql.compile(dialect=engine.dialect)).replace("\t", "").replace("\n", "")
        )

    engine = create_mock_engine(
        url="mysql+aiomysql://",
        executor=executor,
    )
    AbstractBase.metadata.create_all(engine, checkfirst=False)
    return ddl_statements


async def reset_db_async() -> None:
    for engine_key, engine_value in async_engines.items():
        async with engine_value.begin() as conn:
            await conn.run_sync(AbstractBase.metadata.drop_all)
            for table in AbstractBase.metadata.tables.values():
                shard_ids = table.info.get("shard_ids")
                if shard_ids is not None and engine_key in shard_ids:
                    await conn.run_sync(table.create)


def reset_aurora_db() -> None:
    assert AURORA_COMMON_DBNAME is not None
    assert AURORA_SEQUENCE_DBNAME is not None
    assert AURORA_SHARD_DBNAME_PREFIX is not None
    execute(query=f"DROP DATABASE IF EXISTS {AURORA_COMMON_DBNAME}", dbname="mysql")
    execute(query=f"CREATE DATABASE {AURORA_COMMON_DBNAME}", dbname="mysql")
    execute(query=f"DROP DATABASE IF EXISTS {AURORA_SEQUENCE_DBNAME}", dbname="mysql")
    execute(query=f"CREATE DATABASE {AURORA_SEQUENCE_DBNAME}", dbname="mysql")
    for i in range(DB_SHARD_COUNT):
        shard_dbname = f"{AURORA_SHARD_DBNAME_PREFIX}{i}"
        execute(query=f"DROP DATABASE IF EXISTS {shard_dbname}", dbname="mysql")
        execute(query=f"CREATE DATABASE {shard_dbname}", dbname="mysql")
