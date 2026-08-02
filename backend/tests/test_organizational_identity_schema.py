from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.schemas.organizational_identity import (
    OrganizationalIdentityCreate,
    OrganizationalIdentityRead,
)


EXPECTED_CREATE_FIELDS = {
    "identity_id",
    "display_name",
    "status",
}

EXPECTED_READ_FIELDS = {
    "id",
    "organization_id",
    "identity_id",
    "display_name",
    "status",
    "created_at",
    "updated_at",
    "created_by",
    "updated_by",
    "is_active",
}


def test_create_contract_is_exact():
    assert (
        set(OrganizationalIdentityCreate.model_fields)
        == EXPECTED_CREATE_FIELDS
    )


def test_read_contract_is_exact():
    assert (
        set(OrganizationalIdentityRead.model_fields)
        == EXPECTED_READ_FIELDS
    )


@pytest.mark.parametrize(
    "field_name",
    [
        "organization_id",
        "id",
        "created_at",
        "created_by",
        "is_active",
    ],
)
def test_create_rejects_server_controlled_fields(
    field_name: str,
):
    payload = {
        "identity_id": "identity-001",
        field_name: "caller-controlled",
    }

    with pytest.raises(ValidationError):
        OrganizationalIdentityCreate.model_validate(
            payload
        )


def test_create_normalizes_fields():
    schema = (
        OrganizationalIdentityCreate.model_validate(
            {
                "identity_id": "  identity-001  ",
                "display_name": "  John Smith  ",
                "status": "  Active  ",
            }
        )
    )

    assert schema.identity_id == "identity-001"
    assert schema.display_name == "John Smith"
    assert schema.status == "Active"


def test_create_rejects_blank_identity_id():
    with pytest.raises(ValidationError):
        OrganizationalIdentityCreate.model_validate(
            {
                "identity_id": "   ",
            }
        )


def test_read_serializes_from_orm_attributes():
    timestamp = datetime.now(UTC)

    record = SimpleNamespace(
        id="organizational-identity-001",
        organization_id="organization-027",
        identity_id="identity-001",
        display_name="John Smith",
        status="Active",
        created_at=timestamp,
        updated_at=timestamp,
        created_by="system",
        updated_by="system",
        is_active=True,
    )

    schema = OrganizationalIdentityRead.model_validate(
        record
    )

    assert schema.organization_id == "organization-027"
    assert schema.identity_id == "identity-001"
    assert schema.display_name == "John Smith"
