from typing import Any, Iterable, Protocol

from app.intelligence.patterns.pattern_result import (
    PatternResult,
)


class DecisionPatternDetector(Protocol):
    """
    Contract implemented by deterministic decision-pattern detectors.

    Detectors receive already-scoped authoritative decision history. They do
    not query repositories, mutate records, interpret policy, or perform
    enforcement.
    """

    pattern_type: str

    def detect(
        self,
        decision_records: Iterable[Any],
    ) -> list[PatternResult]:
        """
        Return zero or more factual patterns from the supplied history.
        """
