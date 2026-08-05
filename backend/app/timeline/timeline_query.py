from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.timeline.timeline_category import (
    TimelineCategory,
)
from app.timeline.timeline_event import (
    TimelineSubjectReference,
)
from app.timeline.timeline_visibility import (
    TimelineVisibility,
)


class TimelineQuery(BaseModel):
    """
    Provider-neutral request for operational history.

    Organization scope is mandatory.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    organization_id: str

    subject_references: tuple[
        TimelineSubjectReference,
        ...,
    ] = Field(default_factory=tuple)

    identity_id: str | None = None
    work_item_id: str | None = None
    decision_id: str | None = None
    correlation_id: str | None = None

    categories: frozenset[
        TimelineCategory
    ] = Field(default_factory=frozenset)

    visibility_levels: frozenset[
        TimelineVisibility
    ] = Field(default_factory=frozenset)

    start_at: datetime | None = None
    end_at: datetime | None = None

    cursor: str | None = None
    limit: int = 100
    sort_direction: Literal[
        "ascending",
        "descending",
    ] = "descending"

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

    @field_validator(
        "identity_id",
        "work_item_id",
        "decision_id",
        "correlation_id",
        "cursor",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return str(value).strip() or None

    @field_validator(
        "start_at",
        "end_at",
    )
    @classmethod
    def normalize_timestamp(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        if value is None:
            return None

        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)

        return value.astimezone(UTC)

    @field_validator("limit")
    @classmethod
    def validate_limit(
        cls,
        value: int,
    ) -> int:
        if value < 1 or value > 500:
            raise ValueError(
                "limit must be from 1 through 500."
            )

        return value

    @model_validator(mode="after")
    def validate_time_range(
        self,
    ):
        if (
            self.start_at is not None
            and self.end_at is not None
            and self.start_at > self.end_at
        ):
            raise ValueError(
                "start_at must not be after end_at."
            )

        return self
