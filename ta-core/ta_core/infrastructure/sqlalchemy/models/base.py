from typing import Any

from sqlalchemy.orm.decl_api import DeclarativeBase, declared_attr

from ta_core.utils.case_converter import pascal_to_snake


class AbstractBase(DeclarativeBase):
    __abstract__ = True

    @declared_attr
    def __tablename__(self) -> Any:
        return pascal_to_snake(self.__name__)

    @declared_attr
    def __table_args__(self) -> Any:
        return {"mysql_engine": "InnoDB"}
