from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from app.security.auth.GraphToken import GraphToken
from app.security.secrets.SecretProviderFactory import SecretProviderFactory


class MicrosoftGraphAuthService:
    """
    Handles Microsoft Graph OAuth authentication.

    Uses the OAuth 2.0 client credentials flow with a Microsoft Entra
    application registration.

    Secrets are loaded through the configured USOP secret provider so callers
    do not need to know whether credentials originate from environment
    variables, Keeper Secrets Manager, or a future credential source.
    """

    TOKEN_URL_TEMPLATE = (
        "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    )

    DEFAULT_SCOPE = "https://graph.microsoft.com/.default"

    def __init__(self):
        self.secret_provider = SecretProviderFactory.create()
        self._cached_token: GraphToken | None = None

    def get_required_secret(self, name: str) -> str:
        value = self.secret_provider.get_secret(name)

        if not value:
            raise ValueError(f"Required secret is missing: {name}")

        return value

    def get_token(self) -> GraphToken:
        if self._cached_token and not self._cached_token.is_expired():
            return self._cached_token

        tenant_id = self.get_required_secret("MS_GRAPH_TENANT_ID")
        client_id = self.get_required_secret("MS_GRAPH_CLIENT_ID")
        client_secret = self.get_required_secret("MS_GRAPH_CLIENT_SECRET")

        token_url = self.TOKEN_URL_TEMPLATE.format(tenant_id=tenant_id)

        response = httpx.post(
            token_url,
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": self.DEFAULT_SCOPE,
                "grant_type": "client_credentials",
            },
            timeout=30.0,
        )

        response.raise_for_status()

        payload: dict[str, Any] = response.json()

        access_token = payload.get("access_token")

        if not access_token:
            raise ValueError(
                "Microsoft Entra token response did not include an access token."
            )

        expires_in = int(payload.get("expires_in", 3600))

        # Refresh slightly early to reduce edge-of-expiration failures.
        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=max(expires_in - 60, 60)
        )

        self._cached_token = GraphToken(
            access_token=access_token,
            token_type=payload.get("token_type", "Bearer"),
            expires_at=expires_at,
        )

        return self._cached_token