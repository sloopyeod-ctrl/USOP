from types import SimpleNamespace
from unittest.mock import MagicMock

from app.models.account import Account
from app.reconciliation.reconciliation_engine import ReconciliationEngine
from app.schemas.account import AccountCreate


def test_account_model_exposes_organizational_identity_id():
    assert "organizational_identity_id" in Account.__table__.columns
    column = Account.__table__.columns["organizational_identity_id"]
    assert column.nullable is True
    assert list(column.foreign_keys)[0].target_fullname == (
        "organizational_identities.id"
    )


def test_account_schema_accepts_transitional_ownership():
    schema = AccountCreate(
        identity_id="identity-001",
        organizational_identity_id="organizational-identity-001",
        username="john.smith",
        system_name="Microsoft Entra ID",
    )
    assert schema.organizational_identity_id == (
        "organizational-identity-001"
    )


def test_reconciliation_preserves_legacy_mode_without_context():
    engine = ReconciliationEngine(MagicMock())
    assert engine.organization_id is None


def test_reconciliation_normalizes_explicit_context():
    engine = ReconciliationEngine(
        MagicMock(),
        organization_id="  organization-027  ",
    )
    assert engine.organization_id == "organization-027"


def test_reconciliation_resolves_exact_organization_identity_pair():
    db = MagicMock()
    filtered = db.query.return_value.filter.return_value
    filtered.one_or_none.return_value = SimpleNamespace(
        id="organizational-identity-001",
        organization_id="organization-027",
        identity_id="identity-001",
    )
    engine = ReconciliationEngine(
        db,
        organization_id="organization-027",
    )
    result = engine._resolve_organizational_identity(
        identity_id="identity-001"
    )
    assert result.id == "organizational-identity-001"
    filtered.one_or_none.assert_called_once_with()


def test_reconciliation_returns_none_without_context():
    db = MagicMock()
    engine = ReconciliationEngine(db)
    result = engine._resolve_organizational_identity(
        identity_id="identity-001"
    )
    assert result is None
    db.query.assert_not_called()


def test_organization_scoped_reconciliation_creates_identity_placement():
    db = MagicMock()

    engine = ReconciliationEngine(
        db,
        organization_id="organization-027",
    )

    identity = SimpleNamespace(
        id="identity-001",
        display_name="Johnny Example",
    )

    engine._resolve_account_identity = MagicMock(
        return_value=identity
    )
    engine._resolve_organizational_identity = MagicMock(
        side_effect=[
            None,
            SimpleNamespace(
                id="organizational-identity-001",
                organization_id="organization-027",
                identity_id="identity-001",
            ),
        ]
    )

    summary = {
        "organizational_identities_created": 0,
        "accounts_created": 0,
        "accounts_updated": 0,
        "accounts_skipped": 0,
    }

    engine._ensure_organizational_identity_placement(
        identity=identity,
        summary=summary,
    )

    assert summary["organizational_identities_created"] == 1

    added = [
        call.args[0]
        for call in db.add.call_args_list
    ]

    assert len(added) == 1

    organizational_identity = added[0]

    assert organizational_identity.organization_id == "organization-027"
    assert organizational_identity.identity_id == "identity-001"
    assert organizational_identity.display_name == "Johnny Example"
    assert organizational_identity.status == "Active"

    db.flush.assert_called_once()


def test_automatic_identity_placement_is_idempotent():
    db = MagicMock()

    existing = SimpleNamespace(
        id="organizational-identity-001",
        organization_id="organization-027",
        identity_id="identity-001",
    )

    engine = ReconciliationEngine(
        db,
        organization_id="organization-027",
    )

    engine._resolve_organizational_identity = MagicMock(
        return_value=existing
    )

    summary = {
        "organizational_identities_created": 0,
    }

    result = engine._ensure_organizational_identity_placement(
        identity=SimpleNamespace(
            id="identity-001",
            display_name="Johnny Example",
        ),
        summary=summary,
    )

    assert result is existing
    assert summary["organizational_identities_created"] == 0
    db.add.assert_not_called()
    db.flush.assert_not_called()


def test_automatic_identity_placement_does_nothing_without_context():
    db = MagicMock()

    engine = ReconciliationEngine(db)

    summary = {
        "organizational_identities_created": 0,
    }

    result = engine._ensure_organizational_identity_placement(
        identity=SimpleNamespace(
            id="identity-001",
            display_name="Johnny Example",
        ),
        summary=summary,
    )

    assert result is None
    assert summary["organizational_identities_created"] == 0
    db.add.assert_not_called()
    db.flush.assert_not_called()