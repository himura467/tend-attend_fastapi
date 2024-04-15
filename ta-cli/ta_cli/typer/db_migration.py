import asyncio

import typer
from ta_core.sqlalchemy.migrate_db import reset_db

app = typer.Typer()


@app.command("migrate")
def migrate() -> None:
    asyncio.run(reset_db())
