from app.intelligence.drafting.decision_draft import (
    DecisionDraft,
)
from app.intelligence.drafting.draft_context import (
    DecisionDraftContext,
)
from app.intelligence.drafting.draft_pipeline import (
    DecisionDraftPipeline,
)


class DecisionDraftIntelligenceService:
    """
    Orchestrates deterministic construction of decision drafts.

    Responsibilities:

    * Assemble immutable drafting context.
    * Invoke the drafting pipeline.
    * Return the resulting draft.

    This service intentionally performs no persistence,
    policy interpretation, or HTTP handling.
    """

    def __init__(
        self,
        pipeline: DecisionDraftPipeline,
    ):
        self._pipeline = pipeline

    def build(
        self,
        *,
        decision_type,
        recommendation,
        current_disposition,
        decision_history,
        organization_guidance,
        organization_patterns,
    ) -> DecisionDraft:

        context = DecisionDraftContext(
            decision_type=decision_type,
            recommendation=recommendation,
            current_disposition=current_disposition,
            decision_history=tuple(
                decision_history
            ),
            organization_guidance=tuple(
                organization_guidance
            ),
            organization_patterns=tuple(
                organization_patterns
            ),
        )

        return self._pipeline.construct(
            context
        )
