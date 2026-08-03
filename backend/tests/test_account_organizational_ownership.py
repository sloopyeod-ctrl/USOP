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
