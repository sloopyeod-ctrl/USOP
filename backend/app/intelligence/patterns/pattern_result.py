from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping


@dataclass(
    frozen=True,
    slots=True,
)
class PatternResult:
    """
    Deterministic description of one organizational decision pattern.

    PatternResult contains observed historical facts only. It does not
    prescribe an action, interpret organizational policy, assign risk, or
    authorize enforcement.
    """

    pattern_type: str
    title: str
    summary: str
    scope: str
    metrics: Mapping[str, Any]
    first_seen_at: datetime | None
    last_seen_at: datetime | None
    evidence_record_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """
        Return a transport-safe representation without exposing models.
        """

        return {
            "pattern_type": self.pattern_type,
            "title": self.title,
            "summary": self.summary,
            "scope": self.scope,
            "metrics": dict(self.metrics),
            "first_seen_at": self._serialize_datetime(
                self.first_seen_at
            ),
            "last_seen_at": self._serialize_datetime(
                self.last_seen_at
            ),
            "evidence_record_ids": list(
                self.evidence_record_ids
            ),
        }

    @staticmethod
    def _serialize_datetime(
        value: datetime | None,
    ) -> str | None:
        return value.isoformat() if value else None
