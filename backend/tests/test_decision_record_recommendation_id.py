from unittest.mock import Mock

import pytest

from app.domain import DecisionType
from app.schemas.decision_record import (
    DecisionRecordAction,
)
from app.services.decision_record_service import (
    DecisionRecordService,
)


def build_service() -> DecisionRecordService:
    db = Mock()

    service = DecisionRecordService(db)

    service.repository = Mock()
    service.audit_service = Mock()
    service.intelligence_service = Mock()

    return service


def test_unknown_recommendation_id_is_rejected():
    service = build_service()

    service.intelligence_service.get_identity_intelligence.return_value = {
        "identity": {
            "id": "identity-1",
            "display_name": "Test Identity",
        },
        "recommendations": [
            {
                "recommendation_id": "rec_v1_known",
                "title": "Enable MFA",
            },
        ],
    }

    action = DecisionRecordAction(
        decision_type=DecisionType.CORRECT_RISK,
    )

    with pytest.raises(
        ValueError,
        match="Recommendation was not found",
    ):
        service.create_decision_record(
            organization_id="organization-1",
            identity_id="identity-1",
            recommendation_id=(
                "rec_v1_unknown"
            ),
            action=action,
        )

    service.repository.create.assert_not_called()
    service.audit_service.record.assert_not_called()


def test_stable_recommendation_id_is_preserved():
    service = build_service()

    recommendation_id = "rec_v1_known"

    service.intelligence_service.get_identity_intelligence.return_value = {
        "identity": {
            "id": "identity-1",
            "display_name": "Test Identity",
            "source_system": "MicrosoftEntra",
        },
        "risk": {
            "score": 90,
            "level": "Critical",
        },
        "decision": {
            "priority": "Critical",
            "confidence": {
                "score": 100,
            },
        },
        "recommendations": [
            {
                "recommendation_id": (
                    recommendation_id
                ),
                "title": "Enable MFA",
                "description": (
                    "Enable MFA for the account."
                ),
                "severity": "High",
                "recommendation_type": (
                    "Authentication"
                ),
                "evidence_type": (
                    "weak_authentication"
                ),
            },
        ],
    }

    record = Mock()
    record.id = "decision-1"
    record.risk_level = "Critical"

    service.repository.create.return_value = (
        record
    )

    action = DecisionRecordAction(
        decision_type=DecisionType.CORRECT_RISK,
        actor="Regression Test",
    )

    result = service.create_decision_record(
        organization_id="organization-1",
        identity_id="identity-1",
        recommendation_id=recommendation_id,
        action=action,
    )

    assert result is record

    payload = (
        service.repository.create
        .call_args.args[0]
    )

    assert (
        payload.source_identifier
        == recommendation_id
    )

    assert (
        payload.evidence_snapshot_json[
            "recommendation"
        ]["recommendation_id"]
        == recommendation_id
    )

    service.audit_service.record.assert_called_once()

    audit_metadata = (
        service.audit_service.record
        .call_args.kwargs["metadata"]
    )

    assert (
        audit_metadata["recommendation_id"]
        == recommendation_id
    )