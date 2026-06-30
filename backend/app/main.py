from fastapi import FastAPI

app = FastAPI(
    title="USOP",
    description="Unified Security Operations Platform",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "application": "USOP",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "version": "0.1.0"
    }


@app.get("/version")
def version():
    return {
        "application": "USOP",
        "version": "0.1.0",
        "architecture": "Engine First"
    }
