import os

from app.security.secrets.BaseSecretProvider import BaseSecretProvider
from app.security.secrets.EnvSecretProvider import EnvSecretProvider


class SecretProviderFactory:
    """
    Factory responsible for creating the configured secret provider.

    The provider is selected using:

        USOP_SECRET_PROVIDER

    Supported values:
    - env
    - keeper placeholder
    """

    @staticmethod
    def create() -> BaseSecretProvider:
        provider_name = os.getenv("USOP_SECRET_PROVIDER", "env").lower().strip()

        if provider_name == "env":
            return EnvSecretProvider()

        if provider_name == "keeper":
            raise NotImplementedError(
                "Keeper Secrets Manager provider is planned but not implemented."
            )

        raise ValueError(f"Unsupported secret provider: {provider_name}")