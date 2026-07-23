from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.intelligence.decision_knowledge_intelligence_service import (
    DecisionKnowledgeIntelligenceIntegrityError,
    DecisionKnowledgeIntelligenceService,
)


ORGANIZATION_ID = "organization-001"
DECISION_ID = "decision-001"
KNOWLEDGE_ASSET_ID = "knowledge-001"


def relationship_record():
    timestamp = datetime.now(UTC)

    return SimpleNamespace(
        id="relationship-001",
        decision_record_id=DECISION_ID,
        knowledge_asset_id=KNOWLEDGE_ASSET_ID,
        relationship_type="PrimaryGuidance",
        created_at=timestamp,
        updated_at=timestamp,
        created_by="analyst@example.com",
        updated_by="analyst@example.com",
        is_active=True,
    )


def knowledge_asset_record():
    timestamp = datetime.now(UTC)

    return SimpleNamespace(
        id=KNOWLEDGE_ASSET_ID,
        organization_id=ORGANIZATION_ID,
        title="Global Administrator elevation review",
        summary="Review privileged authorization changes.",
        guidance=(
            "Require explicit analyst review for material "
            "privilege elevation."
        ),
        category="Authorization",
        status="Active",
        version=3,
        source_system="MicrosoftEntraID",
        source_identifier="role-assignment-001",
        confidence_score=95,
        created_at=timestamp,
        updated_at=timestamp,
        created_by="architect@example.com",
        updated_by="architect@example.com",
        is_active=True,
    )


@pytest.fixture
def service():
    service = DecisionKnowledgeIntelligenceService(
        MagicMock()
    )

    service.relationship_service = MagicMock()
    service.knowledge_asset_repository = MagicMock()

    return service


def test_list_for_decision_builds_rich_projection(
    service,
):
    relationship = relationship_record()
    knowledge_asset = knowledge_asset_record()

    service.relationship_service.list_for_decision.return_value = [
        relationship
    ]

    service.knowledge_asset_repository.list_by_ids.return_value = [
        knowledge_asset
    ]

    result = service.list_for_decision(
        organization_id=ORGANIZATION_ID,
        decision_record_id=DECISION_ID,
    )

    assert len(result) == 1

    projection = result[0]

    assert (
        projection["relationship"]["id"]
        == relationship.id
    )
    assert (
        projection["relationship"]["relationship_type"]
        == "PrimaryGuidance"
    )
    assert (
        projection["knowledge"]["id"]
        == knowledge_asset.id
    )
    assert (
        projection["knowledge"]["title"]
        == knowledge_asset.title
    )
    assert projection["knowledge"]["version"] == 3
    assert projection["knowledge"]["status"] == "Active"
    assert (
        projection["knowledge"]["confidence_score"]
        == 95
    )


def test_list_for_decision_uses_one_bulk_asset_lookup(
    service,
):
    relationship_one = relationship_record()
    relationship_two = relationship_record()

    relationship_two.id = "relationship-002"
    relationship_two.knowledge_asset_id = "knowledge-002"

    knowledge_one = knowledge_asset_record()
    knowledge_two = knowledge_asset_record()

    knowledge_two.id = "knowledge-002"
    knowledge_two.title = "Secondary guidance"

    service.relationship_service.list_for_decision.return_value = [
        relationship_one,
        relationship_two,
    ]

    service.knowledge_asset_repository.list_by_ids.return_value = [
        knowledge_one,
        knowledge_two,
    ]

    service.list_for_decision(
        organization_id=ORGANIZATION_ID,
        decision_record_id=DECISION_ID,
    )

    (
        service.knowledge_asset_repository
        .list_by_ids
        .assert_called_once_with(
            organization_id=ORGANIZATION_ID,
            knowledge_asset_ids=[
                KNOWLEDGE_ASSET_ID,
                "knowledge-002",
            ],
        )
    )


def test_list_for_decision_preserves_relationship_order(
    service,
):
    relationship_one = relationship_record()
    relationship_two = relationship_record()

    relationship_one.id = "relationship-older"
    relationship_one.knowledge_asset_id = "knowledge-002"

    relationship_two.id = "relationship-newer"
    relationship_two.knowledge_asset_id = KNOWLEDGE_ASSET_ID

    knowledge_one = knowledge_asset_record()
    knowledge_two = knowledge_asset_record()

    knowledge_two.id = "knowledge-002"

    service.relationship_service.list_for_decision.return_value = [
        relationship_one,
        relationship_two,
    ]

    service.knowledge_asset_repository.list_by_ids.return_value = [
        knowledge_one,
        knowledge_two,
    ]

    result = service.list_for_decision(
        organization_id=ORGANIZATION_ID,
        decision_record_id=DECISION_ID,
    )

    assert [
        item["relationship"]["id"]
        for item in result
    ] == [
        "relationship-older",
        "relationship-newer",
    ]


def test_list_for_decision_returns_empty_without_asset_query(
    service,
):
    service.relationship_service.list_for_decision.return_value = []

    result = service.list_for_decision(
        organization_id=ORGANIZATION_ID,
        decision_record_id=DECISION_ID,
    )

    assert result == []

    (
        service.knowledge_asset_repository
        .list_by_ids
        .assert_not_called()
    )


def test_list_for_decision_rejects_unresolved_relationship(
    service,
):
    service.relationship_service.list_for_decision.return_value = [
        relationship_record()
    ]

    service.knowledge_asset_repository.list_by_ids.return_value = []

    with pytest.raises(
        DecisionKnowledgeIntelligenceIntegrityError,
        match="could not be resolved",
    ):
        service.list_for_decision(
            organization_id=ORGANIZATION_ID,
            decision_record_id=DECISION_ID,
        )
