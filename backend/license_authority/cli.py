import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from app.domain.commercial_edition import CommercialEdition
from app.domain.commercial_purpose import CommercialPurpose
from license_authority.issuance import (
    LicenseIssuanceRequest,
    LicenseIssuanceService,
)
from license_authority.signing_key import (
    LicenseAuthoritySigningKey,
    load_license_authority_signing_key,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="usop-license-authority",
        description=(
            "Issue a cryptographically signed USOP License artifact."
        ),
    )

    parser.add_argument(
        "--organization-id",
        required=True,
        help="Canonical USOP Organization identifier.",
    )

    parser.add_argument(
        "--edition",
        required=True,
        choices=(
            "Community",
            "Starter",
            "Professional",
            "Enterprise",
        ),
        help="Commercial Edition.",
    )

    parser.add_argument(
        "--purpose",
        required=True,
        choices=(
            "Internal",
            "Development",
            "Evaluation",
            "Beta",
            "Production",
            "Partner",
        ),
        help="Commercial Purpose.",
    )

    parser.add_argument(
        "--effective-at",
        required=True,
        help="Timezone-aware ISO-8601 effective timestamp.",
    )

    parser.add_argument(
        "--expires-at",
        default=None,
        help="Optional timezone-aware ISO-8601 expiration timestamp.",
    )

    parser.add_argument(
        "--deployment-identifier",
        default=None,
        help="Optional stable USOP Deployment identifier.",
    )

    parser.add_argument(
        "--seat-limit",
        type=int,
        default=None,
        help="Optional commercial seat limit.",
    )

    parser.add_argument(
        "--module",
        action="append",
        default=[],
        dest="commercial_modules",
        help="Commercial module. May be supplied multiple times.",
    )

    parser.add_argument(
        "--entitlement",
        action="append",
        default=[],
        dest="feature_entitlements",
        help="Feature entitlement. May be supplied multiple times.",
    )

    parser.add_argument(
        "--signing-key-id",
        required=True,
        help="Vendor signing-key identifier.",
    )

    parser.add_argument(
        "--private-key-file",
        required=True,
        help="Path to operator-controlled private signing-key PEM.",
    )

    parser.add_argument(
        "--output-directory",
        required=True,
        help="Directory where the License artifact will be written.",
    )

    return parser


def _parse_datetime(
    value: str,
    *,
    field_name: str,
) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError(
            f"{field_name} must be a valid ISO-8601 timestamp."
        ) from error

    if (
        parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        raise ValueError(
            f"{field_name} must be timezone-aware."
        )

    return parsed


def load_cli_signing_key(
    args: argparse.Namespace,
) -> LicenseAuthoritySigningKey:
    try:
        with open(
            args.private_key_file,
            "rb",
        ) as key_file:
            private_key_pem = key_file.read()
    except OSError as error:
        raise ValueError(
            "Unable to read License Authority private-key file."
        ) from error

    return load_license_authority_signing_key(
        key_identifier=args.signing_key_id,
        private_key_pem=private_key_pem,
    )


def build_issuance_request(
    args: argparse.Namespace,
    *,
    issued_at: datetime | None = None,
) -> LicenseIssuanceRequest:
    effective_at = _parse_datetime(
        args.effective_at,
        field_name="effective_at",
    )

    expires_at = (
        _parse_datetime(
            args.expires_at,
            field_name="expires_at",
        )
        if args.expires_at is not None
        else None
    )

    issuance_time = (
        issued_at
        if issued_at is not None
        else datetime.now(UTC)
    )

    return LicenseIssuanceRequest(
        organization_id=args.organization_id,
        commercial_edition=CommercialEdition(
            args.edition
        ),
        commercial_purpose=CommercialPurpose(
            args.purpose
        ),
        issued_at=issuance_time,
        effective_at=effective_at,
        expires_at=expires_at,
        deployment_identifier=(
            args.deployment_identifier
        ),
        seat_limit=args.seat_limit,
        commercial_modules=tuple(
            args.commercial_modules
        ),
        feature_entitlements=tuple(
            args.feature_entitlements
        ),
    )


def issue_from_cli_args(
    args: argparse.Namespace,
    *,
    issued_at: datetime | None = None,
):
    signing_key = load_cli_signing_key(
        args
    )

    issuance_request = build_issuance_request(
        args,
        issued_at=issued_at,
    )

    return LicenseIssuanceService(
        signing_key
    ).issue(
        issuance_request
    )


def write_license_artifact(
    license_request,
    *,
    output_directory: str,
) -> Path:
    directory = Path(
        output_directory
    )

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    artifact_path = directory / (
        f"{license_request.license_identifier}.license.json"
    )

    payload = license_request.model_dump(
        mode="json"
    )

    serialized = json.dumps(
        payload,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    )

    artifact_path.write_text(
        serialized + "\n",
        encoding="utf-8",
    )

    return artifact_path


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    issued = issue_from_cli_args(
        args
    )

    artifact_path = write_license_artifact(
        issued,
        output_directory=args.output_directory,
    )

    print(
        str(artifact_path)
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
