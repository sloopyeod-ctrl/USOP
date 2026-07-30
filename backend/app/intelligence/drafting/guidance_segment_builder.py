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


class GuidanceSegmentBuilder:
    """
    Describe the presence of linked customer-owned organizational guidance.

    This builder does not interpret, summarize, or claim compliance with the
    customer's policy. It only states that linked guidance was considered.
    """

    builder_name = (
        "GuidanceSegmentBuilder"
    )

    order = 200

    def build(
        self,
        context: DecisionDraftContext,
    ) -> DecisionDraftContribution:
        evidence_items = []

        for item in (
            context.organization_guidance
        ):
            knowledge = (
                item.get("knowledge", {})
                if isinstance(item, dict)
                else {}
            )

            knowledge_id = (
                knowledge.get("id")
            )

            title = (
                knowledge.get("title")
                or "Linked organizational guidance"
            )

            detail = (
                knowledge.get("summary")
                or knowledge.get("guidance")
                or title
            )

            evidence_items.append(
                DecisionDraftEvidence(
                    source_type=(
                        "OrganizationGuidance"
                    ),
                    source_id=(
                        str(knowledge_id)
                        if knowledge_id
                        else None
                    ),
                    label=title,
                    detail=detail,
                )
            )

        if not evidence_items:
            return DecisionDraftContribution(
                builder_name=(
                    self.builder_name
                ),
            )

        segment = DecisionDraftSegment(
            text=(
            "Customer-owned organizational "
            "guidance was available during "
            "preparation of this decision "
            "and should be considered during "
            "analyst review."
        ),
            evidence=tuple(
                evidence_items
            ),
        )

        return DecisionDraftContribution(
            builder_name=(
                self.builder_name
            ),
            justification_segments=(
                segment,
            ),
            confidence_points=25,
        )
