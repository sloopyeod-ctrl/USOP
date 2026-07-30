from types import SimpleNamespace

from app.intelligence.drafting import (
    DecisionDraftContext,
    DecisionDraftPipeline,
    HistorySegmentBuilder,
    RecommendationSegmentBuilder,
)


def context(
    history=(),
):
    return DecisionDraftContext(
        decision_type="CorrectRisk",
        recommendation={
            "recommendation_id": (
                "recommendation-001"
            ),
            "title": (
                "Remove unnecessary "
                "privileged access"
            ),
            "description": (
                "Remove the observed "
                "privileged authorization."
            ),
        },
        current_disposition={
            "display_status": "Open",
        },
        decision_history=tuple(
            history
        ),
        organization_guidance=(),
        organization_patterns=(),
    )


def test_history_builder_returns_empty_without_history():
    contribution = (
        HistorySegmentBuilder()
        .build(
            context()
        )
    )

    assert (
        contribution
        .justification_segments
        == ()
    )

    assert (
        contribution.confidence_points
        == 0
    )


def test_history_builder_constructs_factual_summary():
    contribution = (
        HistorySegmentBuilder()
        .build(
            context(
                history=[
                    {
                        "decision_id": (
                            "decision-001"
                        ),
                        "decision_type": (
                            "AcceptRisk"
                        ),
                        "display_status": (
                            "Accepted Temporarily"
                        ),
                        "created_at": (
                            "2026-01-01T00:00:00"
                            "+00:00"
                        ),
                    },
                    {
                        "decision_id": (
                            "decision-002"
                        ),
                        "decision_type": (
                            "CorrectRisk"
                        ),
                        "display_status": (
                            "In Progress"
                        ),
                        "created_at": (
                            "2026-04-01T00:00:00"
                            "+00:00"
                        ),
                    },
                    {
                        "decision_id": (
                            "decision-003"
                        ),
                        "decision_type": (
                            "AcceptRisk"
                        ),
                        "display_status": (
                            "Accepted Temporarily"
                        ),
                        "created_at": (
                            "2026-07-01T00:00:00"
                            "+00:00"
                        ),
                    },
                ]
            )
        )
    )

    assert len(
        contribution
        .justification_segments
    ) == 1

    segment = (
        contribution
        .justification_segments[0]
    )

    assert segment.text == (
        "3 previous organizational decisions "
        "related to this recommendation were "
        "available to provide historical context "
        "(AcceptRisk: 2, CorrectRisk: 1)."
    )

    assert (
        contribution.confidence_points
        == 15
    )

    assert [
        evidence.source_id
        for evidence in segment.evidence
    ] == [
        "decision-001",
        "decision-002",
        "decision-003",
    ]

    assert all(
        evidence.source_type
        == "DecisionHistory"
        for evidence in segment.evidence
    )


def test_history_builder_accepts_object_projections():
    history_item = SimpleNamespace(
        decision_id="decision-001",
        decision_type="Escalate",
        display_status="Escalated",
        created_at=(
            "2026-07-01T00:00:00+00:00"
        ),
    )

    contribution = (
        HistorySegmentBuilder()
        .build(
            context(
                history=[
                    history_item
                ]
            )
        )
    )

    evidence = (
        contribution
        .justification_segments[0]
        .evidence[0]
    )

    assert evidence.source_id == (
        "decision-001"
    )

    assert evidence.label == (
        "Escalate decision"
    )

    assert (
        "Status: Escalated"
        in evidence.detail
    )


def test_history_builder_does_not_prescribe_response():
    contribution = (
        HistorySegmentBuilder()
        .build(
            context(
                history=[
                    {
                        "decision_id": (
                            "decision-001"
                        ),
                        "decision_type": (
                            "CorrectRisk"
                        ),
                        "display_status": (
                            "In Progress"
                        ),
                    }
                ]
            )
        )
    )

    text = (
        contribution
        .justification_segments[0]
        .text
        .lower()
    )

    prohibited_claims = {
        "should",
        "must",
        "recommended",
        "correct response",
        "required by history",
        "consistent with history",
    }

    assert all(
        claim not in text
        for claim in prohibited_claims
    )


def test_pipeline_places_history_after_recommendation():
    pipeline = DecisionDraftPipeline(
        builders=[
            HistorySegmentBuilder(),
            RecommendationSegmentBuilder(),
        ]
    )

    draft = pipeline.construct(
        context(
            history=[
                {
                    "decision_id": (
                        "decision-001"
                    ),
                    "decision_type": (
                        "AcceptRisk"
                    ),
                    "display_status": (
                        "Accepted Temporarily"
                    ),
                }
            ]
        )
    )

    assert len(
        draft.justification_segments
    ) == 2

    assert (
        draft.justification_segments[0]
        .evidence[0]
        .source_type
        == "Recommendation"
    )

    assert (
        draft.justification_segments[1]
        .evidence[0]
        .source_type
        == "DecisionHistory"
    )

    assert draft.confidence_score == 55
