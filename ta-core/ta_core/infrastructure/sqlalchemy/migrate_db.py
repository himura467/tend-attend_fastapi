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
    Recurrence,
    RecurrenceRule,
    EventAttendance,
)


async def reset_db_async() -> None:
    for engine_key, engine_value in async_engines.items():
        async with engine_value.begin() as conn:
            await conn.run_sync(AbstractBase.metadata.drop_all)
            for table in AbstractBase.metadata.tables.values():
                shard_ids = table.info.get("shard_ids")
                if shard_ids is not None and engine_key in shard_ids:
                    await conn.run_sync(table.create)
