from typing import Any

import httpx

from app.security.auth.MicrosoftGraphAuthService import (
    MicrosoftGraphAuthService,
)


class GraphClient:
    """
    Authenticated HTTP client for Microsoft Graph.

    This client owns:
    - Microsoft Graph base URL handling
    - OAuth authorization headers
    - HTTP request execution
    - response validation

    Providers should use this client instead of implementing authentication
    or HTTP request handling directly.
    """

    GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"

    def __init__(
        self,
        auth_service: MicrosoftGraphAuthService | None = None,
        timeout_seconds: float = 30.0,
    ):
        self.auth_service = auth_service or MicrosoftGraphAuthService()
        self.timeout_seconds = timeout_seconds

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute an authenticated Microsoft Graph GET request.

        Args:
            endpoint:
                Relative Graph endpoint such as "/users".

            params:
                Optional query parameters such as "$top" and "$select".

        Returns:
            Parsed Microsoft Graph JSON response.

        Raises:
            ValueError:
                If the endpoint is invalid or Graph returns a non-object body.

            httpx.HTTPStatusError:
                If Microsoft Graph returns an unsuccessful status code.
        """

        if not endpoint or not endpoint.startswith("/"):
            raise ValueError(
                "Microsoft Graph endpoint must be a relative path "
                "beginning with '/'."
            )

        token = self.auth_service.get_token()

        response = httpx.get(
            f"{self.GRAPH_BASE_URL}{endpoint}",
            headers={
                **token.authorization_header(),
                "Accept": "application/json",
            },
            params=params,
            timeout=self.timeout_seconds,
        )

        response.raise_for_status()

        payload = response.json()

        if not isinstance(payload, dict):
            raise ValueError(
                "Microsoft Graph returned an unexpected response format."
            )

        return payload