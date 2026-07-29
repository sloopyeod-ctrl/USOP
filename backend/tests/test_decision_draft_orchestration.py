from enum import Enum

import pytest

from app.intelligence.drafting import (
    DecisionDraftIntelligenceService,
)
from app.intelligence.drafting.decision_draft_intelligence_service import (
    DecisionDraftIdentityNotFoundError,
    DecisionDraftIntelligenceError,
    DecisionDraftIntelligenceValidationError,
    DecisionDraftRecommendationNotFoundError,
)


class FakeIdentityIntelligenceService:

    def __init__(
        self,
        intelligence,
    ):
        self.intelligence = intelligence
        self.calls = []

    def get_identity_intelligence(
        self,
        identity_id,
        organization_id=None,
    ):
        self.calls.append(
            {
                "identity_id": identity_id,
                "organization_id": (
                    organization_id
                ),
            }
        )

        return self.intelligence


class FakeDecisionKnowledgeService:

    def __init__(
        self,
        guidance=None,
    ):
        self.guidance = list(
            guidance or []
        )
        self.calls = []

    def list_for_decision(
        self,
        *,
        organization_id,
        decision_record_id,
    ):
        self.calls.append(
            {
                "organization_id": (
                    organization_id
                ),
                "decision_record_id": (
                    decision_record_id
                ),
            }
        )

        return self.guidance


class FakeDecisionPatternService:

    def __init__(
        self,
        patterns=None,
    ):
        self.patterns = list(
            patterns or []
        )
        self.calls = []

    def analyze_recommendation(
        self,
        *,
        organization_id,
        identity_id,
        recommendation_id,
    ):
        self.calls.append(
            {
                "organization_id": (
                    organization_id
                ),
                "identity_id": (
                    identity_id
                ),
                "recommendation_id": (
                    recommendation_id
                ),
            }
        )

        return self.patterns


def recommendation(
    *,
    disposition=None,
):
    result = {
        "recommendation_id": "rec-001",
        "title": (
            "Remove unnecessary "
            "privileged access"
        ),
        "description": (
            "Remove the observed "
            "privileged authorization."
        ),
        "recommendation_type": (
            "Authorization"
        ),
    }

    if disposition is not None:
        result[
            "organizational_disposition"
        ] = disposition

    return result


def intelligence(
    *,
    recommendations=None,
):
    return {
        "recommendations": list(
            recommendations or []
        ),
    }


def build_service(
    *,
    identity_result,
    guidance=None,
    patterns=None,
):
    identity_service = (
        FakeIdentityIntelligenceService(
            identity_result
        )
    )

    knowledge_service = (
        FakeDecisionKnowledgeService(
            guidance
        )
    )

    pattern_service = (
        FakeDecisionPatternService(
            patterns
        )
    )

    service = (
        DecisionDraftIntelligenceService(
            identity_intelligence_service=(
                identity_service
            ),
            decision_knowledge_service=(
                knowledge_service
            ),
            decision_pattern_service=(
                pattern_service
            ),
        )
    )

    return (
        service,
        identity_service,
        knowledge_service,
        pattern_service,
    )


def test_orchestration_builds_draft_from_authoritative_facts():
    disposition = {
        "decision_id": "decision-001",
        "display_status": (
            "Accepted Temporarily"
        ),
        "history": [
            {
                "decision_id": (
                    "decision-001"
                ),
                "decision_type": (
                    "AcceptRisk"
                ),
                "display_status": (
                    "Accepted Temporarily"
                ),
                "created_at": (
                    "2026-07-01T00:00:00"
                    "+00:00"
                ),
            }
        ],
    }

    guidance = [
        {
            "knowledge": {
                "id": "knowledge-001",
                "title": (
                    "Privileged access "
                    "standard"
                ),
                "summary": (
                    "Privileged assignments "
                    "require review."
                ),
            },
        }
    ]

    patterns = [
        {
            "pattern_type": (
                "RepeatedTemporaryAcceptance"
            ),
            "title": (
                "Repeated Temporary "
                "Acceptance"
            ),
            "summary": (
                "Temporary acceptance "
                "occurred repeatedly."
            ),
        }
    ]

    (
        service,
        identity_service,
        knowledge_service,
        pattern_service,
    ) = build_service(
        identity_result=intelligence(
            recommendations=[
                recommendation(
                    disposition=disposition
                )
            ]
        ),
        guidance=guidance,
        patterns=patterns,
    )

    draft = (
        service.build_for_recommendation(
            organization_id="org-001",
            identity_id="identity-001",
            recommendation_id="rec-001",
            decision_type="CorrectRisk",
        )
    )

    assert draft.decision_type == (
        "CorrectRisk"
    )

    assert draft.confidence_score == 100

    assert [
        item.source_type
        for item in draft.evidence_used
    ] == [
        "Recommendation",
        "DecisionHistory",
        "OrganizationGuidance",
        "OrganizationPattern",
    ]

    assert identity_service.calls == [
        {
            "identity_id": "identity-001",
            "organization_id": "org-001",
        }
    ]

    assert knowledge_service.calls == [
        {
            "organization_id": "org-001",
            "decision_record_id": (
                "decision-001"
            ),
        }
    ]

    assert pattern_service.calls == [
        {
            "organization_id": "org-001",
            "identity_id": "identity-001",
            "recommendation_id": "rec-001",
        }
    ]


