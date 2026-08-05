from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import Mock

from app.timeline import OperationalTimelineEngine, TimelineContributorRegistry, TimelineQuery
from app.timeline.contributors import (
    AuthorizationTimelineContributor,
    DecisionTimelineContributor,
    PendingDecisionTimelineContributor,
)

NOW = datetime(2026, 8, 5, 12, 0, tzinfo=UTC)


def authorization_record():
    return SimpleNamespace(
        id="auth-001", organization_id="organization-001", identity_id="identity-001",
        account_id="account-001", role_assignment_id="role-assignment-001",
        subject_type="Account", subject_id="account-001", event_type="ROLE_ASSIGNED",
        assignment_type="Permanent", previous_status=None, current_status="Active",
        directory_scope="/", application_scope=None, detected_at=NOW,
        risk_level="Critical", is_material=True, source_system="Microsoft Entra ID",
        source_identifier="auth-001", created_by="system:reconciliation",
    )


def pending_record():
    return SimpleNamespace(
        id="work-001", organization_id="organization-001", identity_id="identity-001",
        decision_record_id="decision-001", title="Review privileged access",
        summary="Material authorization change.", materiality_reason="Critical role assigned.",
        decision_category="Authorization", priority="Critical", risk_level="Critical",
        status="Resolved", source_type="AuthorizationEvent", source_id="auth-001",
        source_system="USOP", source_identifier="auth-001", created_at=NOW,
        claimed_at=NOW, assigned_to="analyst@example.com", resolved_at=NOW,
        resolved_by="analyst@example.com", created_by="system:reconciliation",
    )


def decision_record():
    return SimpleNamespace(
        id="decision-001", organization_id="organization-001", identity_id="identity-001",
        title="Correct privileged access", justification="Role was not required.",
        decision_type="CorrectRisk", status="Closed", risk_level="Critical", risk_score=95,
        approval_status="Approved", verification_status="Verified", acceptance_type=None,
        review_due_at=None, source_system="USOP", source_identifier="rec-001",
        created_at=NOW, created_by="analyst@example.com", approved_at=NOW,
        approved_by="approver@example.com", approval_notes="Approved.", verified_at=NOW,
        verified_by="verifier@example.com", verification_notes="Verified.", closed_at=NOW,
        closed_by="analyst@example.com", closure_notes="Completed.",
    )


def test_authorization_contributor_emits_operational_event():
    repository = Mock()
    repository.list_for_organization.return_value = [authorization_record()]
    events = AuthorizationTimelineContributor(Mock(), repository=repository).contribute(
        TimelineQuery(organization_id="organization-001")
    )
    assert len(events) == 1
    assert events[0].event_id == "authorization-event:auth-001:detected"
    assert events[0].title == "Authorization assigned"
    assert events[0].visibility.value == "Critical"


def test_pending_contributor_emits_created_claimed_resolved():
    repository = Mock()
    repository.list_for_organization.return_value = [pending_record()]
    events = PendingDecisionTimelineContributor(Mock(), repository=repository).contribute(
        TimelineQuery(organization_id="organization-001")
    )
    assert {event.event_id for event in events} == {
        "pending-work:work-001:created",
        "pending-work:work-001:claimed",
        "pending-work:work-001:resolved",
    }


def test_decision_contributor_emits_lifecycle_events():
    repository = Mock()
    repository.list_for_organization.return_value = [decision_record()]
    events = DecisionTimelineContributor(Mock(), repository=repository).contribute(
        TimelineQuery(organization_id="organization-001")
    )
    assert {event.event_id for event in events} == {
        "decision-record:decision-001:created",
        "decision-record:decision-001:approved",
        "decision-record:decision-001:verified",
        "decision-record:decision-001:closed",
    }


def test_contributors_do_not_commit_or_mutate():
    db = Mock()
    repository = Mock()
    record = authorization_record()
    repository.list_for_organization.return_value = [record]
    before = dict(vars(record))
    AuthorizationTimelineContributor(db, repository=repository).contribute(
        TimelineQuery(organization_id="organization-001")
    )
    db.commit.assert_not_called()
    db.flush.assert_not_called()
    assert vars(record) == before


def test_combined_engine_returns_one_chronology():
    auth_repo = Mock(); auth_repo.list_for_organization.return_value = [authorization_record()]
    pending_repo = Mock(); pending_repo.list_for_organization.return_value = [pending_record()]
    decision_repo = Mock(); decision_repo.list_for_organization.return_value = [decision_record()]
    registry = TimelineContributorRegistry()
    registry.register(
        descriptor=AuthorizationTimelineContributor.DESCRIPTOR,
        factory=lambda: AuthorizationTimelineContributor(Mock(), repository=auth_repo),
    )
    registry.register(
        descriptor=PendingDecisionTimelineContributor.DESCRIPTOR,
        factory=lambda: PendingDecisionTimelineContributor(Mock(), repository=pending_repo),
    )
    registry.register(
        descriptor=DecisionTimelineContributor.DESCRIPTOR,
        factory=lambda: DecisionTimelineContributor(Mock(), repository=decision_repo),
    )
    result = OperationalTimelineEngine(registry).build(
        TimelineQuery(organization_id="organization-001", identity_id="identity-001")
    )
    assert len(result.events) == 8
    assert {event.contributor_name for event in result.events} == {
        "authorization", "pending-decision", "decision"
    }
