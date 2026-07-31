from app.main import app


COLLECTION_PATH = "/connectors/providers"


def test_openapi_exposes_provider_catalog_as_get_only():
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


def test_openapi_uses_provider_descriptor_response_model():
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
            "ProviderDescriptorRead"
        )
    }


def test_openapi_provider_descriptor_has_exact_fields():
    openapi = app.openapi()

    schema = openapi[
        "components"
    ]["schemas"][
        "ProviderDescriptorRead"
    ]

    properties = set(
        schema["properties"].keys()
    )

    assert properties == {
        "provider_name",
        "display_name",
        "vendor",
        "component_version",
        "intelligence_domains",
        "capabilities",
        "supported_modes",
    }

    assert set(
        schema["required"]
    ) == properties


def test_openapi_provider_descriptor_excludes_runtime_state():
    openapi = app.openapi()

    properties = openapi[
        "components"
    ]["schemas"][
        "ProviderDescriptorRead"
    ]["properties"]

    prohibited_fields = {
        "enabled",
        "healthy",
        "authenticated",
        "configured",
        "licensed",
        "last_sync",
        "last_synchronized_at",
        "credentials",
        "secrets",
        "settings",
        "environment",
    }

    assert prohibited_fields.isdisjoint(
        properties
    )


def test_existing_connector_collection_route_remains_available():
    openapi = app.openapi()

    collection_path = (
        "/connectors/"
        "{connector_name}/collect"
    )

    assert collection_path in openapi["paths"]

    assert set(
        openapi["paths"][
            collection_path
        ].keys()
    ) == {
        "get",
    }


def test_existing_connector_synchronization_route_remains_available():
    openapi = app.openapi()

    synchronization_path = (
        "/connectors/"
        "{connector_name}/synchronize"
    )

    assert synchronization_path in openapi["paths"]

    assert set(
        openapi["paths"][
            synchronization_path
        ].keys()
    ) == {
        "post",
    }
