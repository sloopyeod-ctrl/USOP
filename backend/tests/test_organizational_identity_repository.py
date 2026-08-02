from unittest.mock import MagicMock

from app.repositories.organizational_identity_repository import (
    OrganizationalIdentityRepository,
)


def test_list_for_organization_executes_scoped_query():
    db = MagicMock()
    query = db.query.return_value
    filtered = query.filter.return_value
    ordered = filtered.order_by.return_value
    ordered.all.return_value = []

    repository = OrganizationalIdentityRepository(db)

    result = repository.list_for_organization(
        "organization-027"
    )

    assert result == []
    db.query.assert_called_once()
    query.filter.assert_called_once()
    filtered.order_by.assert_called_once()
    ordered.all.assert_called_once()


def test_get_by_id_for_organization_uses_one_or_none():
    db = MagicMock()
    query = db.query.return_value
    filtered = query.filter.return_value
    filtered.one_or_none.return_value = None

    repository = OrganizationalIdentityRepository(db)

    result = repository.get_by_id_for_organization(
        organization_id="organization-027",
        organizational_identity_id=(
            "organizational-identity-001"
        ),
    )

    assert result is None
    filtered.one_or_none.assert_called_once()


def test_create_adds_and_flushes_record():
    db = MagicMock()
    repository = OrganizationalIdentityRepository(db)
    record = MagicMock()

    result = repository.create(record)

    assert result is record
    db.add.assert_called_once_with(record)
    db.flush.assert_called_once_with()
