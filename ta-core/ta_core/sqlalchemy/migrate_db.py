from typing import Any, Iterable, Optional, Tuple, TypeVar, Union

from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.session import ORMExecuteState
from sqlalchemy.orm.state import InstanceState
from sqlalchemy.sql.elements import ClauseElement

from ta_core.db.settings import (
    CONNECTIONS,
    DB_COMMON_CONNECTION_KEY,
    DB_SEQUENCE_CONNECTION_KEY,
    DB_SHARD_CONNECTION_KEYS,
)
from ta_core.db.sharding import db_shard_resolver
from ta_core.sqlalchemy.db import Base, async_engines, async_session
from ta_core.sqlalchemy.mapped_classes.commons.common_base import AbstractCommonBase
from ta_core.sqlalchemy.mapped_classes.sequences.sequence_base import (
    AbstractSequenceBase,
)
from ta_core.sqlalchemy.mapped_classes.shards.shard_base import AbstractShardBase

_T = TypeVar("_T", bound=Any)


def shard_chooser(
    mapper: Optional[Mapper[_T]], instance: Any, clause: Optional[ClauseElement] = None
) -> Any:
    if isinstance(instance, AbstractCommonBase):
        return DB_COMMON_CONNECTION_KEY
    if isinstance(instance, AbstractShardBase):
        shard_id = db_shard_resolver.resolve_shard_id(int(instance.user_id))
        return DB_SHARD_CONNECTION_KEYS[shard_id]
    if isinstance(instance, AbstractSequenceBase):
        return DB_SEQUENCE_CONNECTION_KEY
    raise NotImplementedError()


def identity_chooser(
    mapper: Mapper[_T],
    primary_key: Union[Any, Tuple[Any, ...]],
    *,
    lazy_loaded_from: Optional[InstanceState[Any]],
    **kw: Any,
) -> Any:
    if lazy_loaded_from:
        return [lazy_loaded_from.identity_token]
    else:
        return CONNECTIONS.keys()


def execute_chooser(context: ORMExecuteState) -> Iterable[Any]:
    return CONNECTIONS.keys()


async_session.configure(
    shard_chooser=shard_chooser,
    identity_chooser=identity_chooser,
    execute_chooser=execute_chooser,
)


async def reset_db() -> None:
    for engine_key, engine_value in async_engines.items():
        async with engine_value.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            for table in Base.metadata.tables.values():
                shard_ids = table.info.get("shard_ids")
                if shard_ids is not None and engine_key in shard_ids:
                    await conn.run_sync(table.create)
