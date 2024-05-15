from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.dialects.mysql import BIGINT, DATETIME
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from ta_core.infrastructure.db.settings import DB_COMMON_CONNECTION_KEY
from ta_core.infrastructure.sqlalchemy.models.base import AbstractBase


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

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True, autoincrement=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DATETIME(timezone=True), server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DATETIME(timezone=True),
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        index=True,
    )
