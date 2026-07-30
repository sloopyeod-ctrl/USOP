from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ProviderDescriptor:
    """
    Immutable description of one connector provider.

    A descriptor defines what a provider is and what it can supply.

    It intentionally excludes:

    - credentials
    - secrets
    - customer configuration
    - runtime health
    - synchronization history
    - licensing decisions
    - enablement state

    Those concerns belong to separate platform capabilities.
    """

    provider_name: str
    display_name: str
    vendor: str
    component_version: str
    intelligence_domains: tuple[str, ...]
    capabilities: tuple[str, ...]
    supported_modes: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "provider_name",
            self._normalize_identifier(
                self.provider_name,
                field_name="provider_name",
            ),
        )

        object.__setattr__(
            self,
            "display_name",
            self._require_text(
                self.display_name,
                field_name="display_name",
            ),
        )

        object.__setattr__(
            self,
            "vendor",
            self._require_text(
                self.vendor,
                field_name="vendor",
            ),
        )

        object.__setattr__(
            self,
            "component_version",
            self._require_text(
                self.component_version,
                field_name="component_version",
            ),
        )

        object.__setattr__(
            self,
            "intelligence_domains",
            self._normalize_values(
                self.intelligence_domains,
                field_name="intelligence_domains",
            ),
        )

        object.__setattr__(
            self,
            "capabilities",
            self._normalize_values(
                self.capabilities,
                field_name="capabilities",
            ),
        )

        object.__setattr__(
            self,
            "supported_modes",
            self._normalize_values(
                self.supported_modes,
                field_name="supported_modes",
            ),
        )

    @staticmethod
    def _require_text(
        value: str,
        *,
        field_name: str,
    ) -> str:
        normalized = str(
            value or ""
        ).strip()

        if not normalized:
            raise ValueError(
                f"{field_name} must not be empty."
            )

        return normalized

    @classmethod
    def _normalize_identifier(
        cls,
        value: str,
        *,
        field_name: str,
    ) -> str:
        normalized = cls._require_text(
            value,
            field_name=field_name,
        ).lower()

        if normalized != value.strip():
            raise ValueError(
                f"{field_name} must use its canonical lowercase form."
            )

        allowed_characters = set(
            "abcdefghijklmnopqrstuvwxyz0123456789-"
        )

        if any(
            character not in allowed_characters
            for character in normalized
        ):
            raise ValueError(
                f"{field_name} contains unsupported characters."
            )

        if (
            normalized.startswith("-")
            or normalized.endswith("-")
            or "--" in normalized
        ):
            raise ValueError(
                f"{field_name} is not a valid canonical identifier."
            )

        return normalized

    @classmethod
    def _normalize_values(
        cls,
        values: Iterable[str],
        *,
        field_name: str,
    ) -> tuple[str, ...]:
        normalized_values = {
            cls._require_text(
                value,
                field_name=field_name,
            )
            for value in values
        }

        if not normalized_values:
            raise ValueError(
                f"{field_name} must contain at least one value."
            )

        return tuple(
            sorted(normalized_values)
        )

    def supports_domain(
        self,
        intelligence_domain: str,
    ) -> bool:
        normalized_domain = self._require_text(
            intelligence_domain,
            field_name="intelligence_domain",
        )

        return (
            normalized_domain
            in self.intelligence_domains
        )

    def supports_capability(
        self,
        capability: str,
    ) -> bool:
        normalized_capability = self._require_text(
            capability,
            field_name="capability",
        )

        return normalized_capability in self.capabilities

    def supports_mode(
        self,
        mode: str,
    ) -> bool:
        normalized_mode = self._require_text(
            mode,
            field_name="mode",
        )

        return normalized_mode in self.supported_modes

    def to_dict(self) -> dict[str, object]:
        return {
            "provider_name": self.provider_name,
            "display_name": self.display_name,
            "vendor": self.vendor,
            "component_version": self.component_version,
            "intelligence_domains": list(
                self.intelligence_domains
            ),
            "capabilities": list(
                self.capabilities
            ),
            "supported_modes": list(
                self.supported_modes
            ),
        }