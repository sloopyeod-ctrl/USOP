from unittest.mock import Mock

import pytest
from fastapi import (
    HTTPException,
    status,
)

from app.api.v1 import (
    decision_drafts as api,
)
from app.domain import DecisionType
from app.intelligence.decision_knowledge_intelligence_service import (
    DecisionKnowledgeIntelligenceIntegrityError,
)
from app.intelligence.drafting import (
    DecisionDraft,
    DecisionDraftEvidence,
    DecisionDraftIdentityNotFoundError,
    DecisionDraftIntelligenceValidationError,
    DecisionDraftRecommendationNotFoundError,
    DecisionDraftSegment,
)
from app.main import app
from app.schemas.decision_draft import (
    DecisionDraftProfile,
    DecisionDraftRead,
    DecisionDraftRequest,
)
from app.services.decision_knowledge_service import (
    DecisionKnowledgeDecisionNotFoundError,
)


BASE_PATH = (
    "/api/v1/organizations/"
    "{organization_id}/identities/"
    "{identity_id}/recommendations/"
    "{recommendation_id}/draft"
)

COLLECTION_PATH = BASE_PATH + "/"


def draft() -> DecisionDraft:
    evidence = DecisionDraftEvidence(
        source_type="Recommendation",
        source_id="recommendation-001",
        label=(
            "Remove unnecessary "
            "privileged access"
        ),
        detail=(
            "Remove the observed "
            "privileged authorization."
        ),
    )

    segment = DecisionDraftSegment(
        text=(
            "The selected organizational "
            "response addresses the "
            "recommendation."
        ),
        evidence=(
            evidence,
        ),
    )

    return DecisionDraft(
        decision_type="CorrectRisk",
        justification_segments=(
            segment,
        ),
        notes_segments=(),
        confidence_score=40,
    )


def request() -> DecisionDraftRequest:
    return DecisionDraftRequest(
        decision_type=(
            DecisionType.CORRECT_RISK
        ),
        draft_profile=(
            DecisionDraftProfile.DEFAULT
        ),
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
        "DecisionDraftIntelligenceService",
        service_factory,
    )

    return service_factory


def test_openapi_exposes_exact_draft_method():
    methods = app.openapi()["paths"][
        COLLECTION_PATH
    ]

    assert set(methods) == {
        "post",
    }


def test_openapi_uses_draft_request_and_response_contracts():
    operation = app.openapi()["paths"][
        COLLECTION_PATH
    ]["post"]

    request_schema = (
        operation["requestBody"]
        ["content"]["application/json"]
        ["schema"]
    )

    response_schema = (
        operation["responses"]["200"]
        ["content"]["application/json"]
        ["schema"]
    )

    assert request_schema[
        "$ref"
    ].endswith(
        "/DecisionDraftRequest"
    )

    assert response_schema[
        "$ref"
    ].endswith(
        "/DecisionDraftRead"
    )


def test_openapi_exposes_complete_draft_response():
    schema = (
        app.openapi()["components"]["schemas"]
        ["DecisionDraftRead"]
    )

    assert set(
        schema["properties"]
    ) == {
        "decision_type",
        "draft_profile",
        "suggested_justification",
        "suggested_notes",
        "justification_segments",
        "notes_segments",
        "evidence_used",
        "confidence_score",
        "construction_version",
        "metadata",
    }


def test_openapi_request_excludes_server_authority():
    schema = (
        app.openapi()["components"]["schemas"]
        ["DecisionDraftRequest"]
    )

    properties = set(
        schema["properties"]
    )

    assert properties == {
        "decision_type",
        "draft_profile",
    }

    assert "organization_id" not in properties
    assert "identity_id" not in properties
    assert "recommendation_id" not in properties
    assert "confidence_score" not in properties
    assert "suggested_justification" not in properties


def test_create_delegates_complete_scope(
    monkeypatch,
):
    expected_draft = draft()

    service = Mock()
    service.build_for_recommendation.return_value = (
        expected_draft
    )

    service_factory = install_service(
        monkeypatch,
        service,
    )

    db = object()
    data = request()

    result = api.create_decision_draft(
        organization_id="organization-001",
        identity_id="identity-001",
        recommendation_id=(
            "recommendation-001"
        ),
        data=data,
        db=db,
    )

    service_factory.assert_called_once_with(
        db=db
    )

    (
        service.build_for_recommendation
        .assert_called_once_with(
            organization_id=(
                "organization-001"
            ),
            identity_id="identity-001",
            recommendation_id=(
                "recommendation-001"
            ),
            decision_type=(
                DecisionType.CORRECT_RISK
            ),
        )
    )

    assert isinstance(
        result,
        DecisionDraftRead,
    )

    assert result.decision_type == (
        DecisionType.CORRECT_RISK
    )

    assert result.draft_profile == (
        DecisionDraftProfile.DEFAULT
    )


def test_create_projects_complete_transport_contract(
    monkeypatch,
):
    service = Mock()
    service.build_for_recommendation.return_value = (
        draft()
    )

    install_service(
        monkeypatch,
        service,
    )

    result = api.create_decision_draft(
        organization_id="organization-001",
        identity_id="identity-001",
        recommendation_id=(
            "recommendation-001"
        ),
        data=request(),
        db=object(),
    )

    assert result.suggested_justification == (
        "The selected organizational "
        "response addresses the "
        "recommendation."
    )

    assert result.suggested_notes == ""

    assert len(
        result.justification_segments
    ) == 1

    assert len(
        result.evidence_used
    ) == 1

    assert result.confidence_score == 40

    assert (
        result.metadata
        .justification_segment_count
        == 1
    )

    assert (
        result.metadata.evidence_count
        == 1
    )


@pytest.mark.parametrize(
    (
        "service_error",
        "expected_status",
    ),
    [
        (
            DecisionDraftIntelligenceValidationError(
                "Organization identifier "
                "is required."
            ),
            status.HTTP_400_BAD_REQUEST,
        ),
        (
            DecisionDraftIdentityNotFoundError(
                "Identity intelligence "
                "was not found."
            ),
            status.HTTP_404_NOT_FOUND,
        ),
        (
            DecisionDraftRecommendationNotFoundError(
                "Recommendation was "
                "not found."
            ),
            status.HTTP_404_NOT_FOUND,
        ),
        (
            DecisionKnowledgeDecisionNotFoundError(
                "DecisionRecord was "
                "not found."
            ),
            status.HTTP_404_NOT_FOUND,
        ),
        (
            DecisionKnowledgeIntelligenceIntegrityError(
                "Knowledge relationship "
                "could not be resolved."
            ),
            status.HTTP_409_CONFLICT,
        ),
    ],
)
def test_create_translates_service_errors(
    monkeypatch,
    service_error,
    expected_status,
):
    service = Mock()

    (
        service.build_for_recommendation
        .side_effect
    ) = service_error

    install_service(
        monkeypatch,
        service,
    )

    with pytest.raises(
        HTTPException
    ) as caught:
        api.create_decision_draft(
            organization_id=(
                "organization-001"
            ),
            identity_id="identity-001",
            recommendation_id=(
                "recommendation-001"
            ),
            data=request(),
            db=object(),
        )

    assert (
        caught.value.status_code
        == expected_status
    )

    assert (
        caught.value.detail
        == str(service_error)
    )


def test_router_exposes_no_other_methods():
    methods = app.openapi()["paths"][
        COLLECTION_PATH
    ]

    assert "get" not in methods
    assert "put" not in methods
    assert "patch" not in methods
    assert "delete" not in methods
