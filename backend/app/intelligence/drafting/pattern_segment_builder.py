from typing import Any

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


class PatternSegmentBuilder:
    """
    Describe deterministic patterns already produced from decision history.

    The builder reports pattern observations without prescribing a response.
    """

    builder_name = (
        "PatternSegmentBuilder"
    )

    order = 300

    def build(
        self,
        context: DecisionDraftContext,
    ) -> DecisionDraftContribution:
        evidence_items = []

        for pattern in (
            context.organization_patterns
        ):
            pattern_type = self._value(
                pattern,
                "pattern_type",
            )

            title = (
                self._value(
                    pattern,
                    "title",
                )
                or "Observed organizational pattern"
            )

            summary = self._value(
                pattern,
                "summary",
            )

            evidence_items.append(
                DecisionDraftEvidence(
                    source_type=(
                        "OrganizationPattern"
                    ),
                    source_id=(
                        str(pattern_type)
                        if pattern_type
                        else None
                    ),
                    label=title,
                    detail=(
                        summary or title
                    ),
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
            "Established organizational "
            "decision patterns were available "
            "to support consistent analyst "
            "decision making."
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
            confidence_points=20,
        )

    @staticmethod
    def _value(
        item: Any,
        field_name: str,
    ):
        if isinstance(item, dict):
            return item.get(
                field_name
            )

        return getattr(
            item,
            field_name,
            None,
        )
