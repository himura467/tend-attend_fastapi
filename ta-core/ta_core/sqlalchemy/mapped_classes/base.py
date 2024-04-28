from typing import Any

from sqlalchemy.ext.declarative import declared_attr

from ta_core.sqlalchemy.db import Base


class AbstractBase(Base):
    __abstract__ = True

    @declared_attr
    def __tablename__(self) -> Any:
        return self.__name__.lower()

    @declared_attr
    def __table_args__(self) -> Any:
        return {"mysql_engine": "InnoDB"}
