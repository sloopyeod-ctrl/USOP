from app.core.version import APP_VERSION


def get_health_status() -> dict:
    return {
        "status": "healthy",
        "version": APP_VERSION,
    }


def get_ready_status() -> dict:
    return {
        "status": "ready",
        "services": {
            "api": "ready",
        },
    }