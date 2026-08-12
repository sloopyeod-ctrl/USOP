from app.models.platform_user import PlatformUser
from app.schemas.platform_user import PlatformUserRead


def test_platform_user_exposes_optional_organizational_identity_binding():
    table = PlatformUser.__table__

    assert "organizational_identity_id" in table.columns
    column = table.columns["organizational_identity_id"]

    assert column.nullable is True
    assert column.index is True

    foreign_keys = {
        foreign_key.target_fullname
        for foreign_key in column.foreign_keys
    }
    assert foreign_keys == {"organizational_identities.id"}


def test_platform_user_read_exposes_binding_without_authority_fields():
    fields = set(PlatformUserRead.model_fields)

    assert "organizational_identity_id" in fields
    assert "password" not in fields
    assert "access_token" not in fields
    assert "roles" not in fields
    assert "permissions" not in fields