def test_new_recommendation_omits_guidance_lookup():
    (
        service,
        _,
        knowledge_service,
        _,
    ) = build_service(
        identity_result=intelligence(
            recommendations=[
                recommendation()
            ]
        ),
    )

    draft = (
        service.build_for_recommendation(
            organization_id="org-001",
            identity_id="identity-001",
            recommendation_id="rec-001",
            decision_type="CorrectRisk",
        )
    )

    assert knowledge_service.calls == []

    assert draft.confidence_score == 40

    assert [
        item.source_type
        for item in draft.evidence_used
    ] == [
        "Recommendation",
    ]


def test_orchestration_accepts_decision_type_enum():
    class DecisionTypeValue(
        str,
        Enum,
    ):
        CORRECT_RISK = "CorrectRisk"

    (
        service,
        _,
        _,
        _,
    ) = build_service(
        identity_result=intelligence(
            recommendations=[
                recommendation()
            ]
        ),
    )

    draft = (
        service.build_for_recommendation(
            organization_id="org-001",
            identity_id="identity-001",
            recommendation_id="rec-001",
            decision_type=(
                DecisionTypeValue
                .CORRECT_RISK
            ),
        )
    )

    assert draft.decision_type == (
        "CorrectRisk"
    )


def test_orchestration_rejects_missing_identity():
    (
        service,
        _,
        _,
        _,
    ) = build_service(
        identity_result=None,
    )

    with pytest.raises(
        DecisionDraftIdentityNotFoundError,
        match=(
            "Identity intelligence "
            "was not found"
        ),
    ):
        service.build_for_recommendation(
            organization_id="org-001",
            identity_id="identity-001",
            recommendation_id="rec-001",
            decision_type="CorrectRisk",
        )


def test_orchestration_rejects_missing_recommendation():
    (
        service,
        _,
        _,
        _,
    ) = build_service(
        identity_result=intelligence(),
    )

    with pytest.raises(
        DecisionDraftRecommendationNotFoundError,
        match="Recommendation was not found",
    ):
        service.build_for_recommendation(
            organization_id="org-001",
            identity_id="identity-001",
            recommendation_id="rec-001",
            decision_type="CorrectRisk",
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "arguments",
    ),
    [
        (
            "Organization",
            {
                "organization_id": " ",
                "identity_id": "identity-001",
                "recommendation_id": "rec-001",
                "decision_type": "CorrectRisk",
            },
        ),
        (
            "Identity",
            {
                "organization_id": "org-001",
                "identity_id": " ",
                "recommendation_id": "rec-001",
                "decision_type": "CorrectRisk",
            },
        ),
        (
            "Recommendation",
            {
                "organization_id": "org-001",
                "identity_id": "identity-001",
                "recommendation_id": " ",
                "decision_type": "CorrectRisk",
            },
        ),
    ],
)
def test_orchestration_validates_scope(
    field_name,
    arguments,
):
    (
        service,
        _,
        _,
        _,
    ) = build_service(
        identity_result=intelligence(),
    )

    with pytest.raises(
        DecisionDraftIntelligenceValidationError,
        match=(
            f"{field_name} identifier "
            "is required"
        ),
    ):
        service.build_for_recommendation(
            **arguments
        )


def test_orchestration_requires_dependencies():
    service = (
        DecisionDraftIntelligenceService()
    )

    with pytest.raises(
        DecisionDraftIntelligenceError,
        match=(
            "orchestration dependencies "
            "are unavailable"
        ),
    ):
        service.build_for_recommendation(
            organization_id="org-001",
            identity_id="identity-001",
            recommendation_id="rec-001",
            decision_type="CorrectRisk",
        )
