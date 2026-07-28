from datetime import (
    UTC,
    datetime,
    timedelta,
)
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.intelligence.decision_pattern_intelligence_service import (
    DecisionPatternIntelligenceService,
    DecisionPatternIntelligenceValidationError,
)
from app.intelligence.patterns import (
    DecisionPatternEngine,
    PatternResult,
)


ORGANIZATION_ID = "organization-001"
IDENTITY_ID = "identity-001"
RECOMMENDATION_ID = "recommendation-001"


def decision_record(
    *,
    record_id: str,
    recommendation_id: str = (
        RECOMMENDATION_ID
    ),
    decision_type: str = "AcceptRisk",
    acceptance_type: str | None = (
        "Temporary"
    ),
    created_at: datetime,
    review_days: int | None = 90,
):
    return SimpleNamespace(
        id=record_id,
        source_identifier=(
            recommendation_id
        ),
        decision_type=decision_type,
        acceptance_type=acceptance_type,
        created_at=created_at,
        review_due_at=(
            created_at
            + timedelta(
                days=review_days
            )
            if review_days is not None
            else None
        ),
    )


@pytest.fixture
def service():
    service = (
        DecisionPatternIntelligenceService(
            MagicMock()
        )
    )

    service.decision_record_service = (
        MagicMock()
    )

    return service


def test_analyze_recommendation_uses_scoped_identity_history(
    service,
):
    service.decision_record_service.by_identity.return_value = []

    result = service.analyze_recommendation(
        organization_id=ORGANIZATION_ID,
        identity_id=IDENTITY_ID,
        recommendation_id=(
            RECOMMENDATION_ID
        ),
    )

    (
        service.decision_record_service
        .by_identity
        .assert_called_once_with(
            organization_id=(
                ORGANIZATION_ID
            ),
            identity_id=IDENTITY_ID,
        )
    )

    assert result == []


def test_analyze_recommendation_filters_other_recommendations(
    service,
):
    service.decision_record_service.by_identity.return_value = [
        decision_record(
            record_id="decision-001",
            created_at=datetime(
                2026,
                1,
                1,
                tzinfo=UTC,
            ),
        ),
        decision_record(
            record_id="decision-002",
            created_at=datetime(
                2026,
                4,
                1,
                tzinfo=UTC,
            ),
        ),
        decision_record(
            record_id="decision-other",
            recommendation_id=(
                "recommendation-other"
            ),
            created_at=datetime(
                2026,
                5,
                1,
                tzinfo=UTC,
            ),
        ),
    ]

    result = service.analyze_recommendation(
        organization_id=ORGANIZATION_ID,
        identity_id=IDENTITY_ID,
        recommendation_id=(
            RECOMMENDATION_ID
        ),
    )

    assert len(result) == 1

    pattern = result[0]

    assert (
        pattern.pattern_type
        == "RepeatedTemporaryAcceptance"
    )

    assert (
        pattern.metrics[
            "occurrence_count"
        ]
        == 2
    )

    assert pattern.evidence_record_ids == (
        "decision-001",
        "decision-002",
    )


def test_analyze_recommendation_passes_immutable_scoped_history_to_engine():
    expected_result = PatternResult(
        pattern_type="ObservedPattern",
        title="Observed Pattern",
        summary=(
            "A deterministic pattern was "
            "observed."
        ),
        scope="Recommendation",
        metrics={
            "occurrence_count": 2,
        },
        first_seen_at=None,
        last_seen_at=None,
        evidence_record_ids=(),
    )

    engine = MagicMock(
        spec=DecisionPatternEngine
    )

    engine.analyze.return_value = [
        expected_result
    ]

    service = (
        DecisionPatternIntelligenceService(
            MagicMock(),
            engine=engine,
        )
    )

    service.decision_record_service = (
        MagicMock()
    )

    matching_one = decision_record(
        record_id="decision-001",
        created_at=datetime(
            2026,
            1,
            1,
            tzinfo=UTC,
        ),
    )

    matching_two = decision_record(
        record_id="decision-002",
        created_at=datetime(
            2026,
            2,
            1,
            tzinfo=UTC,
        ),
    )

    nonmatching = decision_record(
        record_id="decision-other",
        recommendation_id=(
            "recommendation-other"
        ),
        created_at=datetime(
            2026,
            3,
            1,
            tzinfo=UTC,
        ),
    )

    service.decision_record_service.by_identity.return_value = [
        matching_one,
        nonmatching,
        matching_two,
    ]

    result = service.analyze_recommendation(
        organization_id=ORGANIZATION_ID,
        identity_id=IDENTITY_ID,
        recommendation_id=(
            RECOMMENDATION_ID
        ),
    )

    engine.analyze.assert_called_once()

    scoped_history = (
        engine.analyze.call_args.args[0]
    )

    assert isinstance(
        scoped_history,
        tuple,
    )

    assert scoped_history == (
        matching_one,
        matching_two,
    )

    assert result == [
        expected_result
    ]


def test_analyze_recommendation_returns_no_pattern_for_single_occurrence(
    service,
):
    service.decision_record_service.by_identity.return_value = [
        decision_record(
            record_id="decision-001",
            created_at=datetime(
                2026,
                1,
                1,
                tzinfo=UTC,
            ),
        )
    ]

    result = service.analyze_recommendation(
        organization_id=ORGANIZATION_ID,
        identity_id=IDENTITY_ID,
        recommendation_id=(
            RECOMMENDATION_ID
        ),
    )

    assert result == []


@pytest.mark.parametrize(
    (
        "organization_id",
        "identity_id",
        "recommendation_id",
        "expected_message",
    ),
    [
        (
            "",
            IDENTITY_ID,
            RECOMMENDATION_ID,
            "Organization identifier is required.",
        ),
        (
            ORGANIZATION_ID,
            "   ",
            RECOMMENDATION_ID,
            "Identity identifier is required.",
        ),
        (
            ORGANIZATION_ID,
            IDENTITY_ID,
            "",
            "Recommendation identifier is required.",
        ),
    ],
)
def test_analyze_recommendation_rejects_missing_scope(
    service,
    organization_id,
    identity_id,
    recommendation_id,
    expected_message,
):
    with pytest.raises(
        DecisionPatternIntelligenceValidationError,
        match=expected_message,
    ):
        service.analyze_recommendation(
            organization_id=organization_id,
            identity_id=identity_id,
            recommendation_id=(
                recommendation_id
            ),
        )

    (
        service.decision_record_service
        .by_identity
        .assert_not_called()
    )


def test_analyze_recommendation_normalizes_scope_identifiers(
    service,
):
    service.decision_record_service.by_identity.return_value = []

    service.analyze_recommendation(
        organization_id=(
            f"  {ORGANIZATION_ID}  "
        ),
        identity_id=(
            f"  {IDENTITY_ID}  "
        ),
        recommendation_id=(
            f"  {RECOMMENDATION_ID}  "
        ),
    )

    (
        service.decision_record_service
        .by_identity
        .assert_called_once_with(
            organization_id=(
                ORGANIZATION_ID
            ),
            identity_id=IDENTITY_ID,
        )
    )
