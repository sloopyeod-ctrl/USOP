from fastapi import FastAPI

from app.api.router import router
from app.core.config import settings
from app.core.logging import configure_logging
from fastapi.middleware.cors import CORSMiddleware

configure_logging()

app = FastAPI(
    title=settings.app_name,
    description="Unified Security Operations Platform",
    version=settings.app_version,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)