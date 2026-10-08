"""Bring the database schema up to date (alembic upgrade head) from inside the app."""
from pathlib import Path

from alembic import command
from alembic.config import Config

BACKEND_DIR = Path(__file__).resolve().parent.parent


def alembic_config() -> Config:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    cfg.attributes["configure_logger"] = False      # keep uvicorn's logging setup
    return cfg


def upgrade_database() -> None:
    command.upgrade(alembic_config(), "head")


if __name__ == "__main__":
    upgrade_database()
