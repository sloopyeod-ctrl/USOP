from datetime import UTC, datetime

from app.schemas.decision_pattern import (
    DecisionPatternRead,
)


def test_decision_pattern_schema():
    pattern = DecisionPatternRead(
        pattern_type="RepeatedTemporaryAcceptance",
        title="Repeated Temporary Acceptance",
        summary="Observed multiple temporary acceptances.",
        scope="Recommendation",
        metrics={
            "occurrence_count": 4,
            "average_review_days": 90,
        },
        first_seen_at=datetime(
            2026,
            1,
            1,
            tzinfo=UTC,
        ),
        last_seen_at=datetime(
            2026,
            6,
            1,
            tzinfo=UTC,
        ),
        evidence_record_ids=[
            "decision-001",
            "decision-002",
        ],
    )

    assert (
        pattern.pattern_type
        == "RepeatedTemporaryAcceptance"
    )

    assert (
        pattern.metrics[
            "occurrence_count"
        ]
        == 4
    )

    assert (
        pattern.evidence_record_ids
        == [
            "decision-001",
            "decision-002",
        ]
    )


def test_decision_pattern_schema_optional_dates():
    pattern = DecisionPatternRead(
        pattern_type="Pattern",
        title="Pattern",
        summary="Summary",
        scope="Recommendation",
        metrics={},
        evidence_record_ids=[],
    )

    assert pattern.first_seen_at is None
    assert pattern.last_seen_at is None


def test_decision_pattern_schema_dump():
    pattern = DecisionPatternRead(
        pattern_type="Pattern",
        title="Pattern",
        summary="Summary",
        scope="Recommendation",
        metrics={
            "count": 2,
        },
        evidence_record_ids=[
            "decision-001",
        ],
    )

    payload = pattern.model_dump()

    assert payload == {
        "pattern_type": "Pattern",
        "title": "Pattern",
        "summary": "Summary",
        "scope": "Recommendation",
        "metrics": {
            "count": 2,
        },
        "first_seen_at": None,
        "last_seen_at": None,
        "evidence_record_ids": [
            "decision-001",
        ],
    }
