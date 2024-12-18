import asyncio

import typer
from ta_core.aws.aurora import execute
from ta_core.constants.constants import AURORA_DATABASE_NAME
from ta_core.infrastructure.sqlalchemy.migrate_db import generate_ddl, reset_db_async

app = typer.Typer()


@app.command("migrate")
def migrate() -> None:
    asyncio.run(reset_db_async())


@app.command("migrate-aurora")
def migrate_aurora() -> None:
    execute(
        query=f"CREATE DATABASE IF NOT EXISTS {AURORA_DATABASE_NAME}", dbname="mysql"
    )
    for ddl_statement in generate_ddl():
        execute(query=ddl_statement, dbname=AURORA_DATABASE_NAME)
