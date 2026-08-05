from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.decision_record_repository import DecisionRecordRepository
from app.timeline import (
    TimelineCategory,
    TimelineContributorDescriptor,
    TimelineEvent,
    TimelineQuery,
    TimelineSubjectReference,
    TimelineVisibility,
)


class DecisionTimelineContributor:
    DESCRIPTOR = TimelineContributorDescriptor(
        contributor_name="decision",
        display_name="Decision",
        component_version="1.0.0",
        categories=(TimelineCategory.DECISION,),
        priority=30,
    )

    def __init__(self, db: Session, *, repository: DecisionRecordRepository | None = None):
        self.db = db
        self.repository = repository or DecisionRecordRepository(db)

    @property
    def descriptor(self) -> TimelineContributorDescriptor:
        return self.DESCRIPTOR

    def contribute(self, query: TimelineQuery) -> list[TimelineEvent]:
        records = self.repository.list_for_organization(query.organization_id)
        events: list[TimelineEvent] = []
        for record in records:
            events.extend(self._events_for(record))
        return events

    def _events_for(self, record) -> list[TimelineEvent]:
        refs = (
            TimelineSubjectReference(subject_type="DecisionRecord", subject_id=record.id, label=record.title),
            TimelineSubjectReference(subject_type="Identity", subject_id=record.identity_id),
        )
        metadata = {
            "decision_type": record.decision_type,
            "status": record.status,
            "risk_level": record.risk_level,
            "risk_score": record.risk_score,
            "approval_status": record.approval_status,
            "verification_status": record.verification_status,
            "acceptance_type": record.acceptance_type,
            "review_due_at": record.review_due_at.isoformat() if record.review_due_at else None,
            "source_system": record.source_system,
            "source_identifier": record.source_identifier,
        }
        base = dict(
            category=TimelineCategory.DECISION,
            contributor_name=self.DESCRIPTOR.contributor_name,
            contributor_version=self.DESCRIPTOR.component_version,
            source_type="DecisionRecord",
            source_id=record.id,
            organization_id=record.organization_id,
            subject_references=refs,
            correlation_id=record.source_identifier,
            metadata=metadata,
        )
        events = [TimelineEvent(
            event_id=f"decision-record:{record.id}:created",
            occurred_at=record.created_at,
            visibility=self._visibility(record.risk_level),
            title="Decision recorded",
            summary=record.justification or record.title,
            actor=record.created_by,
            **base,
        )]
        for suffix, timestamp, title, summary, actor in (
            ("approved", record.approved_at, "Decision approved", record.approval_notes or "Approval was recorded.", record.approved_by),
            ("verified", record.verified_at, "Decision verified", record.verification_notes or "Verification was recorded.", record.verified_by),
            ("closed", record.closed_at, "Decision closed", record.closure_notes or "The decision was closed.", record.closed_by),
        ):
            if timestamp:
                events.append(TimelineEvent(
                    event_id=f"decision-record:{record.id}:{suffix}",
                    occurred_at=timestamp,
                    visibility=TimelineVisibility.NOTICE,
                    title=title,
                    summary=summary,
                    actor=actor,
                    **base,
                ))
        return events

    @staticmethod
    def _visibility(risk_level: str | None) -> TimelineVisibility:
        value = str(risk_level or "").strip().lower()
        if value == "critical":
            return TimelineVisibility.CRITICAL
        if value in {"high", "moderate"}:
            return TimelineVisibility.WARNING
        return TimelineVisibility.NOTICE
