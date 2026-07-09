from abc import ABC, abstractmethod


class BaseSecretProvider(ABC):
    """
    Base contract for USOP secret providers.

    Secret providers retrieve sensitive values from an external source without
    requiring application code to know where secrets are stored.

    Examples:
    - environment variables
    - Docker Compose environment
    - Keeper Secrets Manager
    - cloud key vaults
    """

    @abstractmethod
    def get_secret(self, name: str, default: str | None = None) -> str | None:
        """
        Retrieve a secret value by name.
        """
        raise NotImplementedError