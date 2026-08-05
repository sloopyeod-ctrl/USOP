from app.main import app


BASE_PATH = (
    "/api/v1/organizations/"
    "{organization_id}/operational-timeline"
)

COLLECTION_PATH = BASE_PATH + "/"


def test_openapi_exposes_get_only():
    paths = app.openapi()["paths"]

    assert COLLECTION_PATH in paths
    assert set(paths[COLLECTION_PATH]) == {
        "get",
    }


def test_openapi_uses_canonical_result_contract():
    operation = app.openapi()["paths"][
        COLLECTION_PATH
    ]["get"]

    schema = (
        operation["responses"]["200"]
        ["content"]["application/json"]
        ["schema"]
    )

    assert schema["$ref"].endswith(
        "/OperationalTimelineResult"
    )


def test_openapi_exposes_complete_result_fields():
    schema = (
        app.openapi()["components"]["schemas"]
        ["OperationalTimelineResult"]
    )

    assert set(schema["properties"]) == {
        "organization_id",
        "events",
        "contributor_diagnostics",
        "warnings",
        "is_partial",
        "next_cursor",
        "generated_at",
        "schema_version",
    }


def test_openapi_exposes_canonical_event_fields():
    schema = (
        app.openapi()["components"]["schemas"]
        ["TimelineEvent"]
    )

    assert set(schema["properties"]) == {
        "event_id",
        "occurred_at",
        "category",
        "visibility",
        "title",
        "summary",
        "actor",
        "contributor_name",
        "contributor_version",
        "source_type",
        "source_id",
        "organization_id",
        "subject_references",
        "correlation_id",
        "metadata",
        "schema_version",
    }


def test_openapi_exposes_supported_query_parameters():
    operation = app.openapi()["paths"][
        COLLECTION_PATH
    ]["get"]

    names = {
        parameter["name"]
        for parameter in operation[
            "parameters"
        ]
    }

    assert names == {
        "organization_id",
        "identity_id",
        "work_item_id",
        "decision_id",
        "correlation_id",
        "category",
        "visibility",
        "start_at",
        "end_at",
        "cursor",
        "limit",
        "sort_direction",
    }


def test_openapi_excludes_mutation_methods():
    methods = app.openapi()["paths"][
        COLLECTION_PATH
    ]

    assert "post" not in methods
    assert "put" not in methods
    assert "patch" not in methods
    assert "delete" not in methods
