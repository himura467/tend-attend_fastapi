import asyncio

import typer
from ta_core.infrastructure.sqlalchemy.migrate_db import reset_db_async, generate_ddl
from ta_core.aws.aurora import execute

app = typer.Typer()


@app.command("migrate")
def migrate() -> None:
    asyncio.run(reset_db_async())


@app.command("migrate-aurora")
def migrate_aurora() -> None:
    for ddl_statement in generate_ddl():
        execute(ddl_statement)
