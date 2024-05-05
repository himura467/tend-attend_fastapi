import asyncio

import typer
from ta_core.infrastructure.sqlalchemy.migrate_db import reset_db_async

app = typer.Typer()


@app.command("migrate")
def migrate() -> None:
    asyncio.run(reset_db_async())
