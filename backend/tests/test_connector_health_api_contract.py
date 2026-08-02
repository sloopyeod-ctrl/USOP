from app.main import app


COLLECTION_PATH = "/connectors/health"


def test_openapi_exposes_connector_health_as_get_only():
    openapi = app.openapi()

    assert COLLECTION_PATH in openapi["paths"]

    methods = set(
        openapi["paths"][
            COLLECTION_PATH
        ].keys()
    )

    assert methods == {
        "get",
    }


def test_openapi_uses_connector_health_response_model():
    openapi = app.openapi()

    operation = openapi["paths"][
        COLLECTION_PATH
    ]["get"]

    response_schema = operation[
        "responses"
    ]["200"]["content"][
        "application/json"
    ]["schema"]

    assert response_schema["type"] == "array"

    assert response_schema["items"] == {
        "$ref": (
            "#/components/schemas/"
            "ConnectorHealthRead"
        )
    }


def test_openapi_connector_health_has_exact_fields():
    openapi = app.openapi()

    schema = openapi[
        "components"
    ]["schemas"][
        "ConnectorHealthRead"
    ]

    properties = set(
        schema["properties"].keys()
    )

    assert properties == {
        "provider_name",
        "healthy",
        "status",
        "checked_at",
        "details",
    }

    assert set(
        schema["required"]
    ) == properties


def test_openapi_health_excludes_unproven_operational_history():
    openapi = app.openapi()

    properties = openapi[
        "components"
    ]["schemas"][
        "ConnectorHealthRead"
    ]["properties"]

    prohibited_fields = {
        "last_sync",
        "last_synchronized_at",
        "next_sync",
        "records_collected",
        "records_normalized",
        "records_synchronized",
        "duration_seconds",
        "remediation_verified",
    }

    assert prohibited_fields.isdisjoint(
        properties
    )


def test_static_health_route_is_not_connector_collect_route():
    openapi = app.openapi()

    assert "/connectors/health" in openapi["paths"]

    assert (
        "/connectors/"
        "{connector_name}/collect"
    ) in openapi["paths"]

    assert set(
        openapi["paths"][
            "/connectors/health"
        ].keys()
    ) == {
        "get",
    }