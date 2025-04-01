from dataclasses import dataclass
from typing import Any, Iterable, Optional, Tuple, TypeVar, Union

from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.session import ORMExecuteState
from sqlalchemy.orm.state import InstanceState
from sqlalchemy.sql.elements import ClauseElement

from tests.db_settings import (
    TEST_COMMON_DB_CONNECTION_KEY,
    TEST_CONNECTIONS,
    TEST_DB_SHARD_COUNT,
    TEST_SEQUENCE_DB_CONNECTION_KEY,
    TEST_SHARD_DB_CONNECTION_KEYS,
)

_T = TypeVar("_T", bound=Any)


def shard_chooser(
    mapper: Optional[Mapper[_T]], instance: Any, clause: Optional[ClauseElement] = None
) -> Any:
    shard_ids: tuple[str, ...] = mapper.local_table.info.get("shard_ids") if mapper else ()  # type: ignore[attr-defined]
    if shard_ids == (TEST_COMMON_DB_CONNECTION_KEY,):
        return TEST_COMMON_DB_CONNECTION_KEY
    if shard_ids == TEST_SHARD_DB_CONNECTION_KEYS:
        shard_id = test_db_shard_resolver.resolve_shard_id(int(instance.user_id))
        return TEST_SHARD_DB_CONNECTION_KEYS[shard_id]
    if shard_ids == (TEST_SEQUENCE_DB_CONNECTION_KEY,):
        return TEST_SEQUENCE_DB_CONNECTION_KEY
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
        return list(TEST_CONNECTIONS.keys())


def execute_chooser(context: ORMExecuteState) -> Iterable[Any]:
    shard_ids = set()
    for table in context.bind_mapper.tables:  # type: ignore[union-attr]
        ids = table.info.get("shard_ids")  # type: ignore[union-attr]
        if ids is not None:
            shard_ids.update(ids)
    if len(shard_ids) == 0:
        return list(TEST_CONNECTIONS.keys())
    else:
        return list(shard_ids)


@dataclass(frozen=True)
class TestDbShardResolver:
    shard_count: int

    def resolve_shard_id(self, user_id: int) -> int:
        return user_id % self.shard_count


test_db_shard_resolver = TestDbShardResolver(shard_count=TEST_DB_SHARD_COUNT)
