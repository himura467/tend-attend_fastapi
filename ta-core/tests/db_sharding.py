from dataclasses import dataclass
from typing import Any, Iterable, Optional, Tuple, TypeVar, Union

from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.session import ORMExecuteState
from sqlalchemy.orm.state import InstanceState
from sqlalchemy.sql.elements import ClauseElement

from tests.db_settings import (
    CONNECTIONS,
    TEST_DB_COMMON_CONNECTION_KEY,
    TEST_DB_SEQUENCE_CONNECTION_KEY,
    TEST_DB_SHARD_CONNECTION_KEYS,
    TEST_DB_SHARD_COUNT,
)
from ta_core.infrastructure.sqlalchemy.models.commons.base import AbstractCommonBase
from ta_core.infrastructure.sqlalchemy.models.sequences.base import AbstractSequenceBase
from ta_core.infrastructure.sqlalchemy.models.shards.base import AbstractShardBase

_T = TypeVar("_T", bound=Any)


def shard_chooser(
    mapper: Optional[Mapper[_T]], instance: Any, clause: Optional[ClauseElement] = None
) -> Any:
    if isinstance(instance, AbstractCommonBase):
        return TEST_DB_COMMON_CONNECTION_KEY
    if isinstance(instance, AbstractShardBase):
        shard_id = test_db_shard_resolver.resolve_shard_id(int(instance.user_id))
        return TEST_DB_SHARD_CONNECTION_KEYS[shard_id]
    if isinstance(instance, AbstractSequenceBase):
        return TEST_DB_SEQUENCE_CONNECTION_KEY
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
        return list(CONNECTIONS.keys())


def execute_chooser(context: ORMExecuteState) -> Iterable[Any]:
    shard_ids = set()
    for table in context.bind_mapper.tables:  # type: ignore
        ids = table.info.get("shard_ids")  # type: ignore
        if ids is not None:
            shard_ids.update(ids)
    if len(shard_ids) == 0:
        return list(CONNECTIONS.keys())
    else:
        return list(shard_ids)


@dataclass(frozen=True)
class TestDbShardResolver:
    shard_count: int

    def resolve_shard_id(self, user_id: int) -> int:
        return user_id % self.shard_count


test_db_shard_resolver = TestDbShardResolver(shard_count=TEST_DB_SHARD_COUNT)
