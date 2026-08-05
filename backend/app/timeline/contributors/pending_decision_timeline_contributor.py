from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.pending_decision_work_item_repository import PendingDecisionWorkItemRepository
from app.timeline import (
    TimelineCategory,
    TimelineContributorDescriptor,
    TimelineEvent,
    TimelineQuery,
    TimelineSubjectReference,
    TimelineVisibility,
)


class PendingDecisionTimelineContributor:
    DESCRIPTOR = TimelineContributorDescriptor(
        contributor_name="pending-decision",
        display_name="Pending Decision Work",
        component_version="1.0.0",
        categories=(TimelineCategory.OPERATIONAL,),
        priority=20,
    )

    def __init__(self, db: Session, *, repository: PendingDecisionWorkItemRepository | None = None):
        self.db = db
        self.repository = repository or PendingDecisionWorkItemRepository(db)

    @property
    def descriptor(self) -> TimelineContributorDescriptor:
        return self.DESCRIPTOR

    def contribute(self, query: TimelineQuery) -> list[TimelineEvent]:
        records = self.repository.list_for_organization(
            organization_id=query.organization_id,
            status=None,
        )
        events: list[TimelineEvent] = []
        for record in records:
            events.extend(self._events_for(record))
        return events

    def _events_for(self, record) -> list[TimelineEvent]:
        refs = [TimelineSubjectReference(
            subject_type="PendingDecisionWorkItem",
            subject_id=record.id,
            label=record.title,
        )]
        if record.identity_id:
            refs.append(TimelineSubjectReference(subject_type="Identity", subject_id=record.identity_id))
        if record.decision_record_id:
            refs.append(TimelineSubjectReference(subject_type="DecisionRecord", subject_id=record.decision_record_id))

        metadata = {
            "decision_category": record.decision_category,
            "priority": record.priority,
            "risk_level": record.risk_level,
            "status": record.status,
            "source_type": record.source_type,
            "source_id": record.source_id,
            "source_system": record.source_system,
        }
        correlation_id = record.source_identifier or record.source_id
        events = [TimelineEvent(
            event_id=f"pending-work:{record.id}:created",
            occurred_at=record.created_at,
            category=TimelineCategory.OPERATIONAL,
            visibility=self._visibility(record.priority, record.risk_level),
            title="Investigation opened",
            summary=record.summary or record.materiality_reason or record.title,
            actor=record.created_by,
            contributor_name=self.DESCRIPTOR.contributor_name,
            contributor_version=self.DESCRIPTOR.component_version,
            source_type="PendingDecisionWorkItem",
            source_id=record.id,
            organization_id=record.organization_id,
            subject_references=tuple(refs),
            correlation_id=correlation_id,
            metadata=metadata,
        )]
        if record.claimed_at:
            events.append(TimelineEvent(
                event_id=f"pending-work:{record.id}:claimed",
                occurred_at=record.claimed_at,
                category=TimelineCategory.OPERATIONAL,
                visibility=TimelineVisibility.NOTICE,
                title="Investigation claimed",
                summary=(f"Assigned to {record.assigned_to}" if record.assigned_to else "Analyst ownership was recorded."),
                actor=record.assigned_to,
                contributor_name=self.DESCRIPTOR.contributor_name,
                contributor_version=self.DESCRIPTOR.component_version,
                source_type="PendingDecisionWorkItem",
                source_id=record.id,
                organization_id=record.organization_id,
                subject_references=tuple(refs),
                correlation_id=correlation_id,
                metadata=metadata,
            ))
        if record.resolved_at:
            events.append(TimelineEvent(
                event_id=f"pending-work:{record.id}:resolved",
                occurred_at=record.resolved_at,
                category=TimelineCategory.OPERATIONAL,
                visibility=TimelineVisibility.NOTICE,
                title="Investigation resolved",
                summary=("Accountable decision was recorded." if record.decision_record_id else "The investigation was resolved."),
                actor=record.resolved_by,
                contributor_name=self.DESCRIPTOR.contributor_name,
                contributor_version=self.DESCRIPTOR.component_version,
                source_type="PendingDecisionWorkItem",
                source_id=record.id,
                organization_id=record.organization_id,
                subject_references=tuple(refs),
                correlation_id=correlation_id,
                metadata={**metadata, "decision_record_id": record.decision_record_id},
            ))
        return events

    @staticmethod
    def _visibility(priority: str, risk_level: str) -> TimelineVisibility:
        values = {str(priority or "").lower(), str(risk_level or "").lower()}
        if "critical" in values:
            return TimelineVisibility.CRITICAL
        if values.intersection({"high", "moderate"}):
            return TimelineVisibility.WARNING
        return TimelineVisibility.NOTICE
