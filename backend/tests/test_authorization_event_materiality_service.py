from app.services.authorization_event_materiality_service import (
    AuthorizationEventMaterialityService,
)


def _classification(risk_level: str) -> dict:
    return {
        "risk_level": risk_level,
        "capability": "Example",
        "classification_source": "Test",
        "reasons": ["test reason"],
        "scope_classification": "TenantWide",
        "assignment_classification": "Direct",
        "evidence": {},
    }


def test_critical_role_assignment_is_material():
    result = AuthorizationEventMaterialityService().evaluate(
        event_type="ROLE_ASSIGNED",
        classification=_classification("Critical"),
    )

    assert result["risk_level"] == "Critical"
    assert result["is_material"] is True


def test_low_role_assignment_is_not_material():
    result = AuthorizationEventMaterialityService().evaluate(
        event_type="ROLE_ASSIGNED",
        classification=_classification("Low"),
    )

    assert result["risk_level"] == "Low"
    assert result["is_material"] is False


def test_unknown_role_assignment_fails_safe():
    result = AuthorizationEventMaterialityService().evaluate(
        event_type="ROLE_ASSIGNED",
        classification=_classification("Unknown"),
    )

    assert result["is_material"] is True
    assert any("incomplete" in reason for reason in result["reasons"])
