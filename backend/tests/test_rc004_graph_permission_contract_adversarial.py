from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

SECURITY_GUIDE = (
    ROOT / "docs" / "customer" / "03-Security-Deployment-Guide.md"
)
KNOWN_LIMITATIONS = (
    ROOT / "docs" / "customer" / "08-Known-Limitations.md"
)
RELEASE_NOTES = (
    ROOT / "docs" / "customer" / "07-Release-Notes.md"
)


REQUIRED_GRAPH_PERMISSIONS = {
    "User.Read.All",
    "GroupMember.Read.All",
    "RoleManagement.Read.Directory",
}

EXCLUDED_BROAD_PERMISSIONS = {
    "Directory.Read.All",
    "Group.Read.All",
    "Application.Read.All",
    "Device.Read.All",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_gate_security_guide_declares_exact_required_permissions():
    text = _text(SECURITY_GUIDE)

    for permission in REQUIRED_GRAPH_PERMISSIONS:
        assert permission in text

    assert "| TBD | TBD | TBD |" not in text


def test_gate_required_permissions_are_application_permissions():
    text = _text(SECURITY_GUIDE)

    for permission in REQUIRED_GRAPH_PERMISSIONS:
        matching_lines = [
            line
            for line in text.splitlines()
            if permission in line and line.startswith("|")
        ]

        assert len(matching_lines) == 1
        assert "| Application | Required |" in matching_lines[0]


def test_gate_admin_consent_is_explicit():
    security = _text(SECURITY_GUIDE)
    limitations = _text(KNOWN_LIMITATIONS)
    release_notes = _text(RELEASE_NOTES)

    assert "Admin Consent" in security
    assert "Administrator consent is required." in limitations
    assert "require administrator consent" in release_notes


def test_gate_broad_permissions_are_explicitly_not_required():
    security = _text(SECURITY_GUIDE)
    limitations = _text(KNOWN_LIMITATIONS)
    release_notes = _text(RELEASE_NOTES)

    for permission in EXCLUDED_BROAD_PERMISSIONS:
        assert permission in security
        assert permission in limitations
        assert permission in release_notes


def test_gate_group_read_all_is_not_declared_required():
    text = _text(SECURITY_GUIDE)

    required_rows = [
        line
        for line in text.splitlines()
        if line.startswith("|")
        and "| Yes |" in line
    ]

    assert not any(
        "Group.Read.All" in line
        for line in required_rows
    )
    assert any(
        "GroupMember.Read.All" in line
        for line in required_rows
    )


def test_gate_directory_read_all_is_not_declared_required():
    text = _text(SECURITY_GUIDE)

    required_rows = [
        line
        for line in text.splitlines()
        if line.startswith("|")
        and "| Yes |" in line
    ]

    assert not any(
        "Directory.Read.All" in line
        for line in required_rows
    )


def test_gate_graph_collector_and_inbound_auth_remain_separate():
    text = _text(SECURITY_GUIDE)

    assert "client-credentials flow" in text
    assert "delegated Microsoft Entra inbound-authentication" in text
    assert "separate" in text


def test_gate_exact_supported_graph_operations_are_documented():
    text = _text(SECURITY_GUIDE)

    expected_operations = (
        "GET /users",
        "GET /groups",
        "GET /groups/{id}/members",
        "GET /roleManagement/directory/roleAssignments",
        "GET /roleManagement/directory/roleDefinitions/{id}",
    )

    for operation in expected_operations:
        assert operation in text


def test_gate_service_principal_membership_limitation_remains_visible():
    text = _text(KNOWN_LIMITATIONS)

    assert "### Service-Principal Group Membership" in text
    assert (
        "does not claim complete service-principal group-membership visibility"
        in text
    )
    assert "Microsoft Graph v1.0" in text
    assert "GET /groups/{id}/members" in text
    assert (
        "absence of a service-principal membership edge in USOP"
        in text
    )
    assert (
        "is not proof that the relationship is absent from Microsoft Entra"
        in text
    )


def test_gate_release_notes_publish_frozen_permission_contract():
    text = _text(RELEASE_NOTES)

    for permission in REQUIRED_GRAPH_PERMISSIONS:
        assert permission in text

    assert (
        "Exact Graph permissions, ports, image identifiers"
        not in text
    )
