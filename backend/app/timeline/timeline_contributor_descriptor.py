from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.timeline.timeline_category import (
    TimelineCategory,
)


@dataclass(frozen=True)
class TimelineContributorDescriptor:
    """
    Immutable description of one timeline contributor.

    Runtime health, licensing, customer configuration, credentials, and
    activation state intentionally remain outside this descriptor.
    """

    contributor_name: str
    display_name: str
    component_version: str
    categories: tuple[
        TimelineCategory,
        ...,
    ]
    priority: int = 100
    extension_id: str | None = None
    requires_license: bool = False
    schema_versions_supported: tuple[
        int,
        ...,
    ] = (1,)

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "contributor_name",
            self._normalize_identifier(
                self.contributor_name,
                field_name="contributor_name",
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
            "component_version",
            self._require_text(
                self.component_version,
                field_name="component_version",
            ),
        )

        object.__setattr__(
            self,
            "categories",
            self._normalize_categories(
                self.categories
            ),
        )

        if not isinstance(
            self.priority,
            int,
        ):
            raise ValueError(
                "priority must be an integer."
            )

        normalized_extension_id = (
            None
            if self.extension_id is None
            else self._normalize_identifier(
                self.extension_id,
                field_name="extension_id",
            )
        )

        object.__setattr__(
            self,
            "extension_id",
            normalized_extension_id,
        )

        versions = tuple(
            sorted(
                {
                    int(version)
                    for version
                    in self.schema_versions_supported
                }
            )
        )

        if (
            not versions
            or any(
                version < 1
                for version in versions
            )
        ):
            raise ValueError(
                "schema_versions_supported must contain "
                "positive integers."
            )

        object.__setattr__(
            self,
            "schema_versions_supported",
            versions,
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

        allowed = set(
            "abcdefghijklmnopqrstuvwxyz0123456789-"
        )

        if any(
            character not in allowed
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

    @staticmethod
    def _normalize_categories(
        values: Iterable[
            TimelineCategory
        ],
    ) -> tuple[
        TimelineCategory,
        ...,
    ]:
        normalized = {
            (
                value
                if isinstance(
                    value,
                    TimelineCategory,
                )
                else TimelineCategory(value)
            )
            for value in values
        }

        if not normalized:
            raise ValueError(
                "categories must contain at least one value."
            )

        return tuple(
            sorted(
                normalized,
                key=lambda item: item.value,
            )
        )

    def supports_category(
        self,
        category: TimelineCategory,
    ) -> bool:
        normalized = (
            category
            if isinstance(
                category,
                TimelineCategory,
            )
            else TimelineCategory(category)
        )

        return normalized in self.categories

    def supports_schema_version(
        self,
        schema_version: int,
    ) -> bool:
        return (
            schema_version
            in self.schema_versions_supported
        )

    def to_dict(
        self,
    ) -> dict[str, object]:
        return {
            "contributor_name": (
                self.contributor_name
            ),
            "display_name": self.display_name,
            "component_version": (
                self.component_version
            ),
            "categories": [
                category.value
                for category in self.categories
            ],
            "priority": self.priority,
            "extension_id": self.extension_id,
            "requires_license": (
                self.requires_license
            ),
            "schema_versions_supported": list(
                self.schema_versions_supported
            ),
        }
