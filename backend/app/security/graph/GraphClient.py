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

    def get_collection(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        max_pages: int = 1000,
    ) -> list[dict[str, Any]]:
        # Retrieve a complete validated Microsoft Graph collection.
        if max_pages < 1:
            raise ValueError(
                "Microsoft Graph max_pages must be at least 1."
            )

        payload = self.get(
            endpoint=endpoint,
            params=params,
        )

        records: list[dict[str, Any]] = []
        visited_next_links: set[str] = set()
        page_count = 0

        while True:
            page_count += 1

            if page_count > max_pages:
                raise ValueError(
                    "Microsoft Graph collection exceeded the "
                    "configured page limit."
                )

            page_records = payload.get("value")

            if not isinstance(page_records, list):
                raise ValueError(
                    "Microsoft Graph collection response did not "
                    "contain a valid value collection."
                )

            if not all(
                isinstance(record, dict)
                for record in page_records
            ):
                raise ValueError(
                    "Microsoft Graph collection contained a "
                    "non-object record."
                )

            records.extend(page_records)

            next_link = payload.get("@odata.nextLink")

            if next_link is None:
                return records

            if (
                not isinstance(next_link, str)
                or not next_link.strip()
            ):
                raise ValueError(
                    "Microsoft Graph collection returned an invalid "
                    "@odata.nextLink."
                )

            next_link = next_link.strip()

            if next_link in visited_next_links:
                raise ValueError(
                    "Microsoft Graph collection returned a repeated "
                    "@odata.nextLink."
                )

            visited_next_links.add(next_link)

            payload = self._get_continuation_page(
                next_link
            )

    def _get_continuation_page(
        self,
        next_link: str,
    ) -> dict[str, Any]:
        from urllib.parse import urlparse

        parsed = urlparse(next_link)

        if parsed.scheme.lower() != "https":
            raise ValueError(
                "Microsoft Graph continuation URL must use HTTPS."
            )

        if parsed.hostname != "graph.microsoft.com":
            raise ValueError(
                "Microsoft Graph continuation URL used an "
                "unexpected host."
            )

        if parsed.port not in (None, 443):
            raise ValueError(
                "Microsoft Graph continuation URL used an "
                "unexpected port."
            )

        if not parsed.path.startswith("/v1.0/"):
            raise ValueError(
                "Microsoft Graph continuation URL must remain "
                "within the v1.0 API boundary."
            )

        token = self.auth_service.get_token()

        response = httpx.get(
            next_link,
            headers={
                **token.authorization_header(),
                "Accept": "application/json",
            },
            timeout=self.timeout_seconds,
        )

        response.raise_for_status()

        payload = response.json()

        if not isinstance(payload, dict):
            raise ValueError(
                "Microsoft Graph returned an unexpected "
                "continuation response format."
            )

        return payload
