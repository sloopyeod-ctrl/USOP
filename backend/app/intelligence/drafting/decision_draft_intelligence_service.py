from typing import Any

from sqlalchemy.orm import Session

from app.intelligence.decision_knowledge_intelligence_service import (
    DecisionKnowledgeIntelligenceService,
)
from app.intelligence.decision_pattern_intelligence_service import (
    DecisionPatternIntelligenceService,
)
from app.intelligence.drafting.decision_draft import (
    DecisionDraft,
)
from app.intelligence.drafting.draft_context import (
    DecisionDraftContext,
)
from app.intelligence.drafting.draft_pipeline import (
    DecisionDraftPipeline,
)
from app.intelligence.drafting.guidance_segment_builder import (
    GuidanceSegmentBuilder,
)
from app.intelligence.drafting.history_segment_builder import (
    HistorySegmentBuilder,
)
from app.intelligence.drafting.pattern_segment_builder import (
    PatternSegmentBuilder,
)
from app.intelligence.drafting.recommendation_segment_builder import (
    RecommendationSegmentBuilder,
)
from app.intelligence.identity_intelligence_service import (
    IdentityIntelligenceService,
)


class DecisionDraftIntelligenceError(
    ValueError
):
    """
    Base error for decision-draft intelligence operations.
    """


class DecisionDraftIntelligenceValidationError(
    DecisionDraftIntelligenceError
):
    """
    Raised when required draft scoping information is invalid.
    """


class DecisionDraftIdentityNotFoundError(
    DecisionDraftIntelligenceError
):
    """
    Raised when identity intelligence cannot be resolved.
    """


class DecisionDraftRecommendationNotFoundError(
    DecisionDraftIntelligenceError
):
    """
    Raised when the requested recommendation is unavailable.
    """


