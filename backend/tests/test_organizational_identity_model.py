from app.models.organizational_identity import (
    OrganizationalIdentity,
)


def test_organizational_identity_table_contract():
    table = OrganizationalIdentity.__table__

    assert table.name == "organizational_identities"

    assert set(table.columns.keys()) == {
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


def test_organizational_identity_owns_organization_and_identity():
    table = OrganizationalIdentity.__table__

    organization_foreign_keys = {
        foreign_key.target_fullname
        for foreign_key
        in table.c.organization_id.foreign_keys
    }

    identity_foreign_keys = {
        foreign_key.target_fullname
        for foreign_key
        in table.c.identity_id.foreign_keys
    }

    assert organization_foreign_keys == {
        "organizations.id",
    }

    assert identity_foreign_keys == {
        "identities.id",
    }

    assert table.c.organization_id.nullable is False
    assert table.c.identity_id.nullable is False


def test_organizational_identity_is_unique_per_organization():
    table = OrganizationalIdentity.__table__

    unique_constraints = {
        constraint.name: {
            column.name
            for column in constraint.columns
        }
        for constraint in table.constraints
        if constraint.name
    }

    assert unique_constraints[
        "uq_organizational_identities_"
        "organization_identity"
    ] == {
        "organization_id",
        "identity_id",
    }
