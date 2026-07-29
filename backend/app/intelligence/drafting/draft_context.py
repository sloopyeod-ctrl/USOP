from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(
    frozen=True,
    slots=True,
)
class DecisionDraftContext:
    """
    Immutable facts supplied to deterministic draft-segment builders.

    The context contains already-scoped intelligence only. It does not query
    repositories, select a decision, interpret policy, or authorize action.
    """

    decision_type: str
    recommendation: Mapping[str, Any]
    current_disposition: Mapping[str, Any]
    decision_history: tuple[
        Mapping[str, Any],
        ...,
    ]
    organization_guidance: tuple[
        Mapping[str, Any],
        ...,
    ]
    organization_patterns: tuple[
        Any,
        ...,
    ]

    def __post_init__(self):
        if (
            not isinstance(
                self.decision_type,
                str,
            )
            or not self.decision_type.strip()
        ):
            raise ValueError(
                "Decision type is required."
            )

        if not isinstance(
            self.recommendation,
            Mapping,
        ):
            raise ValueError(
                "Recommendation context is required."
            )
