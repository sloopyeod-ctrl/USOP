from datetime import datetime

from pydantic import BaseModel, Field


class DecisionPatternRead(BaseModel):
    """
    Stable API projection of organizational decision patterns.

    This schema represents factual organizational observations produced by
    the Decision Pattern Intelligence pipeline. It intentionally contains no
    policy interpretation, recommendations, or enforcement directives.
    """

    pattern_type: str = Field(
        min_length=1,
        max_length=100,
    )

    title: str = Field(
        min_length=1,
        max_length=255,
    )

    summary: str = Field(
        min_length=1,
        max_length=4000,
    )

    scope: str = Field(
        min_length=1,
        max_length=100,
    )

    metrics: dict

    first_seen_at: datetime | None = None

    last_seen_at: datetime | None = None

    evidence_record_ids: list[str]
