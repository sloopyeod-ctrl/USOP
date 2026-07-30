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


class HistorySegmentBuilder:
    """
    Construct factual draft context from prior organizational decisions.

    This builder describes the existence and composition of already-scoped
    decision history. It does not interpret whether previous decisions were
    correct, establish policy, or prescribe the current response.
    """

    builder_name = (
        "HistorySegmentBuilder"
    )

    order = 150

    def build(
        self,
        context: DecisionDraftContext,
    ) -> DecisionDraftContribution:
        history = tuple(
            context.decision_history
        )

        if not history:
            return DecisionDraftContribution(
                builder_name=(
                    self.builder_name
                ),
            )

        evidence_items = tuple(
            self._build_evidence(
                decision,
                index,
            )
            for index, decision
            in enumerate(history)
        )

        decision_counts: dict[str, int] = {}

        for decision in history:
            decision_type = (
                self._value(
                    decision,
                    "decision_type",
                )
                or "Recorded"
            )

            decision_counts[
                decision_type
            ] = (
                decision_counts.get(
                    decision_type,
                    0,
                )
                + 1
            )

        count_summary = ", ".join(
            (
                f"{decision_type}: "
                f"{count}"
            )
            for decision_type, count
            in sorted(
                decision_counts.items()
            )
        )

        history_count = len(history)

        segment = DecisionDraftSegment(
            text=(
                f"{history_count} previous "
                + (
                    "organizational decision "
                    if history_count == 1
                    else "organizational decisions "
                )
                + (
                    "related to this recommendation "
                    "were available to provide "
                    "historical context"
                )
                + (
                    f" ({count_summary})."
                    if count_summary
                    else "."
                )
            ),
            evidence=evidence_items,
        )

        return DecisionDraftContribution(
            builder_name=(
                self.builder_name
            ),
            justification_segments=(
                segment,
            ),
            confidence_points=15,
        )

    @classmethod
    def _build_evidence(
        cls,
        decision,
        index: int,
    ) -> DecisionDraftEvidence:
        decision_id = cls._value(
            decision,
            "decision_id",
        )

        decision_type = (
            cls._value(
                decision,
                "decision_type",
            )
            or "Recorded"
        )

        display_status = (
            cls._value(
                decision,
                "display_status",
            )
            or decision_type
        )

        created_at = cls._value(
            decision,
            "created_at",
        )

        detail_parts = [
            f"Status: {display_status}",
        ]

        if created_at:
            detail_parts.append(
                f"Recorded: {created_at}"
            )

        return DecisionDraftEvidence(
            source_type="DecisionHistory",
            source_id=(
                str(decision_id)
                if decision_id
                else f"history-{index}"
            ),
            label=(
                f"{decision_type} decision"
            ),
            detail="; ".join(
                detail_parts
            ),
        )

    @staticmethod
    def _value(
        item,
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
