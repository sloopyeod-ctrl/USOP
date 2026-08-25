from __future__ import annotations

import inspect

import pytest

from app.connectors.microsoft.EntraProvider import EntraProvider
from app.domain.principal_type import PrincipalType


class FakeGraphClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict | None]] = []

    def get_collection(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> list[dict]:
        self.calls.append((endpoint, params))
        return [
            {
                "id": "assignment-1",
                "principalId": "principal-1",
                "roleDefinitionId": "role-1",
                "directoryScopeId": "/",
                "appScopeId": None,
                "principal": {
                    "@odata.type": "#microsoft.graph.user",
                    "id": "principal-1",
                },
            }
        ]

    def get(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> dict:
        self.calls.append((endpoint, params))
        return {
            "value": [
                {
                    "id": "assignment-1",
                    "principalId": "principal-1",
                    "roleDefinitionId": "role-1",
                    "directoryScopeId": "/",
                    "appScopeId": None,
                    "principal": {
                        "@odata.type": "#microsoft.graph.user",
                        "id": "principal-1",
                    },
                }
            ]
        }


def _provider_without_constructor() -> EntraProvider:
    return object.__new__(EntraProvider)


def test_role_assignment_collection_expands_principal() -> None:
    provider = _provider_without_constructor()
    graph = FakeGraphClient()
    provider.graph = graph

    records = provider._collect_live_role_assignment_records()

    assert len(records) == 1
    assert graph.calls == [
        (
            "/roleManagement/directory/roleAssignments",
            {"$expand": "principal"},
        )
    ]


@pytest.mark.parametrize(
    ("odata_type", "expected_type"),
    [
        ("#microsoft.graph.user", PrincipalType.ACCOUNT),
        ("#microsoft.graph.group", PrincipalType.GROUP),
        (
            "#microsoft.graph.servicePrincipal",
            PrincipalType.SERVICE_PRINCIPAL,
        ),
    ],
)
def test_role_assignment_uses_expanded_principal_type(
    odata_type: str,
    expected_type: PrincipalType,
) -> None:
    provider = _provider_without_constructor()

    assignments = [
        {
            "id": "assignment-1",
            "principalId": "principal-1",
            "roleDefinitionId": "role-1",
            "directoryScopeId": "/",
            "appScopeId": None,
            "principal": {
                "@odata.type": odata_type,
                "id": "principal-1",
            },
        }
    ]
    role_definitions = {
        "role-1": {
            "id": "role-1",
            "displayName": "Example Role",
        }
    }

    result = provider._build_live_role_assignments(
        graph_assignments=assignments,
        graph_role_definitions=role_definitions,
    )

    assert len(result) == 1
    assert result[0]["subject_type"] == expected_type.value
    assert result[0]["subject_source_identifier"] == "principal-1"
    assert result[0]["role_source_identifier"] == "role-1"
    assert result[0]["assignment_type"] == "Direct"
    assert result[0]["status"] == "Active"
    assert result[0]["directory_scope"] == "/"
    assert result[0]["application_scope"] is None


def test_entra_provider_no_longer_uses_directory_objects_lookup() -> None:
    source = inspect.getsource(EntraProvider)

    assert "/directoryObjects/" not in source
