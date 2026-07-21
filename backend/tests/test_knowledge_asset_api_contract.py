from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import HTTPException, status

from app.api.v1 import knowledge_assets as api
from app.domain import (
    KnowledgeAssetStatus,
    KnowledgeCategory,
)
from app.main import app
from app.schemas.knowledge_asset import KnowledgeAssetCreate
from app.services.knowledge_asset_service import (
    KnowledgeAssetDuplicateVersionError,
    KnowledgeAssetOrganizationNotFoundError,
    KnowledgeAssetValidationError,
)


BASE_PATH = (
    "/api/v1/organizations/"
    "{organization_id}/knowledge-assets"
)

COLLECTION_PATH = BASE_PATH + "/"
ITEM_PATH = BASE_PATH + "/{knowledge_asset_id}"


def create_payload() -> KnowledgeAssetCreate:
    return KnowledgeAssetCreate.model_validate(
        {
            "title": "Global Administrator elevation review",
            "guidance": (
                "Require explicit analyst review for material "
                "privilege elevation."
            ),
            "category": KnowledgeCategory.AUTHORIZATION,
            "status": KnowledgeAssetStatus.UNDER_REVIEW,
            "summary": "Review privileged authorization changes.",
            "source_system": "MicrosoftEntraID",
            "source_identifier": "role-assignment-001",
            "confidence_score": 95,
        }
    )


def knowledge_asset_record():
    timestamp = datetime.now(UTC)

    return SimpleNamespace(
        id="knowledge-asset-001",
        organization_id="organization-001",
        title="Global Administrator elevation review",
        summary="Review privileged authorization changes.",
        guidance=(
            "Require explicit analyst review for material "
            "privilege elevation."
        ),
        category=KnowledgeCategory.AUTHORIZATION.value,
        status=KnowledgeAssetStatus.UNDER_REVIEW.value,
        version=1,
        source_system="MicrosoftEntraID",
        source_identifier="role-assignment-001",
        confidence_score=95,
        created_at=timestamp,
        updated_at=timestamp,
        created_by=None,
        updated_by=None,
        is_active=True,
    )


def install_service(monkeypatch, service: Mock):
    service_factory = Mock(return_value=service)

    monkeypatch.setattr(
        api,
        "KnowledgeAssetService",
        service_factory,
    )

    return service_factory


def test_openapi_exposes_exact_knowledge_asset_methods():
    paths = app.openapi()["paths"]

    assert set(paths[COLLECTION_PATH]) == {
        "get",
        "post",
    }

    assert set(paths[ITEM_PATH]) == {
        "get",
    }


def test_openapi_uses_canonical_response_models():
    paths = app.openapi()["paths"]

    post_operation = paths[COLLECTION_PATH]["post"]
    list_operation = paths[COLLECTION_PATH]["get"]
    get_operation = paths[ITEM_PATH]["get"]

    assert "201" in post_operation["responses"]
    assert "200" in list_operation["responses"]
    assert "200" in get_operation["responses"]

    post_schema = (
        post_operation["responses"]["201"]
        ["content"]["application/json"]["schema"]
    )

    list_schema = (
        list_operation["responses"]["200"]
        ["content"]["application/json"]["schema"]
    )

    get_schema = (
        get_operation["responses"]["200"]
        ["content"]["application/json"]["schema"]
    )

    assert post_schema["$ref"].endswith(
        "/KnowledgeAssetRead"
    )

    assert list_schema["type"] == "array"
    assert list_schema["items"]["$ref"].endswith(
        "/KnowledgeAssetRead"
    )

    assert get_schema["$ref"].endswith(
        "/KnowledgeAssetRead"
    )


def test_openapi_create_body_excludes_server_authority():
    schema = (
        app.openapi()["components"]["schemas"]
        ["KnowledgeAssetCreate"]
    )

    properties = set(schema["properties"])

    assert "organization_id" not in properties
    assert "actor" not in properties
    assert "version" not in properties
    assert "created_by" not in properties
    assert "updated_by" not in properties


def test_create_delegates_complete_contract_to_service(
    monkeypatch,
):
    expected = knowledge_asset_record()
    service = Mock()
    service.create.return_value = expected

    service_factory = install_service(
        monkeypatch,
        service,
    )

    db = object()
    data = create_payload()

    result = api.create_knowledge_asset(
        organization_id="organization-001",
        data=data,
        db=db,
    )

    service_factory.assert_called_once_with(db)

    service.create.assert_called_once_with(
        organization_id="organization-001",
        title=data.title,
        guidance=data.guidance,
        category=data.category,
        status=data.status,
        summary=data.summary,
        source_system=data.source_system,
        source_identifier=data.source_identifier,
        confidence_score=data.confidence_score,
    )

    assert result is expected


