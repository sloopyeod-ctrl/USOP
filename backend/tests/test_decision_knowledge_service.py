from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.domain import KnowledgeRelationshipType
from app.models.decision_knowledge import DecisionKnowledge
from app.services.decision_knowledge_service import (
    DecisionKnowledgeAssetNotFoundError,
    DecisionKnowledgeDecisionNotFoundError,
    DecisionKnowledgeDuplicateError,
    DecisionKnowledgeService,
    DecisionKnowledgeValidationError,
)


ORGANIZATION_ID = "organization-1"
DECISION_ID = "decision-1"
KNOWLEDGE_ASSET_ID = "knowledge-1"
RELATIONSHIP_ID = "relationship-1"


@pytest.fixture
def service() -> DecisionKnowledgeService:
    service = DecisionKnowledgeService(MagicMock())

    service.decision_repository = MagicMock()
    service.knowledge_asset_repository = MagicMock()
    service.relationship_repository = MagicMock()
    service.audit_service = MagicMock()

    service.decision_repository.get_by_id_for_organization.return_value = (
        SimpleNamespace(id=DECISION_ID)
    )

    service.knowledge_asset_repository.get_by_id.return_value = (
        SimpleNamespace(id=KNOWLEDGE_ASSET_ID)
    )

    service.relationship_repository.get_relationship.return_value = None

    def create_relationship(
        relationship: DecisionKnowledge,
    ) -> DecisionKnowledge:
        relationship.id = RELATIONSHIP_ID
        return relationship

    service.relationship_repository.create.side_effect = (
        create_relationship
    )

    return service


def test_create_pending_stages_canonical_relationship(
    service: DecisionKnowledgeService,
):
    relationship = service.create_pending(
        organization_id=ORGANIZATION_ID,
        decision_record_id=DECISION_ID,
        knowledge_asset_id=KNOWLEDGE_ASSET_ID,
        relationship_type=(
            KnowledgeRelationshipType.PRIMARY_GUIDANCE
        ),
        actor="analyst@example.com",
    )

    assert relationship.id == RELATIONSHIP_ID
    assert relationship.decision_record_id == DECISION_ID
    assert (
        relationship.knowledge_asset_id
        == KNOWLEDGE_ASSET_ID
    )
    assert relationship.relationship_type == "PrimaryGuidance"
    assert relationship.created_by == "analyst@example.com"
    assert relationship.updated_by == "analyst@example.com"

    service.relationship_repository.create.assert_called_once()
    service.audit_service.record_pending.assert_called_once()

    audit_arguments = (
        service.audit_service
        .record_pending
        .call_args
        .kwargs
    )

    assert (
        audit_arguments["event_type"]
        == "DecisionKnowledgeLinked"
    )
    assert (
        audit_arguments["metadata"]["organization_id"]
        == ORGANIZATION_ID
    )
    assert (
        audit_arguments["metadata"]["relationship_type"]
        == "PrimaryGuidance"
    )


def test_create_pending_accepts_canonical_string(
    service: DecisionKnowledgeService,
):
    relationship = service.create_pending(
        organization_id=ORGANIZATION_ID,
        decision_record_id=DECISION_ID,
        knowledge_asset_id=KNOWLEDGE_ASSET_ID,
        relationship_type="Reference",
    )

    assert relationship.relationship_type == "Reference"


def test_create_pending_rejects_unknown_relationship_type(
    service: DecisionKnowledgeService,
):
    with pytest.raises(
        DecisionKnowledgeValidationError,
        match="Unknown DecisionKnowledge relationship type",
    ):
        service.create_pending(
            organization_id=ORGANIZATION_ID,
            decision_record_id=DECISION_ID,
            knowledge_asset_id=KNOWLEDGE_ASSET_ID,
            relationship_type="UnsupportedRelationship",
        )

    service.relationship_repository.create.assert_not_called()
    service.audit_service.record_pending.assert_not_called()


