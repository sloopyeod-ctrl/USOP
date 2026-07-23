from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import HTTPException, status

from app.api.v1 import decision_knowledge as api
from app.intelligence.decision_knowledge_intelligence_service import (
    DecisionKnowledgeIntelligenceIntegrityError,
)
from app.domain import KnowledgeRelationshipType
from app.main import app
from app.schemas.decision_knowledge import (
    DecisionKnowledgeCreate,
)
from app.services.decision_knowledge_service import (
    DecisionKnowledgeAssetNotFoundError,
    DecisionKnowledgeDecisionNotFoundError,
    DecisionKnowledgeDuplicateError,
    DecisionKnowledgeValidationError,
)


BASE_PATH = (
    "/api/v1/organizations/"
    "{organization_id}/decision-records/"
    "{decision_record_id}/knowledge"
)

COLLECTION_PATH = BASE_PATH + "/"


def create_payload() -> DecisionKnowledgeCreate:
    return DecisionKnowledgeCreate.model_validate(
        {
            "knowledge_asset_id": "knowledge-asset-001",
            "relationship_type": (
                KnowledgeRelationshipType.PRIMARY_GUIDANCE
            ),
        }
    )


def relationship_record():
    timestamp = datetime.now(UTC)

    return SimpleNamespace(
        id="relationship-001",
        decision_record_id="decision-001",
        knowledge_asset_id="knowledge-asset-001",
        relationship_type="PrimaryGuidance",
        created_at=timestamp,
        updated_at=timestamp,
        created_by=None,
        updated_by=None,
        is_active=True,
    )


def install_service(
    monkeypatch,
    service: Mock,
):
    service_factory = Mock(
        return_value=service
    )

    monkeypatch.setattr(
        api,
        "DecisionKnowledgeService",
        service_factory,
    )

    return service_factory


def install_intelligence_service(
    monkeypatch,
    service: Mock,
):
    service_factory = Mock(
        return_value=service
    )

    monkeypatch.setattr(
        api,
        "DecisionKnowledgeIntelligenceService",
        service_factory,
    )

    return service_factory


def test_openapi_exposes_exact_decision_knowledge_methods():
    paths = app.openapi()["paths"]

    assert set(paths[COLLECTION_PATH]) == {
        "get",
        "post",
    }


def test_openapi_uses_canonical_response_models():
    operation = app.openapi()["paths"][COLLECTION_PATH]

    post_schema = (
        operation["post"]["responses"]["201"]
        ["content"]["application/json"]["schema"]
    )

    list_schema = (
        operation["get"]["responses"]["200"]
        ["content"]["application/json"]["schema"]
    )

    assert post_schema["$ref"].endswith(
        "/DecisionKnowledgeRead"
    )

    assert list_schema["type"] == "array"
    assert list_schema["items"]["$ref"].endswith(
        "/DecisionKnowledgeIntelligenceRead"
    )


def test_openapi_create_body_excludes_server_authority():
    schema = (
        app.openapi()["components"]["schemas"]
        ["DecisionKnowledgeCreate"]
    )

    properties = set(schema["properties"])

    assert properties == {
        "knowledge_asset_id",
        "relationship_type",
    }

    assert "organization_id" not in properties
    assert "decision_record_id" not in properties
    assert "actor" not in properties
    assert "created_by" not in properties
    assert "updated_by" not in properties


def test_create_delegates_complete_contract_to_service(
    monkeypatch,
):
    expected = relationship_record()
    service = Mock()
    service.create.return_value = expected

    service_factory = install_service(
        monkeypatch,
        service,
    )

    db = object()
    data = create_payload()

    result = api.create_decision_knowledge(
        organization_id="organization-001",
        decision_record_id="decision-001",
        data=data,
        db=db,
    )

    service_factory.assert_called_once_with(db)

    service.create.assert_called_once_with(
        organization_id="organization-001",
        decision_record_id="decision-001",
        knowledge_asset_id=data.knowledge_asset_id,
        relationship_type=data.relationship_type,
    )

    assert result is expected


@pytest.mark.parametrize(
    ("service_error", "expected_status"),
    [
        (
            DecisionKnowledgeDecisionNotFoundError(
                "DecisionRecord not found."
            ),
            status.HTTP_404_NOT_FOUND,
        ),
        (
            DecisionKnowledgeAssetNotFoundError(
                "KnowledgeAsset not found."
            ),
            status.HTTP_404_NOT_FOUND,
        ),
        (
            DecisionKnowledgeValidationError(
                "Invalid relationship."
            ),
            status.HTTP_400_BAD_REQUEST,
        ),
        (
            DecisionKnowledgeDuplicateError(
                "Duplicate relationship."
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

    install_service(
        monkeypatch,
        service,
    )

    with pytest.raises(HTTPException) as caught:
        api.create_decision_knowledge(
            organization_id="organization-001",
            decision_record_id="decision-001",
            data=create_payload(),
            db=object(),
        )

    assert caught.value.status_code == expected_status
    assert caught.value.detail == str(service_error)


def test_list_delegates_to_scoped_service(
    monkeypatch,
):
    expected = [
        relationship_record(),
    ]

    service = Mock()
    service.list_for_decision.return_value = expected

    service_factory = install_intelligence_service(
        monkeypatch,
        service,
    )

    db = object()

    result = api.list_decision_knowledge(
        organization_id="organization-001",
        decision_record_id="decision-001",
        db=db,
    )

    service_factory.assert_called_once_with(db)

    service.list_for_decision.assert_called_once_with(
        organization_id="organization-001",
        decision_record_id="decision-001",
    )

    assert result is expected


def test_list_translates_missing_scoped_decision(
    monkeypatch,
):
    error = DecisionKnowledgeDecisionNotFoundError(
        "DecisionRecord not found."
    )

    service = Mock()
    service.list_for_decision.side_effect = error

    install_intelligence_service(
        monkeypatch,
        service,
    )

    with pytest.raises(HTTPException) as caught:
        api.list_decision_knowledge(
            organization_id="organization-001",
            decision_record_id="decision-001",
            db=object(),
        )

    assert (
        caught.value.status_code
        == status.HTTP_404_NOT_FOUND
    )
    assert caught.value.detail == str(error)


def test_router_does_not_expose_other_mutation_methods():
    methods = app.openapi()["paths"][COLLECTION_PATH]

    assert "put" not in methods
    assert "patch" not in methods
    assert "delete" not in methods






def test_list_translates_projection_integrity_error(
    monkeypatch,
):
    error = DecisionKnowledgeIntelligenceIntegrityError(
        "Knowledge projection could not be assembled."
    )

    service = Mock()
    service.list_for_decision.side_effect = error

    install_intelligence_service(
        monkeypatch,
        service,
    )

    with pytest.raises(HTTPException) as caught:
        api.list_decision_knowledge(
            organization_id="organization-001",
            decision_record_id="decision-001",
            db=object(),
        )

    assert (
        caught.value.status_code
        == status.HTTP_409_CONFLICT
    )
    assert caught.value.detail == str(error)
