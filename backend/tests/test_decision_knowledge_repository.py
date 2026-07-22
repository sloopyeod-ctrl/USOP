from unittest.mock import MagicMock

from app.models.decision_knowledge import DecisionKnowledge
from app.repositories.decision_knowledge_repository import (
    DecisionKnowledgeRepository,
)


def test_create_stages_relationship_without_owning_transaction():
    db = MagicMock()
    repository = DecisionKnowledgeRepository(db)

    relationship = DecisionKnowledge(
        decision_record_id="decision-1",
        knowledge_asset_id="knowledge-1",
        relationship_type="Reference",
    )

    result = repository.create(relationship)

    db.add.assert_called_once_with(relationship)
    db.flush.assert_called_once_with()
    db.refresh.assert_called_once_with(relationship)
    db.commit.assert_not_called()
    db.rollback.assert_not_called()

    assert result is relationship


def test_list_for_decision_uses_active_deterministic_query():
    db = MagicMock()
    query = db.query.return_value
    filtered_query = query.filter.return_value
    ordered_query = filtered_query.order_by.return_value
    expected = [MagicMock(spec=DecisionKnowledge)]

    ordered_query.all.return_value = expected

    repository = DecisionKnowledgeRepository(db)

    result = repository.list_for_decision("decision-1")

    db.query.assert_called_once_with(DecisionKnowledge)
    query.filter.assert_called_once()
    filtered_query.order_by.assert_called_once()
    ordered_query.all.assert_called_once_with()

    db.commit.assert_not_called()
    db.rollback.assert_not_called()

    assert result == expected


def test_list_for_knowledge_asset_uses_active_deterministic_query():
    db = MagicMock()
    query = db.query.return_value
    filtered_query = query.filter.return_value
    ordered_query = filtered_query.order_by.return_value
    expected = [MagicMock(spec=DecisionKnowledge)]

    ordered_query.all.return_value = expected

    repository = DecisionKnowledgeRepository(db)

    result = repository.list_for_knowledge_asset(
        "knowledge-1"
    )

    db.query.assert_called_once_with(DecisionKnowledge)
    query.filter.assert_called_once()
    filtered_query.order_by.assert_called_once()
    ordered_query.all.assert_called_once_with()

    db.commit.assert_not_called()
    db.rollback.assert_not_called()

    assert result == expected

def test_get_relationship_returns_exact_match_without_side_effects():
    db = MagicMock()
    query = db.query.return_value
    filtered_query = query.filter.return_value
    expected = MagicMock(spec=DecisionKnowledge)

    filtered_query.one_or_none.return_value = expected

    repository = DecisionKnowledgeRepository(db)

    result = repository.get_relationship(
        decision_record_id="decision-1",
        knowledge_asset_id="knowledge-1",
        relationship_type="Reference",
    )

    db.query.assert_called_once_with(DecisionKnowledge)
    query.filter.assert_called_once()
    filtered_query.one_or_none.assert_called_once_with()

    db.commit.assert_not_called()
    db.rollback.assert_not_called()

    assert result is expected

def test_repository_exposes_only_expected_public_operations():
    public_operations = {
        name
        for name in dir(DecisionKnowledgeRepository)
        if not name.startswith("_")
    }

    assert public_operations == {
        "create",
        "get_relationship",
        "list_for_decision",
        "list_for_knowledge_asset",
    }