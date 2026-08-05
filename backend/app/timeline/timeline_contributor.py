from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.timeline.timeline_contributor_descriptor import (
    TimelineContributorDescriptor,
)
from app.timeline.timeline_event import TimelineEvent
from app.timeline.timeline_query import TimelineQuery


@runtime_checkable
class TimelineContributor(Protocol):
    """
    Extension boundary for operational history contributors.
    """

    @property
    def descriptor(
        self,
    ) -> TimelineContributorDescriptor:
        ...

    def contribute(
        self,
        query: TimelineQuery,
    ) -> list[TimelineEvent]:
        ...
