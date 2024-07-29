from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column

from ta_core.infrastructure.db.settings import DB_SEQUENCE_CONNECTION_KEY
from ta_core.infrastructure.sqlalchemy.models.base import AbstractBase
from ta_core.use_case.unit_of_work_base import IUnitOfWork


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

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True, autoincrement=False
    )

    @classmethod
    async def id_generator(cls, uow: IUnitOfWork) -> int:
        record = (await uow.execute_async(select(cls))).scalar_one_or_none()
        if record is None:
            new_id = 0
        else:
            new_id = record.id + 1
            await uow.delete_async(record)
        model = cls(id=new_id)
        uow.add(model)
        return new_id
