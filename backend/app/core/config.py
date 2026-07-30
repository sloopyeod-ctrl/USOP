from app.core.version import APP_VERSION

from pathlib import Path

from pydantic_settings import BaseSettings


BACKEND_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_ROOT / ".env"


class Settings(BaseSettings):
    app_name: str = "USOP"
    app_version: str = APP_VERSION
    environment: str = "development"
    debug: bool = True

    database_url: str = (
        "postgresql+psycopg://"
        "usop:usop_password@localhost:5432/usop"
    )

    class Config:
        env_file = str(ENV_FILE)
        extra = "ignore"


settings = Settings()

