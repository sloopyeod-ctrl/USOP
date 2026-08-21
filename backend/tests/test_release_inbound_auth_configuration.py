from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPOSE = REPO_ROOT / "docker-compose.release.yml"
ENV_EXAMPLE = REPO_ROOT / ".env.release.example"


def test_release_compose_requires_inbound_auth_configuration():
    source = COMPOSE.read_text(encoding="utf-8")
    assert "USOP_AUTH_ENTRA_TENANT_ID:" in source
    assert "${USOP_AUTH_ENTRA_TENANT_ID:?USOP_AUTH_ENTRA_TENANT_ID is required}" in source
    assert "USOP_AUTH_ENTRA_AUDIENCE:" in source
    assert "${USOP_AUTH_ENTRA_AUDIENCE:?USOP_AUTH_ENTRA_AUDIENCE is required}" in source


def test_release_env_example_documents_inbound_auth_configuration():
    source = ENV_EXAMPLE.read_text(encoding="utf-8")
    assert "USOP_AUTH_ENTRA_TENANT_ID=CHANGE_ME" in source
    assert "USOP_AUTH_ENTRA_AUDIENCE=CHANGE_ME" in source


def test_inbound_auth_configuration_is_not_graph_credential_aliasing():
    source = COMPOSE.read_text(encoding="utf-8")
    assert "USOP_AUTH_ENTRA_TENANT_ID: ${MS_GRAPH_TENANT_ID" not in source
    assert "USOP_AUTH_ENTRA_AUDIENCE: ${MS_GRAPH_CLIENT_ID" not in source
    assert "USOP_AUTH_ENTRA_AUDIENCE: ${MS_GRAPH_TENANT_ID" not in source


def test_release_contract_keeps_graph_and_inbound_auth_keys_distinct():
    source = ENV_EXAMPLE.read_text(encoding="utf-8")
    for key in (
        "MS_GRAPH_TENANT_ID=",
        "MS_GRAPH_CLIENT_ID=",
        "MS_GRAPH_CLIENT_SECRET=",
        "USOP_AUTH_ENTRA_TENANT_ID=",
        "USOP_AUTH_ENTRA_AUDIENCE=",
    ):
        assert key in source
