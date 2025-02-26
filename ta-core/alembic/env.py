import inspect
import logging
import re
from importlib import import_module
from logging.config import fileConfig
from typing import Any

from sqlalchemy import MetaData, pool
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm.decl_api import DeclarativeAttributeIntercept

from alembic import context
from ta_core.constants.constants import DB_SHARD_COUNT
from ta_core.infrastructure.db.settings import CONNECTIONS, DB_CONFIG

USE_TWOPHASE = False

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")

# gather section names referring to different
# databases.  These are named "engine1", "engine2"
# in the sample .ini file.
databases = config.get_main_option("databases", "")
db_names = CONNECTIONS.keys()
config.set_section_option("alembic", "db_names", ", ".join(db_names))


def engines_from_config(
    configuration: dict[str, Any], prefix: str = "sqlalchemy.", **kwargs: Any
) -> tuple[Engine, ...]:
    options = {
        key[len(prefix) :]: configuration[key]
        for key in configuration
        if key.startswith(prefix)
    }
    options["_coerce_config"] = True
    options.update(kwargs)
    urls = options.pop("url").split(", ")
    return tuple(create_engine(url, **options) for url in urls)


def create_metadata_for_db(db_name: str) -> MetaData:
    metadata = MetaData()

    models_path = context.config.get_section_option("models_path", db_name) or ""
    models = import_module(models_path)
    declarative_members = (
        member
        for _, member in inspect.getmembers(models)
        if isinstance(member, DeclarativeAttributeIntercept)
    )
    for member in declarative_members:
        member.__table__.tometadata(metadata)  # type: ignore[attr-defined]

    return metadata


# add your model's MetaData objects here
# for 'autogenerate' support.  These must be set
# up to hold just those tables targeting a
# particular database. table.tometadata() may be
# helpful here in case a "copy" of
# a MetaData is needed.
# from myapp import mymodel
# target_metadata = {
#       'engine1':mymodel.metadata1,
#       'engine2':mymodel.metadata2
# }
target_metadata = {
    db_name: create_metadata_for_db(re.sub(r"\d+$", "", db_name))
    for db_name in db_names
}

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # for the --sql use case, run migrations for each URL into
    # individual files.

    engines = {}  # type: ignore[var-annotated]
    for name in db_names:
        engines[name] = rec = {}
        rec["url"] = context.config.get_section_option(name, "sqlalchemy.url")

    for name, rec in engines.items():
        logger.info("Migrating database %s" % name)
        file_ = "%s.sql" % name
        logger.info("Writing output to %s" % file_)
        urls = rec["url"].split(", ")  # type: ignore[union-attr]
        with open(file_, "w") as buffer:
            for url in urls:
                context.configure(
                    url=url,
                    output_buffer=buffer,
                    target_metadata=target_metadata.get(name),
                    literal_binds=True,
                    dialect_opts={"paramstyle": "named"},
                )
                with context.begin_transaction():
                    context.run_migrations(engine_name=name)


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    common_db_url = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['common_dbname']}"
    sequence_db_url = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['sequence_dbname']}"
    shard_db_url = ", ".join(
        f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['shard_dbname_prefix']}{i}"
        for i in range(DB_SHARD_COUNT)
    )

    config.set_section_option("common", "common_db_url", common_db_url)
    config.set_section_option("sequence", "sequence_db_url", sequence_db_url)
    config.set_section_option("shard", "shard_db_url", shard_db_url)

    # for the direct-to-DB use case, start a transaction on all
    # engines, then run all migrations, then commit all transactions.

    engines = {}  # type: ignore[var-annotated]
    for db_name in re.split(r",\s*", databases):
        es = engines_from_config(
            context.config.get_section(db_name, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
        for i, e in enumerate(es):
            engines[f"{db_name}{i if db_name == 'shard' else ''}"] = rec = {}
            rec["engine"] = e

    for name, rec in engines.items():
        engine = rec["engine"]
        rec["connection"] = conn = engine.connect()  # type: ignore[assignment]

        if USE_TWOPHASE:
            rec["transaction"] = conn.begin_twophase()  # type: ignore[assignment]
        else:
            rec["transaction"] = conn.begin()  # type: ignore[assignment]

    try:
        for name, rec in engines.items():
            logger.info("Migrating database %s" % name)
            context.configure(
                connection=rec["connection"],  # type: ignore[arg-type]
                upgrade_token="%s_upgrades" % name,
                downgrade_token="%s_downgrades" % name,
                target_metadata=target_metadata.get(name),
            )
            context.run_migrations(engine_name=name)

        if USE_TWOPHASE:
            for rec in engines.values():
                rec["transaction"].prepare()  # type: ignore[attr-defined]

        for rec in engines.values():
            rec["transaction"].commit()  # type: ignore[attr-defined]
    except:  # noqa: E722
        for rec in engines.values():
            rec["transaction"].rollback()  # type: ignore[attr-defined]
        raise
    finally:
        for rec in engines.values():
            rec["connection"].close()  # type: ignore[attr-defined]


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
