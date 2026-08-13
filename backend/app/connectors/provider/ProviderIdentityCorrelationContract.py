from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderIdentityCorrelationContract:
    """Immutable provider-owned identity-correlation metadata."""

    provider_name: str
    account_source_system: str
    subject_semantics: str
    tenant_semantics: str
    supports_deterministic_subject_match: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "provider_name",
            self._normalize_provider_name(self.provider_name),
        )
        for field_name in (
            "account_source_system",
            "subject_semantics",
            "tenant_semantics",
        ):
            object.__setattr__(
                self,
                field_name,
                self._require_text(
                    getattr(self, field_name),
                    field_name=field_name,
                ),
            )

    @staticmethod
    def _require_text(value: str, *, field_name: str) -> str:
        normalized = str(value or "").strip()
        if not normalized:
            raise ValueError(f"{field_name} must not be empty.")
        return normalized

    @classmethod
    def _normalize_provider_name(cls, value: str) -> str:
        normalized = cls._require_text(
            value,
            field_name="provider_name",
        ).lower()
        allowed = set("abcdefghijklmnopqrstuvwxyz0123456789-")
        if (
            any(character not in allowed for character in normalized)
            or normalized.startswith("-")
            or normalized.endswith("-")
            or "--" in normalized
        ):
            raise ValueError(
                "provider_name must be a canonical lowercase identifier."
            )
        return normalized

    def to_dict(self) -> dict[str, object]:
        return {
            "provider_name": self.provider_name,
            "account_source_system": self.account_source_system,
            "subject_semantics": self.subject_semantics,
            "tenant_semantics": self.tenant_semantics,
            "supports_deterministic_subject_match": (
                self.supports_deterministic_subject_match
            ),
        }
