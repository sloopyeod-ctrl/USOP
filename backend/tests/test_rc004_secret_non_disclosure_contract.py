from datetime import UTC, datetime, timedelta

import httpx
import pytest

from app.security.auth.EntraOidcAuthenticationAdapter import (
    EntraOidcAuthenticationAdapter,
    EntraOidcAuthenticationError,
)
from app.security.auth.EntraOidcValidationConfig import (
    EntraOidcValidationConfig,
)
from app.security.auth.GraphToken import GraphToken
from app.security.auth.MicrosoftGraphAuthService import (
    MicrosoftGraphAuthService,
)


CLIENT_SECRET = "USOP_TEST_CLIENT_SECRET_DO_NOT_LEAK"
BEARER_TOKEN = "USOP_TEST_BEARER_TOKEN_DO_NOT_LEAK"


class CanarySecretProvider:
    def get_secret(self, name, default=None):
        values = {
            "MS_GRAPH_TENANT_ID": "test-tenant",
            "MS_GRAPH_CLIENT_ID": "test-client",
            "MS_GRAPH_CLIENT_SECRET": CLIENT_SECRET,
        }
        return values.get(name, default)


def test_gate_graph_token_repr_does_not_escape_into_auth_errors(monkeypatch):
    service = MicrosoftGraphAuthService()
    service.secret_provider = CanarySecretProvider()

    request = httpx.Request(
        "POST",
        "https://login.microsoftonline.com/test-tenant/oauth2/v2.0/token",
    )
    response = httpx.Response(
        400,
        request=request,
        json={
            "error": "invalid_client",
            "error_description": "synthetic failure",
        },
    )

    def fake_post(*args, **kwargs):
        assert kwargs["data"]["client_secret"] == CLIENT_SECRET
        return response

    monkeypatch.setattr(httpx, "post", fake_post)

    with pytest.raises(httpx.HTTPStatusError) as captured:
        service.get_token()

    rendered = str(captured.value)

    assert CLIENT_SECRET not in rendered


def test_gate_graph_token_authorization_header_is_not_secret_safe_repr():
    token = GraphToken(
        access_token=BEARER_TOKEN,
        token_type="Bearer",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )

    assert token.authorization_header() == {
        "Authorization": f"Bearer {BEARER_TOKEN}"
    }


def test_gate_invalid_inbound_bearer_error_does_not_disclose_token():
    config = EntraOidcValidationConfig(
        tenant_id="test-tenant",
        audience="api://usop-test",
        required_scope="access_as_user",
    )

    adapter = EntraOidcAuthenticationAdapter(config)

    with pytest.raises(EntraOidcAuthenticationError) as captured:
        adapter.authenticate(BEARER_TOKEN)

    rendered = str(captured.value)

    assert BEARER_TOKEN not in rendered


def test_gate_secret_provider_missing_error_names_variable_not_value():
    service = MicrosoftGraphAuthService()

    class EmptyProvider:
        def get_secret(self, name, default=None):
            return None

    service.secret_provider = EmptyProvider()

    with pytest.raises(ValueError) as captured:
        service.get_required_secret("MS_GRAPH_CLIENT_SECRET")

    rendered = str(captured.value)

    assert "MS_GRAPH_CLIENT_SECRET" in rendered
    assert CLIENT_SECRET not in rendered