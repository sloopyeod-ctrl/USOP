from app.intelligence.drafting import (
    DecisionDraft,
    DecisionDraftContext,
    DecisionDraftIntelligenceService,
)


class FakePipeline:

    def __init__(self):
        self.received_context = None
        self.result = DecisionDraft(
            decision_type="CorrectRisk",
            justification_segments=(),
            notes_segments=(),
            confidence_score=77,
        )

    def construct(
        self,
        context: DecisionDraftContext,
    ):
        self.received_context = context

        return self.result


def test_service_builds_context():

    pipeline = FakePipeline()

    service = (
        DecisionDraftIntelligenceService(
            pipeline
        )
    )

    service.build(
        decision_type="CorrectRisk",
        recommendation={
            "recommendation_id": "rec-001",
        },
        current_disposition={
            "display_status": "Open",
        },
        decision_history=[
            {
                "decision_id": "history-1",
            }
        ],
        organization_guidance=[
            {
                "guidance_id": "guide-1",
            }
        ],
        organization_patterns=[
            {
                "pattern_id": "pattern-1",
            }
        ],
    )

    context = pipeline.received_context

    assert context is not None

    assert context.decision_type == (
        "CorrectRisk"
    )

    assert (
        context.recommendation[
            "recommendation_id"
        ]
        == "rec-001"
    )

    assert (
        context.current_disposition[
            "display_status"
        ]
        == "Open"
    )

    assert (
        context.decision_history
        == (
            {
                "decision_id": "history-1",
            },
        )
    )

    assert (
        context.organization_guidance
        == (
            {
                "guidance_id": "guide-1",
            },
        )
    )

    assert (
        context.organization_patterns
        == (
            {
                "pattern_id": "pattern-1",
            },
        )
    )


def test_service_converts_collections_to_tuples():

    pipeline = FakePipeline()

    service = (
        DecisionDraftIntelligenceService(
            pipeline
        )
    )

    service.build(
        decision_type="AcceptRisk",
        recommendation={},
        current_disposition={},
        decision_history=[
            {
                "decision_id": "history-1",
            }
        ],
        organization_guidance=[
            {
                "guidance_id": "guidance-1",
            }
        ],
        organization_patterns=[
            {
                "pattern_id": "pattern-1",
            }
        ],
    )

    context = pipeline.received_context

    assert isinstance(
        context.decision_history,
        tuple,
    )

    assert isinstance(
        context.organization_guidance,
        tuple,
    )

    assert isinstance(
        context.organization_patterns,
        tuple,
    )


def test_service_returns_pipeline_result_unchanged():

    pipeline = FakePipeline()

    service = (
        DecisionDraftIntelligenceService(
            pipeline
        )
    )

    draft = service.build(
        decision_type="CorrectRisk",
        recommendation={},
        current_disposition={},
        decision_history=[],
        organization_guidance=[],
        organization_patterns=[],
    )

    assert draft is pipeline.result

    assert draft.decision_type == (
        "CorrectRisk"
    )

    assert (
        draft.confidence_score
        == 77
    )


def test_service_calls_pipeline_once():

    class CountingPipeline:

        def __init__(self):
            self.calls = 0

        def construct(
            self,
            context,
        ):
            self.calls += 1

            return DecisionDraft(
                decision_type=(
                    context.decision_type
                ),
                justification_segments=(),
                notes_segments=(),
                confidence_score=10,
            )

    pipeline = CountingPipeline()

    service = (
        DecisionDraftIntelligenceService(
            pipeline
        )
    )

    draft = service.build(
        decision_type="AcceptRisk",
        recommendation={},
        current_disposition={},
        decision_history=[],
        organization_guidance=[],
        organization_patterns=[],
    )

    assert pipeline.calls == 1

    assert draft.decision_type == (
        "AcceptRisk"
    )


def test_service_does_not_mutate_inputs():

    history = [
        {
            "decision_id": "history-1",
        }
    ]

    guidance = [
        {
            "guidance_id": "guidance-1",
        }
    ]

    patterns = [
        {
            "pattern_id": "pattern-1",
        }
    ]

    pipeline = FakePipeline()

    service = (
        DecisionDraftIntelligenceService(
            pipeline
        )
    )

    service.build(
        decision_type="CorrectRisk",
        recommendation={},
        current_disposition={},
        decision_history=history,
        organization_guidance=guidance,
        organization_patterns=patterns,
    )

    assert history == [
        {
            "decision_id": "history-1",
        }
    ]

    assert guidance == [
        {
            "guidance_id": "guidance-1",
        }
    ]

    assert patterns == [
        {
            "pattern_id": "pattern-1",
        }
    ]
