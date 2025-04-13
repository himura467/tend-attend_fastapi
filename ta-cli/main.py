from asyncio.proactor_events import _ProactorBasePipeTransport
from functools import wraps
from typing import Any, Callable

import typer
from rich.console import Console

from ta_cli.typers import db_migration, db_mock


def silence_event_loop_closed(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        try:
            return func(self, *args, **kwargs)
        except RuntimeError as e:
            if str(e) != "Event loop is closed":
                raise

    return wrapper


_ProactorBasePipeTransport.__del__ = silence_event_loop_closed(_ProactorBasePipeTransport.__del__)  # type: ignore[method-assign]

app = typer.Typer()

app.add_typer(db_migration.app, name="db-migration")
app.add_typer(db_mock.app, name="db-mock")

error_console = Console(stderr=True)

if __name__ == "__main__":
    app()
