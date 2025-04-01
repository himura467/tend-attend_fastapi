from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, declared_attr

from ta_core.utils.case_converter import pascal_to_snake


class AbstractBase(DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_`%(constraint_name)s`",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )

    @declared_attr
    def __tablename__(self) -> Any:
        return pascal_to_snake(self.__name__)

    @declared_attr
    def __table_args__(self) -> Any:
        return {"mysql_engine": "InnoDB"}
