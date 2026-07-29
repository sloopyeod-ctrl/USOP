from typing import Protocol

from app.intelligence.drafting.draft_context import (
    DecisionDraftContext,
)
from app.intelligence.drafting.draft_contribution import (
    DecisionDraftContribution,
)


class DecisionDraftSegmentBuilder(Protocol):
    """
    Contract for one deterministic drafting responsibility.

    Builders consume immutable, already-scoped facts and return zero or more
    evidence-backed segments. Builders must not query repositories, mutate
    state, select the analyst's decision, or invoke generative AI.
    """

    builder_name: str
    order: int

    def build(
        self,
        context: DecisionDraftContext,
    ) -> DecisionDraftContribution:
        """
        Return this builder's deterministic contribution.
        """
