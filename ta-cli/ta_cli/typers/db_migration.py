import asyncio

import typer
from ta_core.infrastructure.sqlalchemy.migrate_db import generate_ddl, reset_db_async

app = typer.Typer()


@app.command("print-ddl")
def print_ddl() -> None:
    for ddl_statement in generate_ddl():
        print(ddl_statement)


@app.command("migrate")
def migrate() -> None:
    asyncio.run(reset_db_async())
