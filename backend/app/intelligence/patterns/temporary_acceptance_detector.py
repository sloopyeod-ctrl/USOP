from datetime import datetime, timezone
from typing import Any, Iterable

from app.domain import (
    AcceptanceType,
    DecisionType,
)
from app.intelligence.patterns.pattern_result import (
    PatternResult,
)


class TemporaryAcceptancePatternDetector:
    """
    Detect repeated temporary risk acceptance in scoped decision history.

    The detector reports historical facts only. It does not determine whether
    temporary acceptance was correct, permitted by policy, or eligible for
    continued use.
    """

    pattern_type = (
        "RepeatedTemporaryAcceptance"
    )

    def __init__(
        self,
        *,
        minimum_occurrences: int = 2,
    ):
        if minimum_occurrences < 2:
            raise ValueError(
                "Repeated-pattern detection requires "
                "at least two occurrences."
            )

        self.minimum_occurrences = (
            minimum_occurrences
        )

    def detect(
        self,
        decision_records: Iterable[Any],
    ) -> list[PatternResult]:
        temporary_acceptances = [
            record
            for record in decision_records
            if self._is_temporary_acceptance(
                record
            )
        ]

        temporary_acceptances.sort(
            key=self._record_sort_key,
        )

        occurrence_count = len(
            temporary_acceptances
        )

        if (
            occurrence_count
            < self.minimum_occurrences
        ):
            return []

        scheduled_review_days = [
            interval
            for record in temporary_acceptances
            if (
                interval
                := self._scheduled_review_days(
                    record
                )
            )
            is not None
        ]

        average_scheduled_review_days = (
            round(
                sum(scheduled_review_days)
                / len(
                    scheduled_review_days
                ),
                1,
            )
            if scheduled_review_days
            else None
        )

        first_record = (
            temporary_acceptances[0]
        )
        last_record = (
            temporary_acceptances[-1]
        )

        return [
            PatternResult(
                pattern_type=(
                    self.pattern_type
                ),
                title=(
                    "Repeated Temporary "
                    "Acceptance"
                ),
                summary=(
                    "The organization recorded "
                    "temporary risk acceptance "
                    f"{occurrence_count} times "
                    "for this recommendation."
                ),
                scope="Recommendation",
                metrics={
                    "occurrence_count": (
                        occurrence_count
                    ),
                    "scheduled_review_count": (
                        len(
                            scheduled_review_days
                        )
                    ),
                    (
                        "average_scheduled_"
                        "review_days"
                    ): (
                        average_scheduled_review_days
                    ),
                },
                first_seen_at=getattr(
                    first_record,
                    "created_at",
                    None,
                ),
                last_seen_at=getattr(
                    last_record,
                    "created_at",
                    None,
                ),
                evidence_record_ids=tuple(
                    str(
                        getattr(
                            record,
                            "id",
                            "",
                        )
                    )
                    for record
                    in temporary_acceptances
                    if getattr(
                        record,
                        "id",
                        None,
                    )
                ),
            )
        ]

    @staticmethod
    def _is_temporary_acceptance(
        record: Any,
    ) -> bool:
        decision_type = (
            TemporaryAcceptancePatternDetector
            ._enum_value(
                getattr(
                    record,
                    "decision_type",
                    None,
                )
            )
        )

        acceptance_type = (
            TemporaryAcceptancePatternDetector
            ._enum_value(
                getattr(
                    record,
                    "acceptance_type",
                    None,
                )
            )
        )

        return (
            decision_type
            == DecisionType.ACCEPT_RISK.value
            and acceptance_type
            == AcceptanceType.TEMPORARY.value
        )

    @staticmethod
    def _scheduled_review_days(
        record: Any,
    ) -> float | None:
        created_at = getattr(
            record,
            "created_at",
            None,
        )
        review_due_at = getattr(
            record,
            "review_due_at",
            None,
        )

        if (
            created_at is None
            or review_due_at is None
        ):
            return None

        normalized_created_at = (
            TemporaryAcceptancePatternDetector
            ._normalize_datetime(
                created_at
            )
        )
        normalized_review_due_at = (
            TemporaryAcceptancePatternDetector
            ._normalize_datetime(
                review_due_at
            )
        )

        interval = (
            normalized_review_due_at
            - normalized_created_at
        )

        if interval.total_seconds() < 0:
            return None

        return (
            interval.total_seconds()
            / 86_400
        )

    @staticmethod
    def _record_sort_key(
        record: Any,
    ) -> tuple[datetime, str]:
        created_at = getattr(
            record,
            "created_at",
            None,
        )

        if created_at is None:
            created_at = datetime.min.replace(
                tzinfo=timezone.utc
            )
        else:
            created_at = (
                TemporaryAcceptancePatternDetector
                ._normalize_datetime(
                    created_at
                )
            )

        return (
            created_at,
            str(
                getattr(
                    record,
                    "id",
                    "",
                )
            ),
        )

    @staticmethod
    def _normalize_datetime(
        value: datetime,
    ) -> datetime:
        if value.tzinfo is None:
            return value.replace(
                tzinfo=timezone.utc
            )

        return value.astimezone(
            timezone.utc
        )

    @staticmethod
    def _enum_value(
        value: Any,
    ) -> str | None:
        if value is None:
            return None

        return getattr(
            value,
            "value",
            value,
        )
