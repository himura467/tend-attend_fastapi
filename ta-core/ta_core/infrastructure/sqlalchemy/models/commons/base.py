from datetime import datetime
from typing import Any

from sqlalchemy.dialects.mysql import BINARY, DATETIME
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm.base import Mapped
from sqlalchemy.orm.decl_api import declared_attr
from sqlalchemy.sql import text
from sqlalchemy.sql.functions import func

from ta_core.infrastructure.db.settings import COMMON_DB_CONNECTION_KEY
from ta_core.infrastructure.sqlalchemy.models.base import AbstractBase


class AbstractCommonBase(AbstractBase):
    __abstract__ = True

    @declared_attr
    def __table_args__(self) -> Any:
        return {
            **super().__table_args__,
            "info": {"shard_ids": (COMMON_DB_CONNECTION_KEY,)},
        }


class AbstractCommonDynamicBase(AbstractCommonBase):
    __abstract__ = True

    id: Mapped[bytes] = mapped_column(BINARY(16), primary_key=True, autoincrement=False)
    created_at: Mapped[datetime] = mapped_column(
        DATETIME(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DATETIME(timezone=True),
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        nullable=False,
    )
