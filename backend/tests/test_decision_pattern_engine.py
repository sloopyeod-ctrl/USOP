from datetime import (
    UTC,
    datetime,
    timedelta,
)
from types import SimpleNamespace

import pytest

from app.intelligence.patterns import (
    DecisionPatternEngine,
    PatternResult,
    TemporaryAcceptancePatternDetector,
)


def decision_record(
    *,
    record_id: str,
    decision_type: str = "AcceptRisk",
    acceptance_type: str | None = (
        "Temporary"
    ),
    created_at: datetime,
    review_days: int | None = 90,
):
    review_due_at = (
        created_at
        + timedelta(
            days=review_days
        )
        if review_days is not None
        else None
    )

    return SimpleNamespace(
        id=record_id,
        decision_type=decision_type,
        acceptance_type=acceptance_type,
        created_at=created_at,
        review_due_at=review_due_at,
    )


def test_detector_requires_repeated_occurrence():
    detector = (
        TemporaryAcceptancePatternDetector()
    )

    result = detector.detect(
        [
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
    )

    assert result == []


def test_detector_reports_only_temporary_acceptance():
    detector = (
        TemporaryAcceptancePatternDetector()
    )

    result = detector.detect(
        [
            decision_record(
                record_id="decision-003",
                created_at=datetime(
                    2026,
                    7,
                    1,
                    tzinfo=UTC,
                ),
                review_days=120,
            ),
            decision_record(
                record_id="decision-001",
                created_at=datetime(
                    2026,
                    1,
                    1,
                    tzinfo=UTC,
                ),
                review_days=60,
            ),
            decision_record(
                record_id="decision-002",
                created_at=datetime(
                    2026,
                    4,
                    1,
                    tzinfo=UTC,
                ),
                review_days=90,
            ),
            decision_record(
                record_id="decision-permanent",
                acceptance_type="Permanent",
                created_at=datetime(
                    2026,
                    5,
                    1,
                    tzinfo=UTC,
                ),
            ),
            decision_record(
                record_id="decision-corrected",
                decision_type="CorrectRisk",
                acceptance_type=None,
                created_at=datetime(
                    2026,
                    6,
                    1,
                    tzinfo=UTC,
                ),
            ),
        ]
    )

    assert len(result) == 1

    pattern = result[0]

    assert (
        pattern.pattern_type
        == "RepeatedTemporaryAcceptance"
    )
    assert pattern.scope == "Recommendation"
    assert (
        pattern.metrics["occurrence_count"]
        == 3
    )
    assert (
        pattern.metrics[
            "scheduled_review_count"
        ]
        == 3
    )
    assert (
        pattern.metrics[
            "average_scheduled_review_days"
        ]
        == 90.0
    )
    assert pattern.evidence_record_ids == (
        "decision-001",
        "decision-002",
        "decision-003",
    )
    assert pattern.first_seen_at == datetime(
        2026,
        1,
        1,
        tzinfo=UTC,
    )
    assert pattern.last_seen_at == datetime(
        2026,
        7,
        1,
        tzinfo=UTC,
    )


def test_detector_ignores_invalid_review_window():
    detector = (
        TemporaryAcceptancePatternDetector()
    )

    first = decision_record(
        record_id="decision-001",
        created_at=datetime(
            2026,
            1,
            1,
            tzinfo=UTC,
        ),
        review_days=None,
    )

    second = decision_record(
        record_id="decision-002",
        created_at=datetime(
            2026,
            2,
            1,
            tzinfo=UTC,
        ),
        review_days=90,
    )

    first.review_due_at = (
        first.created_at
        - timedelta(days=1)
    )

    result = detector.detect(
        [
            first,
            second,
        ]
    )

    metrics = result[0].metrics

    assert (
        metrics["occurrence_count"]
        == 2
    )
    assert (
        metrics["scheduled_review_count"]
        == 1
    )
    assert (
        metrics[
            "average_scheduled_review_days"
        ]
        == 90.0
    )


def test_detector_rejects_invalid_threshold():
    with pytest.raises(
        ValueError,
        match="at least two",
    ):
        TemporaryAcceptancePatternDetector(
            minimum_occurrences=1
        )


def test_engine_runs_detectors_against_stable_history():
    first_detector = (
        TemporaryAcceptancePatternDetector()
    )

    second_result = PatternResult(
        pattern_type="AnotherPattern",
        title="Another Pattern",
        summary="Another factual pattern.",
        scope="Recommendation",
        metrics={
            "occurrence_count": 2,
        },
        first_seen_at=None,
        last_seen_at=None,
        evidence_record_ids=(),
    )

    class SecondDetector:
        pattern_type = "AnotherPattern"

        def detect(
            self,
            decision_records,
        ):
            assert len(
                tuple(decision_records)
            ) == 2

            return [second_result]

    engine = DecisionPatternEngine(
        detectors=[
            first_detector,
            SecondDetector(),
        ]
    )

    history = (
        decision_record(
            record_id=f"decision-{index}",
            created_at=datetime(
                2026,
                index,
                1,
                tzinfo=UTC,
            ),
        )
        for index in (
            1,
            2,
        )
    )

    results = engine.analyze(history)

    assert [
        result.pattern_type
        for result in results
    ] == [
        "AnotherPattern",
        "RepeatedTemporaryAcceptance",
    ]


def test_pattern_result_serializes_transport_contract():
    pattern = PatternResult(
        pattern_type=(
            "RepeatedTemporaryAcceptance"
        ),
        title=(
            "Repeated Temporary Acceptance"
        ),
        summary=(
            "Temporary acceptance occurred "
            "more than once."
        ),
        scope="Recommendation",
        metrics={
            "occurrence_count": 2,
        },
        first_seen_at=datetime(
            2026,
            1,
            1,
            tzinfo=UTC,
        ),
        last_seen_at=datetime(
            2026,
            2,
            1,
            tzinfo=UTC,
        ),
        evidence_record_ids=(
            "decision-001",
            "decision-002",
        ),
    )

    projection = pattern.to_dict()

    assert projection == {
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
        "scope": "Recommendation",
        "metrics": {
            "occurrence_count": 2,
        },
        "first_seen_at": (
            "2026-01-01T00:00:00+00:00"
        ),
        "last_seen_at": (
            "2026-02-01T00:00:00+00:00"
        ),
        "evidence_record_ids": [
            "decision-001",
            "decision-002",
        ],
    }
