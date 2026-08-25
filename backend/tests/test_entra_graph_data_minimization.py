from app.connectors.microsoft.EntraProvider import EntraProvider


class RecordingGraphClient:
    def __init__(self):
        self.calls = []

    def get_collection(self, endpoint, params=None):
        self.calls.append((endpoint, params))
        return []


def _provider():
    graph = RecordingGraphClient()
    return EntraProvider(graph_client=graph), graph


def test_group_collection_requests_only_operational_fields():
    provider, graph = _provider()
    provider._collect_live_group_records()

    endpoint, params = graph.calls[0]
    assert endpoint == "/groups"
    assert params["$select"] == (
        "id,"
        "displayName,"
        "description,"
        "securityEnabled,"
        "mailEnabled,"
        "groupTypes,"
    )


def test_group_collection_excludes_unused_dynamic_fields():
    provider, graph = _provider()
    provider._collect_live_group_records()

    selected = graph.calls[0][1]["$select"]
    assert "membershipRule" not in selected
    assert "membershipRuleProcessingState" not in selected


def test_member_collection_requests_only_relationship_identity():
    provider, graph = _provider()
    provider._collect_live_group_member_records(
        {"id": "group-1"}
    )

    endpoint, params = graph.calls[0]
    assert endpoint == "/groups/group-1/members"
    assert params["$select"] == (
        "id,"
    )


def test_member_collection_excludes_unused_rich_properties():
    provider, graph = _provider()
    provider._collect_live_group_member_records(
        {"id": "group-1"}
    )

    selected = graph.calls[0][1]["$select"]

    for unused in (
        "displayName",
        "userPrincipalName",
        "appId",
        "deviceId",
    ):
        assert unused not in selected


def test_membership_builder_needs_only_id_and_odata_type():
    provider, _ = _provider()

    membership = provider._build_live_membership(
        member={
            "id": "principal-1",
            "@odata.type": "#microsoft.graph.servicePrincipal",
        },
        group_source_identifier="group-1",
    )

    assert membership is not None
    assert membership["subject_source_identifier"] == "principal-1"
    assert membership["subject_type"] == "ServicePrincipal"
    assert membership["membership_type"] == "Direct"
