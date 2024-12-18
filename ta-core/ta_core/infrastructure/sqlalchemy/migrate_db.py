from typing import Any

from sqlalchemy import create_mock_engine
from sqlalchemy.sql.ddl import ExecutableDDLElement

from ta_core.aws.aurora import execute
from ta_core.constants.constants import AURORA_DATABASE_NAME
from ta_core.infrastructure.sqlalchemy.db import async_engines
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
    if AURORA_DATABASE_NAME is None:
        raise ValueError("AURORA_DATABASE_NAME is not set")
    execute(query=f"DROP DATABASE IF EXISTS {AURORA_DATABASE_NAME}", dbname="mysql")
    execute(query=f"CREATE DATABASE {AURORA_DATABASE_NAME}", dbname="mysql")
    for ddl_statement in generate_ddl():
        execute(query=ddl_statement, dbname=AURORA_DATABASE_NAME)
