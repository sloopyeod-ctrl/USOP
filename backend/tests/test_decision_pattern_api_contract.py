from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from fastapi import HTTPException, status

from app.api.v1 import decision_patterns as api
from app.intelligence.decision_pattern_intelligence_service import (
    DecisionPatternIntelligenceValidationError,
)
from app.intelligence.patterns import (
    PatternResult,
)
from app.main import app
from app.schemas.decision_pattern import (
    DecisionPatternRead,
)


BASE_PATH = (
    "/api/v1/organizations/"
    "{organization_id}/identities/"
    "{identity_id}/recommendations/"
    "{recommendation_id}/patterns"
)

COLLECTION_PATH = BASE_PATH + "/"


def pattern_result() -> PatternResult:
    return PatternResult(
        pattern_type=(
            "RepeatedTemporaryAcceptance"
        ),
        title=(
            "Repeated Temporary Acceptance"
        ),
        summary=(
            "The organization recorded "
            "temporary risk acceptance twice "
            "for this recommendation."
        ),
        scope="Recommendation",
        metrics={
            "occurrence_count": 2,
            "scheduled_review_count": 2,
            (
                "average_scheduled_"
                "review_days"
            ): 90.0,
        },
        first_seen_at=datetime(
            2026,
            1,
            1,
            tzinfo=UTC,
        ),
        last_seen_at=datetime(
            2026,
            4,
            1,
            tzinfo=UTC,
        ),
        evidence_record_ids=(
            "decision-001",
            "decision-002",
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
        "DecisionPatternIntelligenceService",
        service_factory,
    )

    return service_factory


def test_openapi_exposes_exact_decision_pattern_methods():
    methods = app.openapi()["paths"][
        COLLECTION_PATH
    ]

    assert set(methods) == {
        "get",
    }


def test_openapi_uses_canonical_response_model():
    operation = app.openapi()["paths"][
        COLLECTION_PATH
    ]["get"]

    schema = (
        operation["responses"]["200"]
        ["content"]["application/json"]
        ["schema"]
    )

    assert schema["type"] == "array"

    assert schema["items"]["$ref"].endswith(
        "/DecisionPatternRead"
    )


def test_openapi_exposes_complete_read_contract():
    schema = (
        app.openapi()["components"]["schemas"]
        ["DecisionPatternRead"]
    )

    assert set(schema["properties"]) == {
        "pattern_type",
        "title",
        "summary",
        "scope",
        "metrics",
        "first_seen_at",
        "last_seen_at",
        "evidence_record_ids",
    }


def test_list_delegates_complete_scope_to_service(
    monkeypatch,
):
    service = Mock()
    service.analyze_recommendation.return_value = [
        pattern_result()
    ]

    service_factory = install_service(
        monkeypatch,
        service,
    )

    db = object()

    result = api.list_decision_patterns(
        organization_id="organization-001",
        identity_id="identity-001",
        recommendation_id=(
            "recommendation-001"
        ),
        db=db,
    )

    service_factory.assert_called_once_with(db)

    (
        service.analyze_recommendation
        .assert_called_once_with(
            organization_id=(
                "organization-001"
            ),
            identity_id="identity-001",
            recommendation_id=(
                "recommendation-001"
            ),
        )
    )

    assert len(result) == 1
    assert isinstance(
        result[0],
        DecisionPatternRead,
    )


def test_list_projects_internal_pattern_contract(
    monkeypatch,
):
    expected = pattern_result()

    service = Mock()
    service.analyze_recommendation.return_value = [
        expected
    ]

    install_service(
        monkeypatch,
        service,
    )

    result = api.list_decision_patterns(
        organization_id="organization-001",
        identity_id="identity-001",
        recommendation_id=(
            "recommendation-001"
        ),
        db=object(),
    )

    projection = result[0]

    assert (
        projection.pattern_type
        == expected.pattern_type
    )
    assert projection.title == expected.title
    assert projection.summary == expected.summary
    assert projection.scope == expected.scope

    assert projection.metrics == {
        "occurrence_count": 2,
        "scheduled_review_count": 2,
        (
            "average_scheduled_"
            "review_days"
        ): 90.0,
    }

    assert (
        projection.first_seen_at
        == expected.first_seen_at
    )
    assert (
        projection.last_seen_at
        == expected.last_seen_at
    )

    assert projection.evidence_record_ids == [
        "decision-001",
        "decision-002",
    ]


def test_list_preserves_empty_pattern_result(
    monkeypatch,
):
    service = Mock()
    service.analyze_recommendation.return_value = []

    install_service(
        monkeypatch,
        service,
    )

    result = api.list_decision_patterns(
        organization_id="organization-001",
        identity_id="identity-001",
        recommendation_id=(
            "recommendation-001"
        ),
        db=object(),
    )

    assert result == []


def test_list_translates_validation_error(
    monkeypatch,
):
    error = (
        DecisionPatternIntelligenceValidationError(
            "Recommendation identifier is required."
        )
    )

    service = Mock()
    service.analyze_recommendation.side_effect = error

    install_service(
        monkeypatch,
        service,
    )

    with pytest.raises(
        HTTPException
    ) as caught:
        api.list_decision_patterns(
            organization_id="organization-001",
            identity_id="identity-001",
            recommendation_id="",
            db=object(),
        )

    assert (
        caught.value.status_code
        == status.HTTP_400_BAD_REQUEST
    )

    assert caught.value.detail == str(error)


def test_router_exposes_no_mutation_methods():
    methods = app.openapi()["paths"][
        COLLECTION_PATH
    ]

    assert "post" not in methods
    assert "put" not in methods
    assert "patch" not in methods
    assert "delete" not in methods
