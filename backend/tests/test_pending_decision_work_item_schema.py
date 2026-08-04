from app.schemas.pending_decision_work_item import (
    PendingDecisionWorkItemCreate,
)


def test_schema_accepts_generic_authorization_source():
    payload = PendingDecisionWorkItemCreate(
        organization_id="organization-027",
        identity_id="identity-001",
        source_type="AuthorizationEvent",
        source_id="authorization-event-001",
        decision_category="Authorization",
        title="Review Global Administrator assignment",
        priority="Critical",
        risk_level="Critical",
        evidence_snapshot_json={
            "event_type": "ROLE_ASSIGNED",
        },
    )

    assert payload.source_type == "AuthorizationEvent"
    assert payload.decision_category == "Authorization"
    assert payload.status == "Pending"


def test_schema_is_framework_neutral():
    fields = PendingDecisionWorkItemCreate.model_fields

    assert "framework" not in fields
    assert "nist_control" not in fields
    assert "iso_control" not in fields
    assert "gdpr_article" not in fields
