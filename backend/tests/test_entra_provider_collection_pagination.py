from app.connectors.microsoft.EntraProvider import EntraProvider


class FakeGraphClient:
    def __init__(self):
        self.collection_calls = []
        self.get_calls = []
        self.collections = {}
        self.objects = {}

    def get_collection(self, endpoint, params=None):
        self.collection_calls.append((endpoint, params))
        return list(self.collections.get(endpoint, []))

    def get(self, endpoint, params=None):
        self.get_calls.append((endpoint, params))
        return self.objects.get(endpoint, {})


def _provider(graph=None):
    graph = graph or FakeGraphClient()
    return EntraProvider(graph_client=graph), graph


def test_users_use_complete_collection_contract():
    provider, graph = _provider()
    graph.collections["/users"] = [
        {"id": "user-1"},
        {"id": "user-2"},
    ]

    records = provider._collect_live_user_records()

    assert records == [
        {"id": "user-1"},
        {"id": "user-2"},
    ]
    assert graph.collection_calls[0][0] == "/users"
    assert graph.get_calls == []


def test_groups_use_complete_collection_contract():
    provider, graph = _provider()
    graph.collections["/groups"] = [
        {"id": "group-1"},
        {"id": "group-2"},
    ]

    records = provider._collect_live_group_records()

    assert records == [
        {"id": "group-1"},
        {"id": "group-2"},
    ]
    assert graph.collection_calls[0][0] == "/groups"
    assert graph.get_calls == []


def test_direct_members_use_complete_collection_contract():
    provider, graph = _provider()
    endpoint = "/groups/group-1/members"
    graph.collections[endpoint] = [
        {"id": "member-1"},
        {"id": "member-2"},
    ]

    records = provider._collect_live_group_member_records(
        {"id": "group-1", "displayName": "Security"}
    )

    assert records == [
        {"id": "member-1"},
        {"id": "member-2"},
    ]
    assert graph.collection_calls[0][0] == endpoint
    assert "transitiveMembers" not in endpoint
    assert graph.get_calls == []


def test_missing_group_id_does_not_call_graph():
    provider, graph = _provider()

    assert provider._collect_live_group_member_records({}) == []
    assert graph.collection_calls == []
    assert graph.get_calls == []


def test_role_assignments_use_complete_collection_contract():
    provider, graph = _provider()
    endpoint = "/roleManagement/directory/roleAssignments"
    graph.collections[endpoint] = [
        {"id": "assignment-1"},
        {"id": "assignment-2"},
    ]

    records = provider._collect_live_role_assignment_records()

    assert records == [
        {"id": "assignment-1"},
        {"id": "assignment-2"},
    ]
    assert graph.collection_calls[0][0] == endpoint
    assert graph.get_calls == []


def test_role_definition_remains_single_object_read():
    provider, graph = _provider()
    endpoint = (
        "/roleManagement/directory/"
        "roleDefinitions/role-1"
    )
    graph.objects[endpoint] = {
        "id": "role-1",
        "displayName": "Global Administrator",
    }

    record = provider._collect_live_role_definition_record(
        "role-1"
    )

    assert record["id"] == "role-1"
    assert graph.get_calls == [(endpoint, None)]
    assert graph.collection_calls == []


def test_large_user_collection_is_not_truncated():
    provider, graph = _provider()
    graph.collections["/users"] = [
        {"id": f"user-{index}"}
        for index in range(143)
    ]

    records = provider._collect_live_user_records()

    assert len(records) == 143
    assert records[0]["id"] == "user-0"
    assert records[-1]["id"] == "user-142"


def test_all_supported_collections_use_collection_boundary():
    provider, graph = _provider()

    graph.collections["/users"] = []
    graph.collections["/groups"] = []
    graph.collections[
        "/roleManagement/directory/roleAssignments"
    ] = []

    provider._collect_live_user_records()
    provider._collect_live_group_records()
    provider._collect_live_group_member_records(
        {"id": "group-1"}
    )
    provider._collect_live_role_assignment_records()

    endpoints = [
        endpoint
        for endpoint, _ in graph.collection_calls
    ]

    assert endpoints == [
        "/users",
        "/groups",
        "/groups/group-1/members",
        "/roleManagement/directory/roleAssignments",
    ]
