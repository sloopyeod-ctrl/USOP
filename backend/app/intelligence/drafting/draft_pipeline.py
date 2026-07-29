from typing import Iterable

from app.intelligence.drafting.base_segment_builder import (
    DecisionDraftSegmentBuilder,
)
from app.intelligence.drafting.decision_draft import (
    DecisionDraft,
)
from app.intelligence.drafting.draft_context import (
    DecisionDraftContext,
)


class DecisionDraftPipeline:
    """
    Orchestrate independent deterministic draft-segment builders.

    The pipeline combines contributions in stable builder order. It does not
    gather data, select decisions, interpret policy, submit decisions, or call
    an AI model.
    """

    def __init__(
        self,
        builders: Iterable[
            DecisionDraftSegmentBuilder
        ],
    ):
        self.builders = tuple(
            sorted(
                builders,
                key=lambda builder: (
                    builder.order,
                    builder.builder_name,
                ),
            )
        )

    def construct(
        self,
        context: DecisionDraftContext,
    ) -> DecisionDraft:
        justification_segments = []
        notes_segments = []
        confidence_points = 0

        for builder in self.builders:
            contribution = builder.build(
                context
            )

            if (
                contribution.builder_name
                != builder.builder_name
            ):
                raise ValueError(
                    "Draft contribution builder "
                    "identity does not match the "
                    "executing builder."
                )

            justification_segments.extend(
                contribution
                .justification_segments
            )

            notes_segments.extend(
                contribution.notes_segments
            )

            confidence_points += (
                contribution
                .confidence_points
            )

        return DecisionDraft(
            decision_type=(
                context.decision_type
            ),
            justification_segments=tuple(
                justification_segments
            ),
            notes_segments=tuple(
                notes_segments
            ),
            confidence_score=min(
                confidence_points,
                100,
            ),
        )
