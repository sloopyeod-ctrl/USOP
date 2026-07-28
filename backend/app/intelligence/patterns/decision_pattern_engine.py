from typing import Any, Iterable

from app.intelligence.patterns.base_pattern_detector import (
    DecisionPatternDetector,
)
from app.intelligence.patterns.pattern_result import (
    PatternResult,
)


class DecisionPatternEngine:
    """
    Execute independent detectors against authoritative decision history.

    The engine owns detector orchestration and deterministic result ordering.
    It does not own persistence, scoping, policy interpretation, risk
    decisions, recommendations, or enforcement.
    """

    def __init__(
        self,
        detectors: Iterable[
            DecisionPatternDetector
        ],
    ):
        self.detectors = tuple(detectors)

    def analyze(
        self,
        decision_records: Iterable[Any],
    ) -> list[PatternResult]:
        """
        Execute every configured detector against the same stable history.
        """

        stable_history = tuple(
            decision_records
        )

        results: list[PatternResult] = []

        for detector in self.detectors:
            results.extend(
                detector.detect(
                    stable_history
                )
            )

        return sorted(
            results,
            key=self._result_sort_key,
        )

    @staticmethod
    def _result_sort_key(
        result: PatternResult,
    ) -> tuple[str, str]:
        return (
            result.pattern_type,
            result.title,
        )
