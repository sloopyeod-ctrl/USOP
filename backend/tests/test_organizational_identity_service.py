from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.schemas.organizational_identity import (
    OrganizationalIdentityCreate,
)
from app.services.organizational_identity_service import (
    OrganizationalIdentityConflictError,
    OrganizationalIdentityIdentityNotFoundError,
    OrganizationalIdentityOrganizationNotFoundError,
    OrganizationalIdentityService,
)


def build_service():
    db = MagicMock()
    repository = MagicMock()
    organization_repository = MagicMock()
    identity_repository = MagicMock()

    service = OrganizationalIdentityService(
        db,
        repository=repository,
        organization_repository=(
            organization_repository
        ),
        identity_repository=identity_repository,
    )

    return (
        service,
        db,
        repository,
        organization_repository,
        identity_repository,
    )


def test_create_requires_known_organization():
    (
        service,
        _db,
        _repository,
        organization_repository,
        _identity_repository,
    ) = build_service()

    organization_repository.get_by_id.return_value = None

    with pytest.raises(
        OrganizationalIdentityOrganizationNotFoundError
    ):
        service.create(
            organization_id="organization-027",
            data=OrganizationalIdentityCreate(
                identity_id="identity-001",
            ),
        )


def test_create_requires_known_canonical_identity():
    (
        service,
        _db,
        _repository,
        organization_repository,
        identity_repository,
    ) = build_service()

    organization_repository.get_by_id.return_value = (
        SimpleNamespace(id="organization-027")
    )

    identity_repository.get_by_id.return_value = None

    with pytest.raises(
        OrganizationalIdentityIdentityNotFoundError
    ):
        service.create(
            organization_id="organization-027",
            data=OrganizationalIdentityCreate(
                identity_id="identity-001",
            ),
        )


def test_create_rejects_duplicate_placement():
    (
        service,
        _db,
        repository,
        organization_repository,
        identity_repository,
    ) = build_service()

    organization_repository.get_by_id.return_value = (
        SimpleNamespace(id="organization-027")
    )

    identity_repository.get_by_id.return_value = (
        SimpleNamespace(
            id="identity-001",
            display_name="John Smith",
        )
    )

    repository.get_for_identity.return_value = (
        SimpleNamespace(id="existing")
    )

    with pytest.raises(
        OrganizationalIdentityConflictError
    ):
        service.create(
            organization_id="organization-027",
            data=OrganizationalIdentityCreate(
                identity_id="identity-001",
            ),
        )


def test_create_commits_organization_owned_record():
    (
        service,
        db,
        repository,
        organization_repository,
        identity_repository,
    ) = build_service()

    organization_repository.get_by_id.return_value = (
        SimpleNamespace(id="organization-027")
    )

    identity_repository.get_by_id.return_value = (
        SimpleNamespace(
            id="identity-001",
            display_name="John Smith",
        )
    )

    repository.get_for_identity.return_value = None
    repository.create.side_effect = lambda record: record

    result = service.create(
        organization_id="organization-027",
        data=OrganizationalIdentityCreate(
            identity_id="identity-001",
        ),
        actor="system",
    )

    assert result.organization_id == "organization-027"
    assert result.identity_id == "identity-001"
    assert result.display_name == "John Smith"
    assert result.created_by == "system"

    db.commit.assert_called_once_with()
    db.refresh.assert_called_once_with(result)


def test_cross_organization_record_is_not_returned():
    (
        service,
        _db,
        repository,
        organization_repository,
        _identity_repository,
    ) = build_service()

    organization_repository.get_by_id.return_value = (
        SimpleNamespace(id="organization-027")
    )

    repository.get_by_id_for_organization.return_value = (
        None
    )

    result = service.get_by_id(
        organization_id="organization-027",
        organizational_identity_id=(
            "organizational-identity-company-75"
        ),
    )

    assert result is None

    repository.get_by_id_for_organization.assert_called_once_with(
        organization_id="organization-027",
        organizational_identity_id=(
            "organizational-identity-company-75"
        ),
    )
