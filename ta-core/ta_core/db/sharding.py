from dataclasses import dataclass

from ta_core.db.settings import DB_SHARD_COUNT


@dataclass(frozen=True)
class DbShardResolver:
    shard_count: int

    def resolve_shard_id(self, user_id: int) -> int:
        return user_id % self.shard_count


db_shard_resolver = DbShardResolver(shard_count=DB_SHARD_COUNT)
