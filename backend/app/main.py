from fastapi import FastAPI

from app.api.router import router
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(
    title=settings.app_name,
    description="Unified Security Operations Platform",
    version=settings.app_version,
)

app.include_router(router)