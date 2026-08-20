from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import jwt
from jwt import PyJWKClient

from app.security.auth.AuthenticationAdapter import (
    AuthenticationAdapter,
)
from app.security.auth.EntraOidcValidationConfig import (
    EntraOidcValidationConfig,
)
from app.services.trusted_external_principal import (
    TrustedExternalPrincipal,
)


class EntraOidcAuthenticationError(ValueError):
    """Fail-closed Microsoft Entra token validation error."""


class EntraOidcAuthenticationAdapter(AuthenticationAdapter):
    """
    Validate a Microsoft Entra v2 access token intended for the USOP API.

    This adapter owns cryptographic authentication only. It does not select
    an Organization, resolve a PlatformUser, or grant USOP authorization.
    """

    PROVIDER_NAME = "microsoft-entra"

    @property
    def provider_name(self) -> str:
        return self.PROVIDER_NAME

    ALGORITHMS = ("RS256",)
    REQUIRED_CLAIMS = (
        "aud",
        "exp",
        "iat",
        "iss",
        "nbf",
        "oid",
        "tid",
        "ver",
    )

    def __init__(
        self,
        config: EntraOidcValidationConfig,
        *,
        jwk_client: PyJWKClient | None = None,
    ):
        self.config = config
        self.jwk_client = (
            jwk_client
            or PyJWKClient(
                config.jwks_uri,
                cache_keys=True,
            )
        )

    @staticmethod
    def _required_text(
        payload: dict[str, Any],
        claim_name: str,
    ) -> str:
        value = str(payload.get(claim_name) or "").strip()
        if not value:
            raise EntraOidcAuthenticationError(
                f"Required claim missing: {claim_name}"
            )
        return value

    def authenticate(
        self,
        token: str,
        *,
        now: datetime | None = None,
    ) -> TrustedExternalPrincipal:
        token = str(token or "").strip()
        if not token:
            raise EntraOidcAuthenticationError(
                "Bearer token is required."
            )

        try:
            header = jwt.get_unverified_header(token)
        except jwt.PyJWTError as exc:
            raise EntraOidcAuthenticationError(
                "Token header is invalid."
            ) from exc

        algorithm = str(header.get("alg") or "")
        if algorithm not in self.ALGORITHMS:
            raise EntraOidcAuthenticationError(
                "Token signing algorithm is not allowed."
            )

        if not str(header.get("kid") or "").strip():
            raise EntraOidcAuthenticationError(
                "Token signing key identifier is required."
            )

        try:
            signing_key = (
                self.jwk_client.get_signing_key_from_jwt(token)
            )
        except Exception as exc:
            raise EntraOidcAuthenticationError(
                "Token signing key could not be resolved."
            ) from exc

        try:
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=list(self.ALGORITHMS),
                audience=self.config.audience,
                issuer=self.config.issuer,
                options={
                    "require": list(self.REQUIRED_CLAIMS),
                    "verify_signature": True,
                    "verify_aud": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_iss": True,
                    "verify_nbf": True,
                },
            )
        except jwt.PyJWTError as exc:
            raise EntraOidcAuthenticationError(
                "Microsoft Entra access token validation failed."
            ) from exc

        token_version = self._required_text(
            payload,
            "ver",
        )
        if token_version != "2.0":
            raise EntraOidcAuthenticationError(
                "Only Microsoft Entra v2 access tokens are accepted."
            )

        tenant_id = self._required_text(payload, "tid")
        if tenant_id != self.config.tenant_id:
            raise EntraOidcAuthenticationError(
                "Token tenant does not match configured tenant."
            )

        subject_id = self._required_text(payload, "oid")
        issuer = self._required_text(payload, "iss")

        authenticated_at = now or datetime.now(UTC)
        if authenticated_at.tzinfo is None:
            authenticated_at = authenticated_at.replace(tzinfo=UTC)
        else:
            authenticated_at = authenticated_at.astimezone(UTC)

        return TrustedExternalPrincipal(
            identity_provider=self.provider_name,
            external_tenant_id=tenant_id,
            external_subject_id=subject_id,
            issuer=issuer,
            authenticated_at=authenticated_at,
        )
