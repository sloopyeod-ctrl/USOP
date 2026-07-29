import pytest

from app.intelligence.drafting import (
    DecisionDraft,
    DecisionDraftEvidence,
    DecisionDraftSegment,
)


def recommendation_evidence():
    return DecisionDraftEvidence(
        source_type="Recommendation",
        source_id="recommendation-001",
        label="Recommendation",
        detail=(
            "Remove unnecessary privileged "
            "authorization."
        ),
    )


def guidance_evidence():
    return DecisionDraftEvidence(
        source_type="OrganizationGuidance",
        source_id="knowledge-001",
        label="Privileged access standard",
        detail=(
            "Permanent privileged access "
            "requires explicit review."
        ),
    )


def pattern_evidence():
    return DecisionDraftEvidence(
        source_type="OrganizationPattern",
        source_id=(
            "RepeatedTemporaryAcceptance"
        ),
        label=(
            "Repeated Temporary Acceptance"
        ),
        detail=(
            "Temporary acceptance occurred "
            "more than once."
        ),
    )


def test_evidence_requires_source_type():
    with pytest.raises(
        ValueError,
        match="source type is required",
    ):
        DecisionDraftEvidence(
            source_type="",
            source_id=None,
            label="Recommendation",
        )


def test_evidence_requires_label():
    with pytest.raises(
        ValueError,
        match="Evidence label is required",
    ):
        DecisionDraftEvidence(
            source_type="Recommendation",
            source_id=None,
            label="   ",
        )


def test_segment_requires_text():
    with pytest.raises(
        ValueError,
        match="segment text is required",
    ):
        DecisionDraftSegment(
            text="",
            evidence=(
                recommendation_evidence(),
            ),
        )


def test_segment_requires_traceable_evidence():
    with pytest.raises(
        ValueError,
        match="segment evidence is required",
    ):
        DecisionDraftSegment(
            text=(
                "This unsupported sentence "
                "must not be accepted."
            ),
            evidence=(),
        )


def test_decision_draft_assembles_text_in_stable_order():
    recommendation = (
        recommendation_evidence()
    )

    guidance = guidance_evidence()

    draft = DecisionDraft(
        decision_type="CorrectRisk",
        justification_segments=(
            DecisionDraftSegment(
                text=(
                    "The selected response "
                    "addresses the identified "
                    "privileged authorization."
                ),
                evidence=(
                    recommendation,
                ),
            ),
            DecisionDraftSegment(
                text=(
                    "The response is consistent "
                    "with linked organizational "
                    "guidance."
                ),
                evidence=(
                    guidance,
                ),
            ),
        ),
        notes_segments=(
            DecisionDraftSegment(
                text=(
                    "Record remediation details "
                    "and any external ticket "
                    "reference before submission."
                ),
                evidence=(
                    recommendation,
                ),
            ),
        ),
        confidence_score=95,
    )

    assert draft.suggested_justification == (
        "The selected response addresses the "
        "identified privileged authorization. "
        "The response is consistent with linked "
        "organizational guidance."
    )

    assert draft.suggested_notes == (
        "Record remediation details and any "
        "external ticket reference before "
        "submission."
    )


def test_decision_draft_deduplicates_evidence_in_first_seen_order():
    recommendation = (
        recommendation_evidence()
    )

    guidance = guidance_evidence()
    pattern = pattern_evidence()

    draft = DecisionDraft(
        decision_type="AcceptRisk",
        justification_segments=(
            DecisionDraftSegment(
                text=(
                    "The recommendation remains "
                    "applicable."
                ),
                evidence=(
                    recommendation,
                    guidance,
                ),
            ),
            DecisionDraftSegment(
                text=(
                    "Historical decisions show "
                    "repeated temporary "
                    "acceptance."
                ),
                evidence=(
                    pattern,
                    recommendation,
                ),
            ),
        ),
        notes_segments=(
            DecisionDraftSegment(
                text=(
                    "A future review remains "
                    "necessary."
                ),
                evidence=(
                    guidance,
                ),
            ),
        ),
        confidence_score=90,
    )

    assert draft.evidence_used == (
        recommendation,
        guidance,
        pattern,
    )


def test_decision_draft_allows_empty_notes():
    draft = DecisionDraft(
        decision_type="FalsePositive",
        justification_segments=(
            DecisionDraftSegment(
                text=(
                    "The observed condition does "
                    "not match the current "
                    "technical state."
                ),
                evidence=(
                    recommendation_evidence(),
                ),
            ),
        ),
        notes_segments=(),
        confidence_score=80,
    )

    assert draft.suggested_notes == ""
    assert len(
        draft.evidence_used
    ) == 1


@pytest.mark.parametrize(
    "confidence_score",
    [
        -1,
        101,
    ],
)
def test_decision_draft_rejects_invalid_confidence(
    confidence_score,
):
    with pytest.raises(
        ValueError,
        match="between 0 and 100",
    ):
        DecisionDraft(
            decision_type="CorrectRisk",
            justification_segments=(),
            notes_segments=(),
            confidence_score=(
                confidence_score
            ),
        )


def test_decision_draft_requires_selected_decision_type():
    with pytest.raises(
        ValueError,
        match="Decision type is required",
    ):
        DecisionDraft(
            decision_type=" ",
            justification_segments=(),
            notes_segments=(),
            confidence_score=0,
        )


def test_decision_draft_transport_contract_is_complete():
    recommendation = (
        recommendation_evidence()
    )

    segment = DecisionDraftSegment(
        text=(
            "The selected response addresses "
            "the recommendation."
        ),
        evidence=(
            recommendation,
        ),
    )

    draft = DecisionDraft(
        decision_type="CorrectRisk",
        justification_segments=(
            segment,
        ),
        notes_segments=(),
        confidence_score=100,
    )

    projection = draft.to_dict()

    assert projection == {
        "decision_type": "CorrectRisk",
        "suggested_justification": (
            "The selected response addresses "
            "the recommendation."
        ),
        "suggested_notes": "",
        "justification_segments": [
            {
                "text": (
                    "The selected response "
                    "addresses the "
                    "recommendation."
                ),
                "evidence": [
                    {
                        "source_type": (
                            "Recommendation"
                        ),
                        "source_id": (
                            "recommendation-001"
                        ),
                        "label": (
                            "Recommendation"
                        ),
                        "detail": (
                            "Remove unnecessary "
                            "privileged "
                            "authorization."
                        ),
                    }
                ],
            }
        ],
        "notes_segments": [],
        "evidence_used": [
            {
                "source_type": (
                    "Recommendation"
                ),
                "source_id": (
                    "recommendation-001"
                ),
                "label": (
                    "Recommendation"
                ),
                "detail": (
                    "Remove unnecessary "
                    "privileged authorization."
                ),
            }
        ],
        "confidence_score": 100,
        "construction_version": (
            "decision-draft-v1"
        ),
    }
