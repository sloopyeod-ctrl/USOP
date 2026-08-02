from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.schemas.organizational_identity_placement import (
    OrganizationalIdentityPlacementItem,
    OrganizationalIdentityPlacementRequest,
    PlacementDisposition,
)
from app.services.organizational_identity_placement_engine import (
    OrganizationalIdentityPlacementEngine,
    OrganizationalIdentityPlacementOrganizationNotFoundError,
    OrganizationalIdentityPlacementValidationError,
)


def build_engine():
    db = MagicMock()
    placement_repository = MagicMock()
    organization_repository = MagicMock()
    identity_repository = MagicMock()

    engine = OrganizationalIdentityPlacementEngine(
        db,
        organizational_identity_repository=placement_repository,
        organization_repository=organization_repository,
        identity_repository=identity_repository,
    )

    return (
        engine,
        db,
        placement_repository,
        organization_repository,
        identity_repository,
    )


def request_for(*identity_ids: str):
    return OrganizationalIdentityPlacementRequest(
        placements=[
            OrganizationalIdentityPlacementItem(
                identity_id=identity_id
            )
            for identity_id in identity_ids
        ]
    )


def test_preview_requires_known_organization():
    (
        engine,
        _db,
        _placement_repository,
        organization_repository,
        _identity_repository,
    ) = build_engine()

    organization_repository.get_by_id.return_value = None

    with pytest.raises(
        OrganizationalIdentityPlacementOrganizationNotFoundError
    ):
        engine.preview(
            organization_id="organization-027",
            request=request_for("identity-001"),
        )


def test_preview_never_writes_or_commits():
    (
        engine,
        db,
        placement_repository,
        organization_repository,
        identity_repository,
    ) = build_engine()

    organization_repository.get_by_id.return_value = (
        SimpleNamespace(id="organization-027")
    )
    identity_repository.get_by_id.return_value = (
        SimpleNamespace(
            id="identity-001",
            display_name="John Smith",
        )
    )
    placement_repository.get_for_identity.return_value = None

    report = engine.preview(
        organization_id="organization-027",
        request=request_for("identity-001"),
    )

    assert report.dry_run is True
    assert report.ready_count == 1
    assert report.can_apply is True
    assert (
        report.results[0].disposition
        == PlacementDisposition.READY
    )

    placement_repository.create.assert_not_called()
    db.commit.assert_not_called()


def test_preview_reports_unknown_identity_as_invalid():
    (
        engine,
        _db,
        _placement_repository,
        organization_repository,
        identity_repository,
    ) = build_engine()

    organization_repository.get_by_id.return_value = (
        SimpleNamespace(id="organization-027")
    )
    identity_repository.get_by_id.return_value = None

    report = engine.preview(
        organization_id="organization-027",
        request=request_for("identity-missing"),
    )

    assert report.invalid_count == 1
    assert report.can_apply is False


def test_preview_rejects_duplicate_identity_in_batch():
    (
        engine,
        _db,
        placement_repository,
        organization_repository,
        identity_repository,
    ) = build_engine()

    organization_repository.get_by_id.return_value = (
        SimpleNamespace(id="organization-027")
    )

    report = engine.preview(
        organization_id="organization-027",
        request=request_for(
            "identity-001",
            "identity-001",
        ),
    )

    assert report.invalid_count == 2
    assert report.can_apply is False
    identity_repository.get_by_id.assert_not_called()
    placement_repository.get_for_identity.assert_not_called()


def test_preview_is_idempotent_for_existing_placement():
    (
        engine,
        _db,
        placement_repository,
        organization_repository,
        identity_repository,
    ) = build_engine()

    organization_repository.get_by_id.return_value = (
        SimpleNamespace(id="organization-027")
    )
    identity_repository.get_by_id.return_value = (
        SimpleNamespace(
            id="identity-001",
            display_name="John Smith",
        )
    )
    placement_repository.get_for_identity.return_value = (
        SimpleNamespace(
            id="organizational-identity-001",
            display_name="John Smith",
        )
    )

    report = engine.preview(
        organization_id="organization-027",
        request=request_for("identity-001"),
    )

    assert report.already_placed_count == 1
    assert report.can_apply is True


def test_apply_requires_explicit_actor():
    (
        engine,
        _db,
        _placement_repository,
        _organization_repository,
        _identity_repository,
    ) = build_engine()

    with pytest.raises(
        OrganizationalIdentityPlacementValidationError
    ):
        engine.apply(
            organization_id="organization-027",
            request=request_for("identity-001"),
            actor="   ",
        )


def test_apply_refuses_invalid_batch_without_writing():
    (
        engine,
        db,
        placement_repository,
        organization_repository,
        identity_repository,
    ) = build_engine()

    organization_repository.get_by_id.return_value = (
        SimpleNamespace(id="organization-027")
    )
    identity_repository.get_by_id.return_value = None

    with pytest.raises(
        OrganizationalIdentityPlacementValidationError
    ):
        engine.apply(
            organization_id="organization-027",
            request=request_for("identity-missing"),
            actor="platform-admin",
        )

    placement_repository.create.assert_not_called()
    db.commit.assert_not_called()


def test_apply_commits_batch_once():
    (
        engine,
        db,
        placement_repository,
        organization_repository,
        identity_repository,
    ) = build_engine()

    organization_repository.get_by_id.return_value = (
        SimpleNamespace(id="organization-027")
    )

    identities = {
        "identity-001": SimpleNamespace(
            id="identity-001",
            display_name="John Smith",
        ),
        "identity-002": SimpleNamespace(
            id="identity-002",
            display_name="Jane Smith",
        ),
    }

    identity_repository.get_by_id.side_effect = (
        lambda identity_id: identities[identity_id]
    )
    placement_repository.get_for_identity.return_value = None
    placement_repository.create.side_effect = lambda record: record

    report = engine.apply(
        organization_id="organization-027",
        request=request_for(
            "identity-001",
            "identity-002",
        ),
        actor="platform-admin",
    )

    assert report.dry_run is False
    assert report.created_count == 2
    assert report.invalid_count == 0
    assert placement_repository.create.call_count == 2
    db.commit.assert_called_once_with()
    assert db.refresh.call_count == 2

    created_records = [
        call.args[0]
        for call in placement_repository.create.call_args_list
    ]

    assert {
        record.organization_id
        for record in created_records
    } == {
        "organization-027",
    }

    assert {
        record.created_by
        for record in created_records
    } == {
        "platform-admin",
    }


def test_apply_skips_existing_placement():
    (
        engine,
        db,
        placement_repository,
        organization_repository,
        identity_repository,
    ) = build_engine()

    organization_repository.get_by_id.return_value = (
        SimpleNamespace(id="organization-027")
    )
    identity_repository.get_by_id.return_value = (
        SimpleNamespace(
            id="identity-001",
            display_name="John Smith",
        )
    )
    placement_repository.get_for_identity.return_value = (
        SimpleNamespace(
            id="organizational-identity-001",
            display_name="John Smith",
        )
    )

    report = engine.apply(
        organization_id="organization-027",
        request=request_for("identity-001"),
        actor="platform-admin",
    )

    assert report.already_placed_count == 1
    assert report.created_count == 0
    placement_repository.create.assert_not_called()
    db.commit.assert_called_once_with()
