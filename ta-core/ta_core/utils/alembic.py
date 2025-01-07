from pathlib import Path

from alembic.config import Config


def get_alembic_config() -> Config:
    alembic_ini_path = Path(__file__).parents[2].joinpath("alembic.ini")
    return Config(alembic_ini_path)
