from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EntraOidcValidationConfig:
    """
    Tenant-specific configuration for validating Microsoft Entra v2 access
    tokens issued specifically for the USOP API.
    """

    tenant_id: str
    audience: str
    required_scope: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "tenant_id",
            self._required(self.tenant_id, "tenant_id"),
        )
        object.__setattr__(
            self,
            "audience",
            self._required(self.audience, "audience"),
        )
        object.__setattr__(
            self,
            "required_scope",
            self._required(
                self.required_scope,
                "required_scope",
            ),
        )

        if any(
            character.isspace()
            for character in self.required_scope
        ):
            raise ValueError(
                "required_scope must be one delegated scope token."
            )

    @staticmethod
    def _required(value: str, field_name: str) -> str:
        normalized = str(value or "").strip()
        if not normalized:
            raise ValueError(f"{field_name} is required.")
        return normalized

    @property
    def issuer(self) -> str:
        return (
            "https://login.microsoftonline.com/"
            f"{self.tenant_id}/v2.0"
        )

    @property
    def jwks_uri(self) -> str:
        return (
            "https://login.microsoftonline.com/"
            f"{self.tenant_id}/discovery/v2.0/keys"
        )
