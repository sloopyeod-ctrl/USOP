from dataclasses import dataclass

from app.intelligence.drafting.decision_draft import (
    DecisionDraftSegment,
)


@dataclass(
    frozen=True,
    slots=True,
)
class DecisionDraftContribution:
    """
    Explainable draft segments contributed by one independent builder.
    """

    builder_name: str

    justification_segments: tuple[
        DecisionDraftSegment,
        ...,
    ] = ()

    notes_segments: tuple[
        DecisionDraftSegment,
        ...,
    ] = ()

    confidence_points: int = 0

    def __post_init__(self):
        if (
            not isinstance(
                self.builder_name,
                str,
            )
            or not self.builder_name.strip()
        ):
            raise ValueError(
                "Builder name is required."
            )

        if not (
            0
            <= self.confidence_points
            <= 100
        ):
            raise ValueError(
                "Contribution confidence points "
                "must be between 0 and 100."
            )
