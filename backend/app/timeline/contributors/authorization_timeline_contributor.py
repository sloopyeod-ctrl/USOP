from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.authorization_event_repository import AuthorizationEventRepository
from app.timeline import (
    TimelineCategory,
    TimelineContributorDescriptor,
    TimelineEvent,
    TimelineQuery,
    TimelineSubjectReference,
    TimelineVisibility,
)


class AuthorizationTimelineContributor:
    DESCRIPTOR = TimelineContributorDescriptor(
        contributor_name="authorization",
        display_name="Authorization",
        component_version="1.0.0",
        categories=(TimelineCategory.AUTHORIZATION,),
        priority=10,
    )

    def __init__(self, db: Session, *, repository: AuthorizationEventRepository | None = None):
        self.db = db
        self.repository = repository or AuthorizationEventRepository(db)

    @property
    def descriptor(self) -> TimelineContributorDescriptor:
        return self.DESCRIPTOR

    def contribute(self, query: TimelineQuery) -> list[TimelineEvent]:
        records = self.repository.list_for_organization(
            organization_id=query.organization_id,
            limit=500,
            offset=0,
        )
        return [self._to_event(record) for record in records]

    def _to_event(self, record) -> TimelineEvent:
        title = {
            "ROLE_ASSIGNED": "Authorization assigned",
            "ROLE_REMOVED": "Authorization removed",
            "ROLE_UPDATED": "Authorization changed",
        }.get(record.event_type, "Authorization state changed")

        references = [
            TimelineSubjectReference(
                subject_type=record.subject_type,
                subject_id=record.subject_id,
            )
        ]
        for subject_type, subject_id in (
            ("Identity", record.identity_id),
            ("Account", record.account_id),
            ("RoleAssignment", record.role_assignment_id),
        ):
            if subject_id:
                references.append(
                    TimelineSubjectReference(
                        subject_type=subject_type,
                        subject_id=subject_id,
                    )
                )

        summary = f"{record.subject_type} {record.subject_id}"
        if record.current_status:
            summary += f"; status {record.current_status}"

        return TimelineEvent(
            event_id=f"authorization-event:{record.id}:detected",
            occurred_at=record.detected_at,
            category=TimelineCategory.AUTHORIZATION,
            visibility=self._visibility(record.risk_level, record.is_material),
            title=title,
            summary=summary,
            actor=record.created_by,
            contributor_name=self.DESCRIPTOR.contributor_name,
            contributor_version=self.DESCRIPTOR.component_version,
            source_type="AuthorizationEvent",
            source_id=record.id,
            organization_id=record.organization_id,
            subject_references=tuple(references),
            correlation_id=record.source_identifier,
            metadata={
                "event_type": record.event_type,
                "assignment_type": record.assignment_type,
                "previous_status": record.previous_status,
                "current_status": record.current_status,
                "directory_scope": record.directory_scope,
                "application_scope": record.application_scope,
                "risk_level": record.risk_level,
                "is_material": record.is_material,
                "source_system": record.source_system,
            },
        )

    @staticmethod
    def _visibility(risk_level: str, is_material: bool) -> TimelineVisibility:
        value = str(risk_level or "").strip().lower()
        if value == "critical":
            return TimelineVisibility.CRITICAL
        if value in {"high", "moderate"}:
            return TimelineVisibility.WARNING
        if is_material:
            return TimelineVisibility.NOTICE
        return TimelineVisibility.INFORMATION
