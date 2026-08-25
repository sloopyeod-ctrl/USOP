from datetime import datetime, timedelta, timezone

import importlib
import pytest

from app.security.auth.GraphToken import GraphToken
from app.security.graph.GraphClient import GraphClient

graph_client_module = importlib.import_module(
    "app.security.graph.GraphClient"
)


class FakeAuthService:
    def get_token(self):
        return GraphToken(
            access_token="test-token",
            token_type="Bearer",
            expires_at=(
                datetime.now(timezone.utc)
                + timedelta(hours=1)
            ),
        )


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def _client():
    return GraphClient(
        auth_service=FakeAuthService(),
    )


@pytest.mark.parametrize(
    "next_link",
    [
        "http://graph.microsoft.com/v1.0/users?page=2",
        "https://evil.example/v1.0/users?page=2",
        "https://graph.microsoft.com:8443/v1.0/users?page=2",
        "https://graph.microsoft.com/beta/users?page=2",
    ],
)
def test_gate_rejects_unsafe_next_link(
    monkeypatch,
    next_link,
):
    def fake_get(url, **kwargs):
        return FakeResponse(
            {
                "value": [{"id": "user-1"}],
                "@odata.nextLink": next_link,
            }
        )

    monkeypatch.setattr(
        graph_client_module.httpx,
        "get",
        fake_get,
    )

    with pytest.raises(ValueError):
        _client().get_collection("/users")


@pytest.mark.parametrize(
    "next_link",
    [
        "",
        " ",
        123,
        [],
        {},
    ],
)
def test_gate_rejects_malformed_next_link(
    monkeypatch,
    next_link,
):
    def fake_get(url, **kwargs):
        return FakeResponse(
            {
                "value": [],
                "@odata.nextLink": next_link,
            }
        )

    monkeypatch.setattr(
        graph_client_module.httpx,
        "get",
        fake_get,
    )

    with pytest.raises(
        ValueError,
        match="@odata.nextLink",
    ):
        _client().get_collection("/users")


def test_gate_rejects_repeated_next_link(monkeypatch):
    repeated = (
        "https://graph.microsoft.com/v1.0/users?page=2"
    )

    calls = 0

    def fake_get(url, **kwargs):
        nonlocal calls
        calls += 1

        return FakeResponse(
            {
                "value": [],
                "@odata.nextLink": repeated,
            }
        )

    monkeypatch.setattr(
        graph_client_module.httpx,
        "get",
        fake_get,
    )

    with pytest.raises(
        ValueError,
        match="repeated",
    ):
        _client().get_collection("/users")

    assert calls == 2


def test_gate_enforces_page_limit(monkeypatch):
    calls = 0

    def fake_get(url, **kwargs):
        nonlocal calls
        calls += 1

        return FakeResponse(
            {
                "value": [],
                "@odata.nextLink": (
                    "https://graph.microsoft.com/v1.0/users"
                    f"?page={calls + 1}"
                ),
            }
        )

    monkeypatch.setattr(
        graph_client_module.httpx,
        "get",
        fake_get,
    )

    with pytest.raises(
        ValueError,
        match="page limit",
    ):
        _client().get_collection(
            "/users",
            max_pages=2,
        )


def test_gate_rejects_invalid_max_pages():
    with pytest.raises(
        ValueError,
        match="max_pages",
    ):
        _client().get_collection(
            "/users",
            max_pages=0,
        )


def test_gate_rejects_invalid_continuation_payload(
    monkeypatch,
):
    first_url = (
        "https://graph.microsoft.com/v1.0/users"
    )
    next_url = (
        "https://graph.microsoft.com/v1.0/users?page=2"
    )

    def fake_get(url, **kwargs):
        if url == first_url:
            return FakeResponse(
                {
                    "value": [],
                    "@odata.nextLink": next_url,
                }
            )

        return FakeResponse(["not-an-object"])

    monkeypatch.setattr(
        graph_client_module.httpx,
        "get",
        fake_get,
    )

    with pytest.raises(
        ValueError,
        match="continuation response format",
    ):
        _client().get_collection("/users")
