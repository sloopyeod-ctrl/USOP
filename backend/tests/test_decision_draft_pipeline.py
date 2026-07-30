from app.intelligence.drafting import (
    DecisionDraftContext,
    DecisionDraftContribution,
    DecisionDraftPipeline,
    GuidanceSegmentBuilder,
    PatternSegmentBuilder,
    RecommendationSegmentBuilder,
)


def context(
    *,
    guidance=(),
    patterns=(),
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
            "recommendation_type": (
                "Authorization"
            ),
        },
        current_disposition={
            "display_status": "Open",
        },
        decision_history=(),
        organization_guidance=tuple(
            guidance
        ),
        organization_patterns=tuple(
            patterns
        ),
    )


def guidance_item():
    return {
        "knowledge": {
            "id": "knowledge-001",
            "title": (
                "Privileged access standard"
            ),
            "summary": (
                "Privileged assignments "
                "require explicit review."
            ),
        },
    }


def pattern_item():
    return {
        "pattern_type": (
            "RepeatedTemporaryAcceptance"
        ),
        "title": (
            "Repeated Temporary Acceptance"
        ),
        "summary": (
            "Temporary acceptance occurred "
            "more than once."
        ),
    }


def test_pipeline_constructs_stable_explainable_draft():
    pipeline = DecisionDraftPipeline(
        builders=[
            PatternSegmentBuilder(),
            RecommendationSegmentBuilder(),
            GuidanceSegmentBuilder(),
        ]
    )

    draft = pipeline.construct(
        context(
            guidance=[
                guidance_item()
            ],
            patterns=[
                pattern_item()
            ],
        )
    )

    assert draft.decision_type == (
        "CorrectRisk"
    )

    assert (
        draft.suggested_justification
        == (
            "This decision documents the "
            "organization's response to the "
            "recommendation: Remove "
            "unnecessary privileged access. "
            "Customer-owned organizational "
            "guidance was available during "
            "preparation of this decision "
            "and should be considered during "
            "analyst review. "
            "Established organizational "
            "decision patterns were available "
            "to support consistent analyst "
            "decision making."
        )
    )

    assert draft.confidence_score == 85

    assert [
        item.source_type
        for item in draft.evidence_used
    ] == [
        "Recommendation",
        "OrganizationGuidance",
        "OrganizationPattern",
    ]


def test_pipeline_omits_builders_without_supporting_facts():
    pipeline = DecisionDraftPipeline(
        builders=[
            RecommendationSegmentBuilder(),
            GuidanceSegmentBuilder(),
            PatternSegmentBuilder(),
        ]
    )

    draft = pipeline.construct(
        context()
    )

    assert len(
        draft.justification_segments
    ) == 1

    assert draft.confidence_score == 40

    assert [
        item.source_type
        for item in draft.evidence_used
    ] == [
        "Recommendation",
    ]


def test_pipeline_caps_confidence_at_one_hundred():
    class HighConfidenceBuilder:
        builder_name = (
            "HighConfidenceBuilder"
        )
        order = 1

        def build(self, draft_context):
            return DecisionDraftContribution(
                builder_name=(
                    self.builder_name
                ),
                confidence_points=100,
            )

    pipeline = DecisionDraftPipeline(
        builders=[
            HighConfidenceBuilder(),
            RecommendationSegmentBuilder(),
        ]
    )

    draft = pipeline.construct(
        context()
    )

    assert draft.confidence_score == 100


def test_pipeline_rejects_builder_identity_mismatch():
    class InvalidBuilder:
        builder_name = "ExpectedBuilder"
        order = 1

        def build(self, draft_context):
            return DecisionDraftContribution(
                builder_name=(
                    "UnexpectedBuilder"
                ),
            )

    pipeline = DecisionDraftPipeline(
        builders=[
            InvalidBuilder()
        ]
    )

    try:
        pipeline.construct(
            context()
        )
    except ValueError as error:
        assert (
            "identity does not match"
            in str(error)
        )
    else:
        raise AssertionError(
            "Expected builder identity "
            "validation to fail."
        )


def test_guidance_builder_does_not_interpret_policy():
    contribution = (
        GuidanceSegmentBuilder()
        .build(
            context(
                guidance=[
                    guidance_item()
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
        "complies with",
        "required by policy",
        "policy requires",
        "approved by",
    }

    assert all(
        claim not in text
        for claim in prohibited_claims
    )


def test_pattern_builder_accepts_pattern_objects():
    class Pattern:
        pattern_type = (
            "ObservedPattern"
        )
        title = "Observed Pattern"
        summary = (
            "A deterministic pattern "
            "was observed."
        )

    contribution = (
        PatternSegmentBuilder()
        .build(
            context(
                patterns=[
                    Pattern()
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
        "ObservedPattern"
    )
    assert evidence.label == (
        "Observed Pattern"
    )


def test_context_requires_selected_decision_type():
    try:
        DecisionDraftContext(
            decision_type=" ",
            recommendation={},
            current_disposition={},
            decision_history=(),
            organization_guidance=(),
            organization_patterns=(),
        )
    except ValueError as error:
        assert (
            "Decision type is required"
            in str(error)
        )
    else:
        raise AssertionError(
            "Expected decision-type "
            "validation to fail."
        )
