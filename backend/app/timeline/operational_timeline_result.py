from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from app.timeline.timeline_event import (
    TimelineEvent,
)


class TimelineContributorDiagnostic(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    contributor_name: str
    contributor_version: str
    status: Literal[
        "Succeeded",
        "Failed",
        "Skipped",
        "Unavailable",
    ]
    event_count: int = 0
    message: str | None = None

    @field_validator(
        "contributor_name",
        "contributor_version",
    )
    @classmethod
    def validate_required_text(
        cls,
        value: str,
        info,
    ) -> str:
        normalized = str(value or "").strip()

        if not normalized:
            raise ValueError(
                f"{info.field_name} must not be empty."
            )

        return normalized

    @field_validator("event_count")
    @classmethod
    def validate_event_count(
        cls,
        value: int,
    ) -> int:
        if value < 0:
            raise ValueError(
                "event_count must not be negative."
            )

        return value


class OperationalTimelineResult(BaseModel):
    """
    Canonical result returned by the Operational Timeline Engine.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    organization_id: str
    events: tuple[
        TimelineEvent,
        ...,
    ] = Field(default_factory=tuple)

    contributor_diagnostics: tuple[
        TimelineContributorDiagnostic,
        ...,
    ] = Field(default_factory=tuple)

    warnings: tuple[str, ...] = Field(
        default_factory=tuple
    )
    is_partial: bool = False
    next_cursor: str | None = None
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(
            UTC
        )
    )
    schema_version: int = 1

    @field_validator("organization_id")
    @classmethod
    def validate_organization_id(
        cls,
        value: str,
    ) -> str:
        normalized = str(value or "").strip()

        if not normalized:
            raise ValueError(
                "organization_id must not be empty."
            )

        return normalized

    @field_validator("generated_at")
    @classmethod
    def normalize_generated_at(
        cls,
        value: datetime,
    ) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)

        return value.astimezone(UTC)
