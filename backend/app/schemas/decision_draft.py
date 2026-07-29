from enum import StrEnum
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.domain import DecisionType
from app.intelligence.drafting import (
    DecisionDraft,
)


class DecisionDraftProfile(StrEnum):
    """
    Stable presentation profile requested by a caller.

    Only the deterministic default profile is currently implemented.
    Additional profiles must receive explicit semantics and regression
    coverage before being added.
    """

    DEFAULT = "default"


class DecisionDraftRequest(BaseModel):
    """
    Request contract for constructing deterministic decision documentation.

    Organization, identity, and recommendation scope come from the API path.
    The caller supplies only the organizational response already selected by
    the analyst and the supported draft profile.

    Evidence selection, confidence, construction version, and draft content
    remain server-controlled.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    decision_type: DecisionType

    draft_profile: DecisionDraftProfile = (
        DecisionDraftProfile.DEFAULT
    )


class DecisionDraftEvidenceRead(BaseModel):
    """
    One authoritative evidence reference supporting draft text.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    source_type: str = Field(
        min_length=1,
        max_length=100,
    )

    source_id: str | None = Field(
        default=None,
        max_length=255,
    )

    label: str = Field(
        min_length=1,
        max_length=255,
    )

    detail: str | None = Field(
        default=None,
        max_length=10000,
    )


class DecisionDraftSegmentRead(BaseModel):
    """
    One explainable unit of deterministic draft text.

    Every segment must retain at least one evidence reference.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    text: str = Field(
        min_length=1,
        max_length=10000,
    )

    evidence: list[
        DecisionDraftEvidenceRead
    ] = Field(
        min_length=1,
    )


class DecisionDraftMetadataRead(BaseModel):
    """
    Transport metadata derived from the completed deterministic draft.

    Counts describe the returned projection only. They do not represent risk,
    policy compliance, decision quality, or analyst approval.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    justification_segment_count: int = Field(
        ge=0,
    )

    notes_segment_count: int = Field(
        ge=0,
    )

    evidence_count: int = Field(
        ge=0,
    )


class DecisionDraftRead(BaseModel):
    """
    Stable API projection of an analyst-reviewable deterministic draft.

    Internal dataclasses, pipeline builders, repositories, and orchestration
    details are intentionally excluded from the public contract.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    decision_type: DecisionType

    draft_profile: DecisionDraftProfile

    suggested_justification: str = Field(
        max_length=50000,
    )

    suggested_notes: str = Field(
        max_length=50000,
    )

    justification_segments: list[
        DecisionDraftSegmentRead
    ]

    notes_segments: list[
        DecisionDraftSegmentRead
    ]

    evidence_used: list[
        DecisionDraftEvidenceRead
    ]

    confidence_score: int = Field(
        ge=0,
        le=100,
    )

    construction_version: str = Field(
        min_length=1,
        max_length=100,
    )

    metadata: DecisionDraftMetadataRead

    @classmethod
    def from_draft(
        cls,
        draft: DecisionDraft,
        *,
        draft_profile: (
            DecisionDraftProfile
            | str
        ) = DecisionDraftProfile.DEFAULT,
    ) -> Self:
        """
        Project one internal DecisionDraft into the stable transport contract.
        """

        projection = draft.to_dict()

        projection[
            "draft_profile"
        ] = draft_profile

        projection["metadata"] = {
            "justification_segment_count": len(
                draft.justification_segments
            ),
            "notes_segment_count": len(
                draft.notes_segments
            ),
            "evidence_count": len(
                draft.evidence_used
            ),
        }

        return cls.model_validate(
            projection
        )
