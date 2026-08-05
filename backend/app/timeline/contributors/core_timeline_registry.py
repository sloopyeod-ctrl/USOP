from sqlalchemy.orm import Session

from app.timeline import TimelineContributorRegistry
from app.timeline.contributors.authorization_timeline_contributor import AuthorizationTimelineContributor
from app.timeline.contributors.decision_timeline_contributor import DecisionTimelineContributor
from app.timeline.contributors.pending_decision_timeline_contributor import PendingDecisionTimelineContributor


def build_core_timeline_registry(db: Session) -> TimelineContributorRegistry:
    registry = TimelineContributorRegistry()
    registry.register(
        descriptor=AuthorizationTimelineContributor.DESCRIPTOR,
        factory=lambda: AuthorizationTimelineContributor(db),
    )
    registry.register(
        descriptor=PendingDecisionTimelineContributor.DESCRIPTOR,
        factory=lambda: PendingDecisionTimelineContributor(db),
    )
    registry.register(
        descriptor=DecisionTimelineContributor.DESCRIPTOR,
        factory=lambda: DecisionTimelineContributor(db),
    )
    return registry
