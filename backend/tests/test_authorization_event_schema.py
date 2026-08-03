from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from app.schemas.authorization_event import AuthorizationEventCreate


def test_authorization_event_create_accepts_privilege_window():
    start = datetime(2026, 8, 3, 8, 0, tzinfo=UTC)
    end = datetime(2026, 8, 3, 16, 0, tzinfo=UTC)

    payload = AuthorizationEventCreate(
        organization_id="organization-027",
        organizational_identity_id="organizational-identity-001",
        identity_id="identity-001",
        account_id="account-001",
        role_assignment_id="assignment-001",
        subject_type="Account",
        subject_id="account-001",
        event_type="PIM_ACTIVATED",
        assignment_type="Eligible",
        previous_status="Eligible",
        current_status="Active",
        effective_start=start,
        effective_end=end,
        detected_at=start,
        risk_level="Critical",
        is_material=True,
        source_system="Microsoft Entra ID",
    )

    assert payload.effective_start == start
    assert payload.effective_end == end
    assert payload.is_material is True


def test_authorization_event_rejects_reversed_window():
    start = datetime(2026, 8, 3, 16, 0, tzinfo=UTC)
    end = start - timedelta(hours=8)

    with pytest.raises(ValidationError):
        AuthorizationEventCreate(
            organization_id="organization-027",
            subject_type="Account",
            subject_id="account-001",
            event_type="PIM_ACTIVATED",
            effective_start=start,
            effective_end=end,
            detected_at=start,
        )


def test_authorization_event_confidence_is_bounded():
    with pytest.raises(ValidationError):
        AuthorizationEventCreate(
            organization_id="organization-027",
            subject_type="Account",
            subject_id="account-001",
            event_type="ROLE_ASSIGNED",
            detected_at=datetime.now(UTC),
            confidence_score=101,
        )