def test_create_pending_rejects_decision_outside_organization(
    service: DecisionKnowledgeService,
):
    service.decision_repository.get_by_id_for_organization.return_value = (
        None
    )

    with pytest.raises(
        DecisionKnowledgeDecisionNotFoundError,
        match="DecisionRecord",
    ):
        service.create_pending(
            organization_id=ORGANIZATION_ID,
            decision_record_id=DECISION_ID,
            knowledge_asset_id=KNOWLEDGE_ASSET_ID,
            relationship_type="Reference",
        )

    service.knowledge_asset_repository.get_by_id.assert_not_called()
    service.relationship_repository.create.assert_not_called()


def test_create_pending_rejects_asset_outside_organization(
    service: DecisionKnowledgeService,
):
    service.knowledge_asset_repository.get_by_id.return_value = None

    with pytest.raises(
        DecisionKnowledgeAssetNotFoundError,
        match="KnowledgeAsset",
    ):
        service.create_pending(
            organization_id=ORGANIZATION_ID,
            decision_record_id=DECISION_ID,
            knowledge_asset_id=KNOWLEDGE_ASSET_ID,
            relationship_type="Reference",
        )

    service.relationship_repository.create.assert_not_called()
    service.audit_service.record_pending.assert_not_called()


def test_create_pending_rejects_existing_relationship(
    service: DecisionKnowledgeService,
):
    service.relationship_repository.get_relationship.return_value = (
        SimpleNamespace(id="existing-relationship")
    )

    with pytest.raises(
        DecisionKnowledgeDuplicateError,
        match="already has this relationship",
    ):
        service.create_pending(
            organization_id=ORGANIZATION_ID,
            decision_record_id=DECISION_ID,
            knowledge_asset_id=KNOWLEDGE_ASSET_ID,
            relationship_type="Reference",
        )

    service.relationship_repository.create.assert_not_called()
    service.audit_service.record_pending.assert_not_called()


def test_create_pending_translates_database_uniqueness_race(
    service: DecisionKnowledgeService,
):
    service.relationship_repository.create.side_effect = (
        IntegrityError(
            statement=None,
            params=None,
            orig=Exception("duplicate relationship"),
        )
    )

    with pytest.raises(
        DecisionKnowledgeDuplicateError,
        match="already has this relationship",
    ):
        service.create_pending(
            organization_id=ORGANIZATION_ID,
            decision_record_id=DECISION_ID,
            knowledge_asset_id=KNOWLEDGE_ASSET_ID,
            relationship_type="Reference",
        )

    service.audit_service.record_pending.assert_not_called()


def test_list_for_decision_enforces_organization_boundary(
    service: DecisionKnowledgeService,
):
    expected = [
        SimpleNamespace(id="relationship-1"),
        SimpleNamespace(id="relationship-2"),
    ]

    service.relationship_repository.list_for_decision.return_value = (
        expected
    )

    result = service.list_for_decision(
        organization_id=ORGANIZATION_ID,
        decision_record_id=DECISION_ID,
    )

    assert result == expected

    (
        service.decision_repository
        .get_by_id_for_organization
        .assert_called_once_with(
            organization_id=ORGANIZATION_ID,
            decision_id=DECISION_ID,
        )
    )

    (
        service.relationship_repository
        .list_for_decision
        .assert_called_once_with(
            DECISION_ID
        )
    )


def test_create_commits_and_refreshes_relationship(
    service: DecisionKnowledgeService,
):
    relationship = service.create(
        organization_id=ORGANIZATION_ID,
        decision_record_id=DECISION_ID,
        knowledge_asset_id=KNOWLEDGE_ASSET_ID,
        relationship_type="Reference",
    )

    assert relationship.id == RELATIONSHIP_ID

    service.db.commit.assert_called_once_with()
    service.db.refresh.assert_called_once_with(
        relationship
    )
    service.db.rollback.assert_not_called()


def test_create_rolls_back_when_pending_creation_fails(
    service: DecisionKnowledgeService,
):
    service.relationship_repository.create.side_effect = (
        RuntimeError("persistence failed")
    )

    with pytest.raises(
        RuntimeError,
        match="persistence failed",
    ):
        service.create(
            organization_id=ORGANIZATION_ID,
            decision_record_id=DECISION_ID,
            knowledge_asset_id=KNOWLEDGE_ASSET_ID,
            relationship_type="Reference",
        )

    service.db.commit.assert_not_called()
    service.db.refresh.assert_not_called()
    service.db.rollback.assert_called_once_with()
