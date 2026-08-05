from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from app.timeline.timeline_category import (
    TimelineCategory,
)
from app.timeline.timeline_visibility import (
    TimelineVisibility,
)


def _required_text(
    value: str,
    *,
    field_name: str,
) -> str:
    normalized = str(value or "").strip()

    if not normalized:
        raise ValueError(
            f"{field_name} must not be empty."
        )

    return normalized


class TimelineSubjectReference(BaseModel):
    """
    Provider-neutral reference to one subject related to an event.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    subject_type: str
    subject_id: str
    label: str | None = None

    @field_validator(
        "subject_type",
        "subject_id",
    )
    @classmethod
    def validate_required_text(
        cls,
        value: str,
        info,
    ) -> str:
        return _required_text(
            value,
            field_name=info.field_name,
        )

    @field_validator("label")
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return str(value).strip() or None


class TimelineEvent(BaseModel):
    """
    Derived projection of authoritative operational history.

    This schema never becomes the authoritative owner of that history.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    event_id: str
    occurred_at: datetime
    category: TimelineCategory
    visibility: TimelineVisibility
    title: str
    summary: str | None = None
    actor: str | None = None

    contributor_name: str
    contributor_version: str

    source_type: str
    source_id: str
    organization_id: str

    subject_references: tuple[
        TimelineSubjectReference,
        ...,
    ] = Field(default_factory=tuple)

    correlation_id: str | None = None
    metadata: dict[str, Any] = Field(
        default_factory=dict
    )
    schema_version: int = 1

    @field_validator(
        "event_id",
        "title",
        "contributor_name",
        "contributor_version",
        "source_type",
        "source_id",
        "organization_id",
    )
    @classmethod
    def validate_required_text(
        cls,
        value: str,
        info,
    ) -> str:
        return _required_text(
            value,
            field_name=info.field_name,
        )

    @field_validator(
        "summary",
        "actor",
        "correlation_id",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return str(value).strip() or None

    @field_validator("occurred_at")
    @classmethod
    def normalize_timestamp(
        cls,
        value: datetime,
    ) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)

        return value.astimezone(UTC)

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(
        cls,
        value: int,
    ) -> int:
        if value < 1:
            raise ValueError(
                "schema_version must be at least 1."
            )

        return value

    def canonical_payload(
        self,
    ) -> dict[str, Any]:
        """
        Return deterministic event content for duplicate comparison.
        """

        return self.model_dump(
            mode="json",
            exclude_none=False,
        )
