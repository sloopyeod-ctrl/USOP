from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

PROVIDER = (
    ROOT
    / "backend"
    / "app"
    / "connectors"
    / "microsoft"
    / "EntraProvider.py"
)

SECURITY_GUIDE = (
    ROOT / "docs" / "customer" / "03-Security-Deployment-Guide.md"
)
KNOWN_LIMITATIONS = (
    ROOT / "docs" / "customer" / "08-Known-Limitations.md"
)
RELEASE_NOTES = (
    ROOT / "docs" / "customer" / "07-Release-Notes.md"
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_gate_provider_keeps_stable_direct_membership_endpoint():
    text = _text(PROVIDER)

    assert 'f"/groups/{group_identifier}/members"' in text
    assert '"$top": 100' in text


def test_gate_provider_does_not_use_graph_beta():
    text = _text(PROVIDER).lower()

    assert "graph.microsoft.com/beta" not in text
    assert "/beta/" not in text


def test_gate_provider_does_not_replace_direct_members_with_expand():
    text = _text(PROVIDER)

    assert '"": "members"' not in text
    assert "=members" not in text


def test_gate_provider_does_not_substitute_transitive_membership():
    text = _text(PROVIDER)

    assert "transitiveMembers" not in text


def test_gate_security_guide_disclaims_service_principal_completeness():
    text = _text(SECURITY_GUIDE)

    assert (
        "does not claim complete service-principal group-membership visibility"
        in text
    )
    assert "GET /groups/{id}/members" in text
    assert "GET /groups/{id}?$expand=members" in text


def test_gate_security_guide_preserves_direct_semantics():
    text = _text(SECURITY_GUIDE)

    assert "direct relationship semantics" in text
    assert "transitive membership" in text


def test_gate_known_limitations_warns_absence_is_not_proof():
    text = _text(KNOWN_LIMITATIONS)

    assert (
        "absence of a service-principal membership edge in USOP"
        in text
    )
    assert (
        "is not proof that the relationship is absent from Microsoft Entra"
        in text
    )


def test_gate_known_limitations_records_live_validation_evidence():
    text = _text(KNOWN_LIMITATIONS)

    assert "Release validation reproduced the limitation" in text
    assert "#microsoft.graph.servicePrincipal" in text


def test_gate_release_notes_publish_membership_boundary():
    text = _text(RELEASE_NOTES)

    assert (
        "does not claim complete service-principal group-membership visibility"
        in text
    )
    assert "does not use Microsoft Graph beta APIs" in text


def test_gate_service_principal_translation_remains_supported():
    text = _text(PROVIDER)

    assert 'odata_type.endswith(".serviceprincipal")' in text
    assert "PrincipalType.SERVICE_PRINCIPAL" in text
