from __future__ import annotations

from app.connectors.provider.ProviderIdentityCorrelationContract import (
    ProviderIdentityCorrelationContract,
)


class ProviderIdentityCorrelationRegistry:
    """Vendor-neutral catalog of provider-owned correlation contracts."""

    def __init__(self) -> None:
        self._contracts: dict[
            str,
            ProviderIdentityCorrelationContract,
        ] = {}

    def register(
        self,
        contract: ProviderIdentityCorrelationContract,
    ) -> None:
        if contract.provider_name in self._contracts:
            raise ValueError(
                "Identity correlation contract already registered: "
                f"{contract.provider_name}"
            )
        self._contracts[contract.provider_name] = contract

    def get(
        self,
        provider_name: str,
    ) -> ProviderIdentityCorrelationContract | None:
        normalized = str(provider_name or "").strip().lower()
        return self._contracts.get(normalized)

    def provider_names(self) -> tuple[str, ...]:
        return tuple(sorted(self._contracts))


def build_default_identity_correlation_registry(
) -> ProviderIdentityCorrelationRegistry:
    from app.connectors.microsoft.EntraIdentityCorrelation import (
        ENTRA_IDENTITY_CORRELATION_CONTRACT,
    )

    registry = ProviderIdentityCorrelationRegistry()
    registry.register(ENTRA_IDENTITY_CORRELATION_CONTRACT)
    return registry
