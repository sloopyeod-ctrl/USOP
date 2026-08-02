import argparse
import json
from collections.abc import Sequence

from app.database.session import SessionLocal
from app.schemas.organizational_identity_placement import (
    OrganizationalIdentityPlacementItem,
    OrganizationalIdentityPlacementRequest,
)
from app.services.organizational_identity_placement_engine import (
    OrganizationalIdentityPlacementEngine,
    OrganizationalIdentityPlacementError,
)
from app.services.organizational_identity_service import (
    OrganizationalIdentityError,
    OrganizationalIdentityService,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="organizational-identity-placement",
        description="Preview, validate, apply, or report identity placement.",
    )
    parser.add_argument("--json", action="store_true", dest="json_output")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("preview", "validate", "apply"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("--organization-id", required=True)
        command_parser.add_argument(
            "--identity-id",
            action="append",
            required=True,
            dest="identity_ids",
        )

        if command == "apply":
            command_parser.add_argument("--actor", required=True)
            command_parser.add_argument(
                "--confirm-organization-id",
                required=True,
            )

    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("--organization-id", required=True)
    return parser


def build_request(
    identity_ids: Sequence[str],
) -> OrganizationalIdentityPlacementRequest:
    return OrganizationalIdentityPlacementRequest(
        placements=[
            OrganizationalIdentityPlacementItem(identity_id=value)
            for value in identity_ids
        ]
    )


def print_payload(payload: dict, *, json_output: bool) -> None:
    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return

    for key, value in payload.items():
        if key == "results":
            continue
        print(f"{key}: {value}")

    for result in payload.get("results", []):
        print(
            f"- {result['identity_id']}"
            f" | {result.get('display_name') or 'Unnamed'}"
            f" | {result['disposition']}"
            f" | {result['message']}"
        )


def execute(args: argparse.Namespace, *, db) -> int:
    if args.command == "report":
        records = OrganizationalIdentityService(
            db
        ).list_for_organization(args.organization_id)

        print_payload(
            {
                "organization_id": args.organization_id,
                "count": len(records),
                "results": [
                    {
                        "identity_id": record.identity_id,
                        "display_name": record.display_name,
                        "disposition": record.status,
                        "message": record.id,
                    }
                    for record in records
                ],
            },
            json_output=args.json_output,
        )
        return 0

    request = build_request(args.identity_ids)
    engine = OrganizationalIdentityPlacementEngine(db)

    if args.command in ("preview", "validate"):
        report = engine.preview(
            organization_id=args.organization_id,
            request=request,
        )
        print_payload(
            report.model_dump(mode="json"),
            json_output=args.json_output,
        )
        return 0 if (
            args.command == "preview"
            or report.can_apply
        ) else 2

    if args.confirm_organization_id != args.organization_id:
        print("Apply refused: Organization confirmation does not match.")
        return 2

    report = engine.apply(
        organization_id=args.organization_id,
        request=request,
        actor=args.actor,
    )
    print_payload(
        report.model_dump(mode="json"),
        json_output=args.json_output,
    )
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    db = SessionLocal()

    try:
        return execute(args, db=db)
    except (
        OrganizationalIdentityPlacementError,
        OrganizationalIdentityError,
    ) as error:
        print(f"Placement failed: {error}")
        return 2
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