@pytest.mark.parametrize(
    ("service_error", "expected_status"),
    [
        (
            KnowledgeAssetOrganizationNotFoundError(
                "Unknown Organization."
            ),
            status.HTTP_404_NOT_FOUND,
        ),
        (
            KnowledgeAssetValidationError(
                "Invalid KnowledgeAsset."
            ),
            status.HTTP_400_BAD_REQUEST,
        ),
        (
            KnowledgeAssetDuplicateVersionError(
                "Duplicate KnowledgeAsset version."
            ),
            status.HTTP_409_CONFLICT,
        ),
    ],
)
def test_create_translates_service_errors(
    monkeypatch,
    service_error,
    expected_status: int,
):
    service = Mock()
    service.create.side_effect = service_error

    install_service(monkeypatch, service)

    with pytest.raises(HTTPException) as caught:
        api.create_knowledge_asset(
            organization_id="organization-001",
            data=create_payload(),
            db=object(),
        )

    assert caught.value.status_code == expected_status
    assert caught.value.detail == str(service_error)


def test_list_delegates_to_organization_scoped_service(
    monkeypatch,
):
    expected = [knowledge_asset_record()]
    service = Mock()
    service.list_for_organization.return_value = expected

    service_factory = install_service(
        monkeypatch,
        service,
    )

    db = object()

    result = api.list_knowledge_assets(
        organization_id="organization-001",
        db=db,
    )

    service_factory.assert_called_once_with(db)

    service.list_for_organization.assert_called_once_with(
        "organization-001"
    )

    assert result is expected


def test_list_translates_unknown_organization(
    monkeypatch,
):
    error = KnowledgeAssetOrganizationNotFoundError(
        "Unknown Organization."
    )

    service = Mock()
    service.list_for_organization.side_effect = error

    install_service(monkeypatch, service)

    with pytest.raises(HTTPException) as caught:
        api.list_knowledge_assets(
            organization_id="organization-001",
            db=object(),
        )

    assert (
        caught.value.status_code
        == status.HTTP_404_NOT_FOUND
    )
    assert caught.value.detail == str(error)


def test_get_delegates_to_organization_scoped_service(
    monkeypatch,
):
    expected = knowledge_asset_record()
    service = Mock()
    service.get_by_id.return_value = expected

    service_factory = install_service(
        monkeypatch,
        service,
    )

    db = object()

    result = api.get_knowledge_asset(
        organization_id="organization-001",
        knowledge_asset_id="knowledge-asset-001",
        db=db,
    )

    service_factory.assert_called_once_with(db)

    service.get_by_id.assert_called_once_with(
        organization_id="organization-001",
        knowledge_asset_id="knowledge-asset-001",
    )

    assert result is expected


def test_get_translates_unknown_organization(
    monkeypatch,
):
    error = KnowledgeAssetOrganizationNotFoundError(
        "Unknown Organization."
    )

    service = Mock()
    service.get_by_id.side_effect = error

    install_service(monkeypatch, service)

    with pytest.raises(HTTPException) as caught:
        api.get_knowledge_asset(
            organization_id="organization-001",
            knowledge_asset_id="knowledge-asset-001",
            db=object(),
        )

    assert (
        caught.value.status_code
        == status.HTTP_404_NOT_FOUND
    )
    assert caught.value.detail == str(error)


def test_get_returns_not_found_for_missing_scoped_asset(
    monkeypatch,
):
    service = Mock()
    service.get_by_id.return_value = None

    install_service(monkeypatch, service)

    with pytest.raises(HTTPException) as caught:
        api.get_knowledge_asset(
            organization_id="organization-001",
            knowledge_asset_id="knowledge-asset-001",
            db=object(),
        )

    assert (
        caught.value.status_code
        == status.HTTP_404_NOT_FOUND
    )

    assert (
        caught.value.detail
        == "Knowledge Asset not found."
    )


def test_router_does_not_expose_mutation_methods_beyond_create():
    paths = app.openapi()["paths"]

    assert "put" not in paths[COLLECTION_PATH]
    assert "patch" not in paths[COLLECTION_PATH]
    assert "delete" not in paths[COLLECTION_PATH]

    assert "post" not in paths[ITEM_PATH]
    assert "put" not in paths[ITEM_PATH]
    assert "patch" not in paths[ITEM_PATH]
    assert "delete" not in paths[ITEM_PATH]
