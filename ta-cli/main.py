from asyncio.proactor_events import _ProactorBasePipeTransport
from functools import wraps

import typer
from rich.console import Console

from ta_cli.typers import db_migration


def silence_event_loop_closed(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RuntimeError as e:
            if str(e) != "Event loop is closed":
                raise

    return wrapper


_ProactorBasePipeTransport.__del__ = silence_event_loop_closed(
    _ProactorBasePipeTransport.__del__
)

app = typer.Typer()

app.add_typer(db_migration.app, name="db-migration")

error_console = Console(stderr=True)

if __name__ == "__main__":
    app()
