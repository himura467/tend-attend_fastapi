from typing import Any

from sqlalchemy import Column, text
from sqlalchemy.dialects.mysql import BIGINT, DATETIME
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func

from ta_core.db.settings import DB_COMMON_CONNECTION_KEY
from ta_core.sqlalchemy.mapped_classes.base import AbstractBase


class AbstractCommonBase(AbstractBase):
    __abstract__ = True

    @declared_attr
    def __table_args__(self) -> Any:
        return {
            **super().__table_args__,
            "info": {"shard_ids": (DB_COMMON_CONNECTION_KEY,)},
        }


class AbstractCommonDynamicBase(AbstractCommonBase):
    __abstract__ = True

    id = Column(BIGINT(unsigned=True), primary_key=True)
    created_at = Column(DATETIME(timezone=True), server_default=func.now())
    updated_at = Column(
        DATETIME(timezone=True),
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )
