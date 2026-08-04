from app.models.pending_decision_work_item import (
    PendingDecisionWorkItem,
)


def test_pending_decision_work_item_contract():
    table = PendingDecisionWorkItem.__table__

    assert table.name == "pending_decision_work_items"
    assert table.columns["organization_id"].nullable is False
    assert table.columns["source_type"].nullable is False
    assert table.columns["source_id"].nullable is False
    assert table.columns["decision_category"].nullable is False
    assert table.columns["evidence_snapshot_json"].nullable is False
    assert table.columns["identity_id"].nullable is True
    assert table.columns["decision_record_id"].nullable is True


def test_pending_decision_work_item_unique_source():
    constraints = {
        constraint.name
        for constraint in (
            PendingDecisionWorkItem.__table__.constraints
        )
    }

    assert (
        "uq_pending_decision_work_items_organization_source"
        in constraints
    )
