from app.intelligence.drafting.decision_draft import (
    DecisionDraftEvidence,
    DecisionDraftSegment,
)
from app.intelligence.drafting.draft_context import (
    DecisionDraftContext,
)
from app.intelligence.drafting.draft_contribution import (
    DecisionDraftContribution,
)


class RecommendationSegmentBuilder:
    """
    Construct the baseline segment supported by recommendation facts.
    """

    builder_name = (
        "RecommendationSegmentBuilder"
    )

    order = 100

    def build(
        self,
        context: DecisionDraftContext,
    ) -> DecisionDraftContribution:
        recommendation = (
            context.recommendation
        )

        recommendation_id = (
            recommendation.get(
                "recommendation_id"
            )
        )

        title = (
            recommendation.get("title")
            or "Security recommendation"
        )

        description = (
            recommendation.get(
                "description"
            )
        )

        recommendation_type = (
            recommendation.get(
                "recommendation_type"
            )
        )

        detail_parts = [
            value
            for value in (
                description,
                (
                    "Recommendation type: "
                    f"{recommendation_type}"
                    if recommendation_type
                    else None
                ),
            )
            if value
        ]

        evidence = DecisionDraftEvidence(
            source_type="Recommendation",
            source_id=(
                str(recommendation_id)
                if recommendation_id
                else None
            ),
            label=title,
            detail=(
                " ".join(detail_parts)
                or title
            ),
        )

        segment = DecisionDraftSegment(
            text=(
                "The selected organizational "
                "response addresses the "
                f"recommendation: {title}."
            ),
            evidence=(evidence,),
        )

        return DecisionDraftContribution(
            builder_name=(
                self.builder_name
            ),
            justification_segments=(
                segment,
            ),
            confidence_points=40,
        )
