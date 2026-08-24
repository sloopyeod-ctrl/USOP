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

    # Inbound caller authentication for the USOP API.
    # These are intentionally separate from MS_GRAPH_* connector credentials.
    usop_auth_entra_tenant_id: str | None = None
    usop_auth_entra_audience: str | None = None
    usop_auth_entra_required_scope: str | None = None

    class Config:
        env_file = str(ENV_FILE)
        extra = "ignore"


settings = Settings()

