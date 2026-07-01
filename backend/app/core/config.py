from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "USOP"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True

    database_url: str = "postgresql+psycopg://usop:usop_password@localhost:5432/usop"

    class Config:
        env_file = ".env"


settings = Settings()