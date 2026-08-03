from app.models.authorization_event import AuthorizationEvent


def test_authorization_event_table_contract():
    table = AuthorizationEvent.__table__

    assert table.name == "authorization_events"
    assert table.columns["organization_id"].nullable is False
    assert table.columns["subject_type"].nullable is False
    assert table.columns["subject_id"].nullable is False
    assert table.columns["event_type"].nullable is False
    assert table.columns["detected_at"].nullable is False
    assert table.columns["organizational_identity_id"].nullable is True
    assert table.columns["identity_id"].nullable is True
    assert table.columns["account_id"].nullable is True
    assert table.columns["role_assignment_id"].nullable is True


def test_authorization_event_foreign_keys():
    table = AuthorizationEvent.__table__

    targets = {
        foreign_key.target_fullname
        for column in table.columns
        for foreign_key in column.foreign_keys
    }

    assert "organizations.id" in targets
    assert "organizational_identities.id" in targets
    assert "identities.id" in targets
    assert "accounts.id" in targets
    assert "role_assignments.id" in targets
