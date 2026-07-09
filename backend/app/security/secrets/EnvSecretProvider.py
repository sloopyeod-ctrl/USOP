import os

from app.security.secrets.BaseSecretProvider import BaseSecretProvider


class EnvSecretProvider(BaseSecretProvider):
    """
    Secret provider backed by environment variables.

    This provider is intended for local development, Docker Compose, and simple
    deployment scenarios.

    Production deployments may replace this with Keeper Secrets Manager or a
    cloud-native key vault provider.
    """

    def get_secret(self, name: str, default: str | None = None) -> str | None:
        return os.getenv(name, default)