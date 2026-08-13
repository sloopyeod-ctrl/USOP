from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class TrustedExternalPrincipal:
    """
    Provider-neutral representation of an already-authenticated caller.

    SECURITY BOUNDARY:
    Instances of this type must only be created after a provider-specific
    authentication adapter has cryptographically validated the inbound
    credential/token and extracted its authoritative claims.

    This object does not validate signatures, issuers, audiences, expiry,
    nonce, or token freshness by itself.
    """

    identity_provider: str
    external_tenant_id: str
    external_subject_id: str
    issuer: str | None = None
    authenticated_at: datetime | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "identity_provider",
            self._normalize_provider(self.identity_provider),
        )
        object.__setattr__(
            self,
            "external_tenant_id",
            self._required(
                self.external_tenant_id,
                "external_tenant_id",
            ),
        )
        object.__setattr__(
            self,
            "external_subject_id",
            self._required(
                self.external_subject_id,
                "external_subject_id",
            ),
        )

        if self.issuer is not None:
            object.__setattr__(
                self,
                "issuer",
                self._required(
                    self.issuer,
                    "issuer",
                ),
            )

        if self.authenticated_at is not None:
            value = self.authenticated_at
            if value.tzinfo is None:
                value = value.replace(tzinfo=UTC)
            else:
                value = value.astimezone(UTC)

            object.__setattr__(
                self,
                "authenticated_at",
                value,
            )

    @staticmethod
    def _required(
        value: str,
        field_name: str,
    ) -> str:
        normalized = str(value or "").strip()
        if not normalized:
            raise ValueError(f"{field_name} is required.")
        return normalized

    @classmethod
    def _normalize_provider(
        cls,
        value: str,
    ) -> str:
        normalized = cls._required(
            value,
            "identity_provider",
        ).lower()

        allowed = set(
            "abcdefghijklmnopqrstuvwxyz0123456789-"
        )

        if (
            any(character not in allowed for character in normalized)
            or normalized.startswith("-")
            or normalized.endswith("-")
            or "--" in normalized
        ):
            raise ValueError(
                "identity_provider must be a canonical "
                "lowercase provider identifier."
            )

        return normalized
