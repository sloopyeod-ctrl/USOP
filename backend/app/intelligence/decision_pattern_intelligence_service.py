from sqlalchemy.orm import Session

from app.intelligence.patterns import (
    DecisionPatternEngine,
    PatternResult,
    TemporaryAcceptancePatternDetector,
)
from app.services.decision_record_service import (
    DecisionRecordService,
)


class DecisionPatternIntelligenceError(
    ValueError
):
    """
    Base error for decision-pattern intelligence operations.
    """


class DecisionPatternIntelligenceValidationError(
    DecisionPatternIntelligenceError
):
    """
    Raised when required scoping information is absent or invalid.
    """


class DecisionPatternIntelligenceService:
    """
    Assemble recommendation-scoped organizational pattern intelligence.

    This service owns the boundary between authoritative DecisionRecord
    history and deterministic pattern analysis.

    Organization and identity scoping are delegated to DecisionRecordService.
    Recommendation scoping is performed using the canonical
    DecisionRecord.source_identifier value established when the decision was
    created.

    The service does not interpret policy, recommend an organizational
    response, assign risk, modify customer systems, or perform enforcement.
    """

    def __init__(
        self,
        db: Session,
        *,
        engine: DecisionPatternEngine | None = None,
    ):
        self.db = db

        self.decision_record_service = (
            DecisionRecordService(db)
        )

        self.engine = (
            engine
            or DecisionPatternEngine(
                detectors=[
                    TemporaryAcceptancePatternDetector(),
                ]
            )
        )

    def analyze_recommendation(
        self,
        *,
        organization_id: str,
        identity_id: str,
        recommendation_id: str,
    ) -> list[PatternResult]:
        """
        Return deterministic patterns for one recommendation and identity.

        Only active DecisionRecords already scoped to the requested
        Organization and identity are considered. Records for other
        recommendations are excluded before the history reaches the engine.
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

        decision_records = (
            self.decision_record_service.by_identity(
                organization_id=(
                    normalized_organization_id
                ),
                identity_id=(
                    normalized_identity_id
                ),
            )
        )

        recommendation_history = tuple(
            record
            for record in decision_records
            if (
                getattr(
                    record,
                    "source_identifier",
                    None,
                )
                == normalized_recommendation_id
            )
        )

        return self.engine.analyze(
            recommendation_history
        )

    @staticmethod
    def _require_identifier(
        value: str,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise (
                DecisionPatternIntelligenceValidationError(
                    f"{field_name} identifier is required."
                )
            )

        normalized = value.strip()

        if not normalized:
            raise (
                DecisionPatternIntelligenceValidationError(
                    f"{field_name} identifier is required."
                )
            )

        return normalized
