from __future__ import annotations

from abc import ABC, abstractmethod

from app.services.trusted_external_principal import (
    TrustedExternalPrincipal,
)


class AuthenticationAdapter(ABC):
    """
    Provider-neutral contract for authenticating one external caller.

    SECURITY BOUNDARY:

    An AuthenticationAdapter owns provider-specific cryptographic
    authentication only.

    It must not select an Organization, resolve or activate a
    PlatformUser, allocate a Seat, evaluate licensing, grant roles or
    permissions, or perform runtime RBAC authorization.

    Successful authentication returns a TrustedExternalPrincipal.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the canonical provider identifier."""
        raise NotImplementedError

    @abstractmethod
    def authenticate(
        self,
        credential: str,
    ) -> TrustedExternalPrincipal:
        """
        Cryptographically authenticate one provider credential.

        Implementations must fail closed when the credential cannot
        be authenticated.
        """
        raise NotImplementedError
