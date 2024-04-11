import typer
from ta_core.db import reset_common_db, reset_sequence_db, reset_shard_db
from ta_core.settings import DB_SHARD_COUNT

from ta_cli.utilities import coro

app = typer.Typer()


@app.command("migrate")
@coro
async def migrate() -> None:
    await reset_common_db()
    await reset_sequence_db()
    for shard_id in range(DB_SHARD_COUNT):
        await reset_shard_db(shard_id)
