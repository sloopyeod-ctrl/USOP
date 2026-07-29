import pytest
from pydantic import ValidationError

from app.domain import DecisionType
from app.intelligence.drafting import (
    DecisionDraft,
    DecisionDraftEvidence,
    DecisionDraftSegment,
)
from app.schemas.decision_draft import (
    DecisionDraftEvidenceRead,
    DecisionDraftMetadataRead,
    DecisionDraftProfile,
    DecisionDraftRead,
    DecisionDraftRequest,
    DecisionDraftSegmentRead,
)


def evidence(
    *,
    source_type="Recommendation",
    source_id="recommendation-001",
    label="Remove privileged access",
    detail=(
        "Remove unnecessary privileged "
        "authorization."
    ),
):
    return DecisionDraftEvidence(
        source_type=source_type,
        source_id=source_id,
        label=label,
        detail=detail,
    )


def draft() -> DecisionDraft:
    recommendation = evidence()

    guidance = evidence(
        source_type=(
            "OrganizationGuidance"
        ),
        source_id="knowledge-001",
        label=(
            "Privileged access standard"
        ),
        detail=(
            "Privileged assignments require "
            "explicit review."
        ),
    )

    justification = (
        DecisionDraftSegment(
            text=(
                "The selected organizational "
                "response addresses the "
                "recommendation."
            ),
            evidence=(
                recommendation,
            ),
        ),
        DecisionDraftSegment(
            text=(
                "Linked organizational guidance "
                "was available for analyst "
                "review."
            ),
            evidence=(
                guidance,
                recommendation,
            ),
        ),
    )

    notes = (
        DecisionDraftSegment(
            text=(
                "Record remediation details "
                "before submission."
            ),
            evidence=(
                recommendation,
            ),
        ),
    )

    return DecisionDraft(
        decision_type="CorrectRisk",
        justification_segments=(
            justification
        ),
        notes_segments=notes,
        confidence_score=85,
    )


def test_request_accepts_canonical_decision_type():
    request = DecisionDraftRequest(
        decision_type=(
            DecisionType.CORRECT_RISK
        )
    )

    assert request.decision_type == (
        DecisionType.CORRECT_RISK
    )

    assert request.draft_profile == (
        DecisionDraftProfile.DEFAULT
    )


def test_request_accepts_explicit_default_profile():
    request = (
        DecisionDraftRequest.model_validate(
            {
                "decision_type": (
                    "AcceptRisk"
                ),
                "draft_profile": "default",
            }
        )
    )

    assert request.decision_type == (
        DecisionType.ACCEPT_RISK
    )

    assert request.draft_profile == (
        DecisionDraftProfile.DEFAULT
    )


def test_request_rejects_unknown_decision_type():
    with pytest.raises(
        ValidationError,
    ):
        DecisionDraftRequest(
            decision_type=(
                "InventedDecision"
            )
        )


def test_request_rejects_unknown_profile():
    with pytest.raises(
        ValidationError,
    ):
        DecisionDraftRequest(
            decision_type=(
                DecisionType.CORRECT_RISK
            ),
            draft_profile="executive",
        )


def test_request_forbids_server_controlled_fields():
    prohibited_fields = {
        "organization_id": (
            "organization-001"
        ),
        "identity_id": "identity-001",
        "recommendation_id": (
            "recommendation-001"
        ),
        "confidence_score": 100,
        "suggested_justification": (
            "Caller-supplied draft text."
        ),
        "construction_version": (
            "caller-version"
        ),
        "options": {},
    }

    for field_name, value in (
        prohibited_fields.items()
    ):
        with pytest.raises(
            ValidationError,
        ):
            DecisionDraftRequest.model_validate(
                {
                    "decision_type": (
                        "CorrectRisk"
                    ),
                    field_name: value,
                }
            )


def test_evidence_schema_requires_source_type():
    with pytest.raises(
        ValidationError,
    ):
        DecisionDraftEvidenceRead(
            source_type="",
            source_id=None,
            label="Recommendation",
        )


def test_segment_schema_requires_evidence():
    with pytest.raises(
        ValidationError,
    ):
        DecisionDraftSegmentRead(
            text=(
                "Unsupported draft sentence."
            ),
            evidence=[],
        )


def test_metadata_rejects_negative_counts():
    with pytest.raises(
        ValidationError,
    ):
        DecisionDraftMetadataRead(
            justification_segment_count=-1,
            notes_segment_count=0,
            evidence_count=0,
        )


def test_read_projects_internal_draft():
    result = DecisionDraftRead.from_draft(
        draft()
    )

    assert result.decision_type == (
        DecisionType.CORRECT_RISK
    )

    assert result.draft_profile == (
        DecisionDraftProfile.DEFAULT
    )

    assert result.suggested_justification == (
        "The selected organizational "
        "response addresses the "
        "recommendation. Linked "
        "organizational guidance was "
        "available for analyst review."
    )

    assert result.suggested_notes == (
        "Record remediation details "
        "before submission."
    )

    assert len(
        result.justification_segments
    ) == 2

    assert len(
        result.notes_segments
    ) == 1

    assert len(
        result.evidence_used
    ) == 2

    assert result.confidence_score == 85

    assert (
        result.construction_version
        == "decision-draft-v1"
    )

    assert (
        result.metadata
        .justification_segment_count
        == 2
    )

    assert (
        result.metadata
        .notes_segment_count
        == 1
    )

    assert (
        result.metadata.evidence_count
        == 2
    )


def test_read_preserves_evidence_deduplication():
    result = DecisionDraftRead.from_draft(
        draft()
    )

    assert [
        item.source_type
        for item in result.evidence_used
    ] == [
        "Recommendation",
        "OrganizationGuidance",
    ]


def test_read_accepts_supported_profile_string():
    result = DecisionDraftRead.from_draft(
        draft(),
        draft_profile="default",
    )

    assert result.draft_profile == (
        DecisionDraftProfile.DEFAULT
    )


def test_read_dump_is_transport_safe():
    payload = (
        DecisionDraftRead
        .from_draft(
            draft()
        )
        .model_dump(
            mode="json"
        )
    )

    assert payload[
        "decision_type"
    ] == "CorrectRisk"

    assert payload[
        "draft_profile"
    ] == "default"

    assert payload["metadata"] == {
        "justification_segment_count": 2,
        "notes_segment_count": 1,
        "evidence_count": 2,
    }

    assert (
        payload[
            "justification_segments"
        ][0]["evidence"][0][
            "source_id"
        ]
        == "recommendation-001"
    )


def test_read_forbids_unknown_transport_fields():
    payload = (
        DecisionDraftRead
        .from_draft(
            draft()
        )
        .model_dump(
            mode="json"
        )
    )

    payload["internal_builder_names"] = [
        "RecommendationSegmentBuilder"
    ]

    with pytest.raises(
        ValidationError,
    ):
        DecisionDraftRead.model_validate(
            payload
        )
