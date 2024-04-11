import typer
from rich.console import Console

from ta_cli.typers import db_migration

app = typer.Typer()

app.add_typer(db_migration.app, name="db-migration")

error_console = Console(stderr=True)

if __name__ == "__main__":
    app()
