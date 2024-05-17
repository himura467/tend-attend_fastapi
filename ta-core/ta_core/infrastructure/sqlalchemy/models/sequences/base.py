from typing import Any

from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column

from ta_core.infrastructure.db.settings import DB_SEQUENCE_CONNECTION_KEY
from ta_core.infrastructure.sqlalchemy.models.base import AbstractBase


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

    id: Mapped[str] = mapped_column(VARCHAR(36), primary_key=True, autoincrement=False)
