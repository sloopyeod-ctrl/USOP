from app.security.authorization.authorization_classification_service import (
    AuthorizationClassificationService,
)


def test_global_administrator_is_critical():
    result = AuthorizationClassificationService().classify(
        {
            "system_name": "Microsoft Entra ID",
            "role_source_identifier": (
                "62e90394-69f5-4237-9190-012177145e10"
            ),
            "assignment_type": "Direct",
            "directory_scope": "/",
        }
    )

    assert result["risk_level"] == "Critical"
    assert result["capability"] == "TenantAdministrator"
    assert result["scope_classification"] == "TenantWide"


def test_explicit_privilege_metadata_takes_precedence():
    result = AuthorizationClassificationService().classify(
        {
            "privilege_level": "Privileged",
            "system_name": "Unknown",
            "role_source_identifier": "unknown-role",
        }
    )

    assert result["risk_level"] == "High"
    assert (
        result["classification_source"]
        == "CanonicalPrivilegeMetadata"
    )


def test_unknown_evidence_remains_unknown():
    result = AuthorizationClassificationService().classify(
        {
            "system_name": "Microsoft Entra ID",
            "role_source_identifier": "unmapped-role",
        }
    )

    assert result["risk_level"] == "Unknown"
    assert result["classification_source"] == "InsufficientEvidence"
