from datetime import datetime, timezone
from typing import Any, Iterable


class RecommendationDispositionService:
    """
    Project authoritative organizational decision state onto deterministic
    recommendations.

    Recommendations remain visible so analysts can distinguish new work from
    previously handled work. Full decision history is projected for rapid
    review and repeated-deferral detection.
    """

    OPEN_DISPLAY_STATUS = "Open"

    def project(
        self,
        *,
        recommendations: list[dict[str, Any]],
        decision_records: Iterable[Any],
        now: datetime | None = None,
    ) -> list[dict[str, Any]]:
        effective_now = now or datetime.now(timezone.utc)
        history_by_recommendation: dict[str, list[Any]] = {}

        for record in decision_records:
            recommendation_id = getattr(record, "source_identifier", None)
            if not recommendation_id:
                continue
            history_by_recommendation.setdefault(recommendation_id, []).append(record)

        for history in history_by_recommendation.values():
            history.sort(key=self._record_sort_key, reverse=True)

        return [
            {
                **recommendation,
                "organizational_disposition": self._build_disposition(
                    history_by_recommendation.get(
                        recommendation.get("recommendation_id"),
                        [],
                    ),
                    now=effective_now,
                ),
            }
            for recommendation in recommendations
        ]

    def _build_disposition(
        self,
        history: list[Any],
        *,
        now: datetime,
    ) -> dict[str, Any]:
        if not history:
            return {
                "decision_id": None,
                "decision_type": None,
                "status": "Open",
                "display_status": self.OPEN_DISPLAY_STATUS,
                "acceptance_type": None,
                "review_due_at": None,
                "escalated_to": None,
                "justification": None,
                "notes": None,
                "external_ticket_reference": None,
                "created_at": None,
                "updated_at": None,
                "is_actionable": True,
                "is_review_due": False,
                "history_count": 0,
                "history": [],
            }

        latest_projection = self._project_record(history[0], now=now)
        return {
            **latest_projection,
            "history_count": len(history),
            "history": [
                self._project_record(record, now=now)
                for record in history
            ],
        }

    def _project_record(self, record: Any, *, now: datetime) -> dict[str, Any]:
        decision_type = self._enum_value(getattr(record, "decision_type", None))
        status = self._enum_value(getattr(record, "status", None))
        acceptance_type = self._enum_value(getattr(record, "acceptance_type", None))
        review_due_at = getattr(record, "review_due_at", None)
        is_review_due = self._is_review_due(review_due_at, now=now)

        return {
            "decision_id": getattr(record, "id", None),
            "decision_type": decision_type,
            "status": status,
            "display_status": self._display_status(
                decision_type=decision_type,
                acceptance_type=acceptance_type,
                is_review_due=is_review_due,
            ),
            "acceptance_type": acceptance_type,
            "review_due_at": self._serialize_datetime(review_due_at),
            "escalated_to": getattr(record, "escalated_to", None),
            "justification": getattr(record, "justification", None),
            "notes": getattr(record, "notes", None),
            "external_ticket_reference": getattr(record, "external_ticket_reference", None),
            "created_at": self._serialize_datetime(getattr(record, "created_at", None)),
            "updated_at": self._serialize_datetime(getattr(record, "updated_at", None)),
            "is_actionable": is_review_due,
            "is_review_due": is_review_due,
        }

    @staticmethod
    def _display_status(*, decision_type: str | None, acceptance_type: str | None, is_review_due: bool) -> str:
        if is_review_due:
            return "Review Due"
        if decision_type == "CorrectRisk":
            return "In Progress"
        if decision_type == "AcceptRisk":
            return "Accepted Temporarily" if acceptance_type == "Temporary" else "Accepted Permanently"
        if decision_type == "Escalate":
            return "Escalated"
        if decision_type == "Defer":
            return "Deferred"
        if decision_type == "FalsePositive":
            return "False Positive"
        return "Recorded"

    @staticmethod
    def _is_review_due(review_due_at: datetime | None, *, now: datetime) -> bool:
        if review_due_at is None:
            return False
        normalized_review_due_at = review_due_at if review_due_at.tzinfo is not None else review_due_at.replace(tzinfo=timezone.utc)
        normalized_now = now if now.tzinfo is not None else now.replace(tzinfo=timezone.utc)
        return normalized_review_due_at <= normalized_now

    @staticmethod
    def _record_sort_key(record: Any) -> tuple[datetime, str]:
        created_at = getattr(record, "created_at", None)
        if created_at is None:
            created_at = datetime.min.replace(tzinfo=timezone.utc)
        elif created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        return created_at, str(getattr(record, "id", ""))

    @staticmethod
    def _serialize_datetime(value: datetime | None) -> str | None:
        return value.isoformat() if value else None

    @staticmethod
    def _enum_value(value: Any) -> str | None:
        if value is None:
            return None
        return getattr(value, "value", value)
