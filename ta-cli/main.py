import typer
from rich.console import Console

app = typer.Typer()

error_console = Console(stderr=True)

if __name__ == "__main__":
    app()
