from datetime import datetime, timedelta, timezone

import pytest

from app.security.auth.GraphToken import GraphToken
from app.security.graph.GraphClient import GraphClient
import importlib

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


def test_collection_single_page(monkeypatch):
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return FakeResponse(
            {
                "value": [
                    {"id": "user-1"},
                    {"id": "user-2"},
                ]
            }
        )

    monkeypatch.setattr(
        graph_client_module.httpx,
        "get",
        fake_get,
    )

    records = _client().get_collection(
        "/users",
        params={"$top": 100},
    )

    assert records == [
        {"id": "user-1"},
        {"id": "user-2"},
    ]
    assert len(calls) == 1


def test_collection_follows_next_link(monkeypatch):
    first_url = "https://graph.microsoft.com/v1.0/users"
    second_url = (
        "https://graph.microsoft.com/v1.0/users"
        "?$skiptoken=page-2"
    )

    responses = {
        first_url: {
            "value": [{"id": "user-1"}],
            "@odata.nextLink": second_url,
        },
        second_url: {
            "value": [{"id": "user-2"}],
        },
    }

    calls = []

    def fake_get(url, **kwargs):
        calls.append(url)
        return FakeResponse(responses[url])

    monkeypatch.setattr(
        graph_client_module.httpx,
        "get",
        fake_get,
    )

    records = _client().get_collection("/users")

    assert records == [
        {"id": "user-1"},
        {"id": "user-2"},
    ]

    assert calls == [
        first_url,
        second_url,
    ]


def test_collection_follows_multiple_pages(monkeypatch):
    base = "https://graph.microsoft.com/v1.0/groups"

    responses = {
        base: {
            "value": [{"id": "group-1"}],
            "@odata.nextLink": base + "?page=2",
        },
        base + "?page=2": {
            "value": [{"id": "group-2"}],
            "@odata.nextLink": base + "?page=3",
        },
        base + "?page=3": {
            "value": [{"id": "group-3"}],
        },
    }

    def fake_get(url, **kwargs):
        return FakeResponse(responses[url])

    monkeypatch.setattr(
        graph_client_module.httpx,
        "get",
        fake_get,
    )

    assert _client().get_collection("/groups") == [
        {"id": "group-1"},
        {"id": "group-2"},
        {"id": "group-3"},
    ]


def test_collection_preserves_initial_params(monkeypatch):
    captured = []

    def fake_get(url, **kwargs):
        captured.append(
            (
                url,
                kwargs.get("params"),
            )
        )
        return FakeResponse({"value": []})

    monkeypatch.setattr(
        graph_client_module.httpx,
        "get",
        fake_get,
    )

    _client().get_collection(
        "/users",
        params={
            "$select": "id,displayName",
            "$top": 100,
        },
    )

    assert captured == [
        (
            "https://graph.microsoft.com/v1.0/users",
            {
                "$select": "id,displayName",
                "$top": 100,
            },
        )
    ]


def test_collection_rejects_invalid_value(monkeypatch):
    def fake_get(url, **kwargs):
        return FakeResponse({"value": "not-a-list"})

    monkeypatch.setattr(
        graph_client_module.httpx,
        "get",
        fake_get,
    )

    with pytest.raises(
        ValueError,
        match="valid value collection",
    ):
        _client().get_collection("/users")


def test_collection_rejects_non_object_record(monkeypatch):
    def fake_get(url, **kwargs):
        return FakeResponse(
            {
                "value": [
                    {"id": "user-1"},
                    "invalid",
                ]
            }
        )

    monkeypatch.setattr(
        graph_client_module.httpx,
        "get",
        fake_get,
    )

    with pytest.raises(
        ValueError,
        match="non-object record",
    ):
        _client().get_collection("/users")
