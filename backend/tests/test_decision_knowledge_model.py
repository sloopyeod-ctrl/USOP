from sqlalchemy import UniqueConstraint

from app.domain import KnowledgeRelationshipType
from app.models import DecisionKnowledge


def test_decision_knowledge_uses_canonical_table_name():
    assert DecisionKnowledge.__tablename__ == "decision_knowledge"


def test_decision_knowledge_contract_is_exact():
    assert set(DecisionKnowledge.__table__.columns.keys()) == {
        "id",
        "decision_record_id",
        "knowledge_asset_id",
        "relationship_type",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "is_active",
        "source_system",
        "source_identifier",
        "confidence_score",
    }


def test_decision_knowledge_foreign_keys_are_explicit():
    decision_foreign_keys = {
        foreign_key.target_fullname
        for foreign_key
        in DecisionKnowledge.__table__
        .c.decision_record_id.foreign_keys
    }
    knowledge_foreign_keys = {
        foreign_key.target_fullname
        for foreign_key
        in DecisionKnowledge.__table__
        .c.knowledge_asset_id.foreign_keys
    }

    assert decision_foreign_keys == {
        "decision_records.id",
    }
    assert knowledge_foreign_keys == {
        "knowledge_assets.id",
    }


def test_decision_knowledge_relationship_type_default_is_canonical():
    default = (
        DecisionKnowledge.__table__
        .c.relationship_type.default
    )

    assert default is not None
    assert (
        default.arg
        == KnowledgeRelationshipType.REFERENCE.value
    )


def test_decision_knowledge_has_canonical_unique_constraint():
    unique_constraints = {
        (
            constraint.name,
            tuple(column.name for column in constraint.columns),
        )
        for constraint in DecisionKnowledge.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert (
        "uq_decision_knowledge_decision_asset_relationship",
        (
            "decision_record_id",
            "knowledge_asset_id",
            "relationship_type",
        ),
    ) in unique_constraints


def test_decision_knowledge_does_not_duplicate_entity_ownership():
    prohibited_columns = {
        "organization_id",
        "knowledge_title",
        "knowledge_summary",
        "knowledge_guidance",
        "knowledge_version",
        "evidence_snapshot_json",
        "first_seen_at",
        "last_seen_at",
        "status",
    }

    assert prohibited_columns.isdisjoint(
        DecisionKnowledge.__table__.columns.keys()
    )