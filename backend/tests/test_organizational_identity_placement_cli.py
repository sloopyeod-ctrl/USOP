from unittest.mock import MagicMock, patch

from app.schemas.organizational_identity_placement import (
    OrganizationalIdentityPlacementReport,
    OrganizationalIdentityPlacementResultItem,
    PlacementDisposition,
)
from tools.organizational_identity_placement import (
    build_parser,
    build_request,
    execute,
)


def make_report(*, can_apply: bool = True):
    return OrganizationalIdentityPlacementReport(
        organization_id="organization-027",
        dry_run=True,
        requested_count=1,
        ready_count=1 if can_apply else 0,
        already_placed_count=0,
        invalid_count=0 if can_apply else 1,
        created_count=0,
        can_apply=can_apply,
        results=[
            OrganizationalIdentityPlacementResultItem(
                identity_id="identity-001",
                display_name="John Smith",
                disposition=(
                    PlacementDisposition.READY
                    if can_apply
                    else PlacementDisposition.INVALID
                ),
                message="Preview result.",
            )
        ],
    )


def test_build_request_preserves_ids():
    request = build_request(["identity-001", "identity-002"])
    assert [item.identity_id for item in request.placements] == [
        "identity-001",
        "identity-002",
    ]


def test_preview_calls_engine_only():
    args = build_parser().parse_args(
        [
            "preview",
            "--organization-id",
            "organization-027",
            "--identity-id",
            "identity-001",
        ]
    )

    with patch(
        "tools.organizational_identity_placement."
        "OrganizationalIdentityPlacementEngine"
    ) as engine_type:
        engine_type.return_value.preview.return_value = make_report()
        assert execute(args, db=MagicMock()) == 0
        engine_type.return_value.preview.assert_called_once()
        engine_type.return_value.apply.assert_not_called()


def test_validate_returns_two_for_invalid_report():
    args = build_parser().parse_args(
        [
            "validate",
            "--organization-id",
            "organization-027",
            "--identity-id",
            "identity-001",
        ]
    )

    with patch(
        "tools.organizational_identity_placement."
        "OrganizationalIdentityPlacementEngine"
    ) as engine_type:
        engine_type.return_value.preview.return_value = make_report(
            can_apply=False
        )
        assert execute(args, db=MagicMock()) == 2


def test_apply_requires_matching_confirmation():
    args = build_parser().parse_args(
        [
            "apply",
            "--organization-id",
            "organization-027",
            "--identity-id",
            "identity-001",
            "--actor",
            "platform-admin",
            "--confirm-organization-id",
            "organization-075",
        ]
    )

    with patch(
        "tools.organizational_identity_placement."
        "OrganizationalIdentityPlacementEngine"
    ) as engine_type:
        assert execute(args, db=MagicMock()) == 2
        engine_type.return_value.apply.assert_not_called()


def test_apply_delegates_to_engine():
    args = build_parser().parse_args(
        [
            "apply",
            "--organization-id",
            "organization-027",
            "--identity-id",
            "identity-001",
            "--actor",
            "platform-admin",
            "--confirm-organization-id",
            "organization-027",
        ]
    )

    report = make_report().model_copy(
        update={
            "dry_run": False,
            "ready_count": 0,
            "created_count": 1,
        }
    )

    with patch(
        "tools.organizational_identity_placement."
        "OrganizationalIdentityPlacementEngine"
    ) as engine_type:
        engine_type.return_value.apply.return_value = report
        assert execute(args, db=MagicMock()) == 0
        engine_type.return_value.apply.assert_called_once()