class DecisionDraftIntelligenceService:
    """
    Orchestrate deterministic construction of decision drafts.

    build() accepts already-scoped authoritative facts and performs pure
    context construction and pipeline execution.

    build_for_recommendation() gathers recommendation-scoped intelligence,
    then delegates deterministic construction to build().

    This service performs no persistence, policy interpretation, decision
    selection, HTTP handling, AI generation, or enforcement.
    """

    def __init__(
        self,
        pipeline: DecisionDraftPipeline | None = None,
        *,
        db: Session | None = None,
        identity_intelligence_service=None,
        decision_knowledge_service=None,
        decision_pattern_service=None,
    ):
        self._pipeline = (
            pipeline
            or DecisionDraftPipeline(
                builders=[
                    RecommendationSegmentBuilder(),
                    HistorySegmentBuilder(),
                    GuidanceSegmentBuilder(),
                    PatternSegmentBuilder(),
                ]
            )
        )

        self._identity_intelligence_service = (
            identity_intelligence_service
        )

        self._decision_knowledge_service = (
            decision_knowledge_service
        )

        self._decision_pattern_service = (
            decision_pattern_service
        )

        if db is not None:
            if (
                self._identity_intelligence_service
                is None
            ):
                self._identity_intelligence_service = (
                    IdentityIntelligenceService(db)
                )

            if (
                self._decision_knowledge_service
                is None
            ):
                self._decision_knowledge_service = (
                    DecisionKnowledgeIntelligenceService(
                        db
                    )
                )

            if (
                self._decision_pattern_service
                is None
            ):
                self._decision_pattern_service = (
                    DecisionPatternIntelligenceService(
                        db
                    )
                )

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
        """
        Construct one draft from already-scoped authoritative facts.
        """

        context = DecisionDraftContext(
            decision_type=(
                self._normalize_decision_type(
                    decision_type
                )
            ),
            recommendation=recommendation,
            current_disposition=(
                current_disposition
            ),
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

    def build_for_recommendation(
        self,
        *,
        organization_id: str,
        identity_id: str,
        recommendation_id: str,
        decision_type,
    ) -> DecisionDraft:
        """
        Gather authoritative recommendation intelligence and construct a
        deterministic analyst-reviewable draft.

        Organizational guidance is loaded only when the current disposition
        references an existing DecisionRecord. New recommendations therefore
        legitimately produce no guidance contribution unless an accountable
        decision already exists.
        """

        normalized_organization_id = (
            self._require_identifier(
                organization_id,
                "Organization",
            )
        )

        normalized_identity_id = (
            self._require_identifier(
                identity_id,
                "Identity",
            )
        )

        normalized_recommendation_id = (
            self._require_identifier(
                recommendation_id,
                "Recommendation",
            )
        )

        normalized_decision_type = (
            self._normalize_decision_type(
                decision_type
            )
        )

        self._require_orchestration_dependencies()

        intelligence = (
            self._identity_intelligence_service
            .get_identity_intelligence(
                normalized_identity_id,
                organization_id=(
                    normalized_organization_id
                ),
            )
        )

        if intelligence is None:
            raise DecisionDraftIdentityNotFoundError(
                "Identity intelligence was not found."
            )

        recommendations = intelligence.get(
            "recommendations",
            [],
        )

        recommendation = next(
            (
                item
                for item in recommendations
                if (
                    item.get(
                        "recommendation_id"
                    )
                    == normalized_recommendation_id
                )
            ),
            None,
        )

        if recommendation is None:
            raise (
                DecisionDraftRecommendationNotFoundError(
                    "Recommendation was not found."
                )
            )

        current_disposition = (
            recommendation.get(
                "organizational_disposition"
            )
            or self._open_disposition()
        )

        decision_history = tuple(
            current_disposition.get(
                "history",
                [],
            )
        )

        organization_patterns = (
            self._decision_pattern_service
            .analyze_recommendation(
                organization_id=(
                    normalized_organization_id
                ),
                identity_id=(
                    normalized_identity_id
                ),
                recommendation_id=(
                    normalized_recommendation_id
                ),
            )
        )

        organization_guidance = []

        current_decision_id = (
            current_disposition.get(
                "decision_id"
            )
        )

        if current_decision_id:
            organization_guidance = (
                self._decision_knowledge_service
                .list_for_decision(
                    organization_id=(
                        normalized_organization_id
                    ),
                    decision_record_id=(
                        str(current_decision_id)
                    ),
                )
            )

        return self.build(
            decision_type=(
                normalized_decision_type
            ),
            recommendation=recommendation,
            current_disposition=(
                current_disposition
            ),
            decision_history=(
                decision_history
            ),
            organization_guidance=(
                organization_guidance
            ),
            organization_patterns=(
                organization_patterns
            ),
        )

    def _require_orchestration_dependencies(
        self,
    ) -> None:
        missing_dependencies = []

        if (
            self._identity_intelligence_service
            is None
        ):
            missing_dependencies.append(
                "identity intelligence"
            )

        if (
            self._decision_knowledge_service
            is None
        ):
            missing_dependencies.append(
                "decision knowledge"
            )

        if (
            self._decision_pattern_service
            is None
        ):
            missing_dependencies.append(
                "decision pattern"
            )

        if missing_dependencies:
            raise DecisionDraftIntelligenceError(
                "Decision draft orchestration "
                "dependencies are unavailable: "
                + ", ".join(
                    missing_dependencies
                )
                + "."
            )

    @staticmethod
    def _require_identifier(
        value: str,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise (
                DecisionDraftIntelligenceValidationError(
                    f"{field_name} identifier "
                    "is required."
                )
            )

        normalized = value.strip()

        if not normalized:
            raise (
                DecisionDraftIntelligenceValidationError(
                    f"{field_name} identifier "
                    "is required."
                )
            )

        return normalized

    @staticmethod
    def _normalize_decision_type(
        value: Any,
    ) -> str:
        normalized_value = getattr(
            value,
            "value",
            value,
        )

        if not isinstance(
            normalized_value,
            str,
        ):
            raise (
                DecisionDraftIntelligenceValidationError(
                    "Decision type is required."
                )
            )

        normalized = (
            normalized_value.strip()
        )

        if not normalized:
            raise (
                DecisionDraftIntelligenceValidationError(
                    "Decision type is required."
                )
            )

        return normalized

    @staticmethod
    def _open_disposition() -> dict:
        return {
            "decision_id": None,
            "decision_type": None,
            "status": "Open",
            "display_status": "Open",
            "history_count": 0,
            "history": [],
            "is_actionable": True,
            "is_review_due": False,
        }
