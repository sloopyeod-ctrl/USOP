from __future__ import annotations

from collections.abc import Callable

from app.security.auth.AuthenticationAdapter import (
    AuthenticationAdapter,
)


AuthenticationAdapterFactory = Callable[
    [],
    AuthenticationAdapter,
]


class AuthenticationProviderRegistry:
    """
    Provider-neutral catalog of authentication adapter factories.

    The registry owns provider discovery and adapter construction.

    It does not own credential validation, Organization selection,
    PlatformUser resolution, invitation activation, authorization,
    runtime RBAC, MFA policy, secrets, or licensing.
    """

    def __init__(self) -> None:
        self._factories: dict[
            str,
            AuthenticationAdapterFactory,
        ] = {}

    def register(
        self,
        provider_name: str,
        factory: AuthenticationAdapterFactory,
    ) -> None:
        normalized_name = self._normalize_provider_name(
            provider_name
        )

        if not normalized_name:
            raise ValueError(
                "Authentication provider name is required."
            )

        if normalized_name in self._factories:
            raise ValueError(
                "Authentication provider already registered: "
                f"{normalized_name}"
            )

        if not callable(factory):
            raise TypeError(
                "Authentication adapter factory must be callable."
            )

        self._factories[normalized_name] = factory

    def unregister(
        self,
        provider_name: str,
    ) -> None:
        normalized_name = self._normalize_provider_name(
            provider_name
        )
        self._factories.pop(normalized_name, None)

    def provider_names(self) -> tuple[str, ...]:
        return tuple(sorted(self._factories))

    def create(
        self,
        provider_name: str,
    ) -> AuthenticationAdapter | None:
        normalized_name = self._normalize_provider_name(
            provider_name
        )

        factory = self._factories.get(normalized_name)

        if factory is None:
            return None

        adapter = factory()

        if not isinstance(adapter, AuthenticationAdapter):
            raise TypeError(
                "Authentication provider factory returned an "
                "object that does not implement "
                "AuthenticationAdapter."
            )

        adapter_provider_name = self._normalize_provider_name(
            adapter.provider_name
        )

        if adapter_provider_name != normalized_name:
            raise ValueError(
                "Authentication adapter provider name does not "
                "match its registry entry."
            )

        return adapter

    @staticmethod
    def _normalize_provider_name(
        provider_name: str,
    ) -> str:
        normalized = str(
            provider_name or ""
        ).strip().lower()

        if not normalized:
            return ""

        allowed = set(
            "abcdefghijklmnopqrstuvwxyz0123456789-"
        )

        if (
            any(
                character not in allowed
                for character in normalized
            )
            or normalized.startswith("-")
            or normalized.endswith("-")
            or "--" in normalized
        ):
            raise ValueError(
                "Authentication provider name must be a "
                "canonical lowercase provider identifier."
            )

        return normalized
