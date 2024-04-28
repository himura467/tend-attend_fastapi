from typing import Any

from sqlalchemy import Column
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.ext.declarative import declared_attr

from ta_core.db.settings import DB_SEQUENCE_CONNECTION_KEY
from ta_core.sqlalchemy.mapped_classes.base import AbstractBase


class AbstractSequenceBase(AbstractBase):
    __abstract__ = True

    @declared_attr
    def __table_args__(self) -> Any:
        return {
            **super().__table_args__,
            "info": {"shard_ids": (DB_SEQUENCE_CONNECTION_KEY,)},
        }


class AbstractSequenceId(AbstractSequenceBase):
    __abstract__ = True

    id = Column(BIGINT(unsigned=True), primary_key=True)
