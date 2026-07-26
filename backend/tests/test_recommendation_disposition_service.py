from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from app.intelligence.recommendation_disposition_service import (
    RecommendationDispositionService,
)

NOW = datetime(2026, 7, 27, 12, 0, tzinfo=timezone.utc)


def recommendation(recommendation_id: str = "rec_v1_test"):
    return {
        "recommendation_id": recommendation_id,
        "title": "Disable Dormant Account",
    }


def record(
    *,
    record_id: str = "decision-1",
    recommendation_id: str = "rec_v1_test",
    decision_type: str = "AcceptRisk",
    status: str = "Accepted",
    acceptance_type: str | None = "Temporary",
    review_due_at=None,
    created_at=None,
    justification: str = "Business need remains.",
    notes: str = "Review after migration.",
):
    return SimpleNamespace(
        id=record_id,
        source_identifier=recommendation_id,
        decision_type=decision_type,
        status=status,
        acceptance_type=acceptance_type,
        review_due_at=review_due_at,
        escalated_to=None,
        justification=justification,
        notes=notes,
        external_ticket_reference="CHG-10452",
        created_at=created_at or NOW,
        updated_at=created_at or NOW,
    )


def test_open_recommendation_is_actionable():
    service = RecommendationDispositionService()
    projected = service.project(
        recommendations=[recommendation()],
        decision_records=[],
        now=NOW,
    )
    disposition = projected[0]["organizational_disposition"]
    assert disposition["display_status"] == "Open"
    assert disposition["is_actionable"] is True
    assert disposition["history_count"] == 0
    assert disposition["history"] == []


def test_temporary_acceptance_is_not_actionable_before_review():
    service = RecommendationDispositionService()
    projected = service.project(
        recommendations=[recommendation()],
        decision_records=[record(review_due_at=NOW + timedelta(days=30))],
        now=NOW,
    )
    disposition = projected[0]["organizational_disposition"]
    assert disposition["display_status"] == "Accepted Temporarily"
    assert disposition["is_actionable"] is False
    assert disposition["history_count"] == 1


def test_temporary_acceptance_reopens_when_review_is_due():
    service = RecommendationDispositionService()
    projected = service.project(
        recommendations=[recommendation()],
        decision_records=[record(review_due_at=NOW - timedelta(minutes=1))],
        now=NOW,
    )
    disposition = projected[0]["organizational_disposition"]
    assert disposition["display_status"] == "Review Due"
    assert disposition["is_actionable"] is True


def test_latest_decision_is_authoritative_and_history_is_preserved():
    service = RecommendationDispositionService()
    projected = service.project(
        recommendations=[recommendation()],
        decision_records=[
            record(
                record_id="older",
                decision_type="Escalate",
                status="Escalated",
                acceptance_type=None,
                created_at=NOW - timedelta(days=1),
                justification="Leadership review required.",
                notes="Escalated to IAM.",
            ),
            record(
                record_id="newer",
                decision_type="FalsePositive",
                status="Closed",
                acceptance_type=None,
                created_at=NOW,
                justification="Evidence was stale.",
                notes="Provider data corrected.",
            ),
        ],
        now=NOW,
    )
    disposition = projected[0]["organizational_disposition"]
    assert disposition["decision_id"] == "newer"
    assert disposition["display_status"] == "False Positive"
    assert disposition["history_count"] == 2
    assert [item["decision_id"] for item in disposition["history"]] == ["newer", "older"]
