from datetime import datetime
from enum import StrEnum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.domain.commercial_edition import CommercialEdition
from app.domain.commercial_purpose import CommercialPurpose


class LicenseInstallDisposition(StrEnum):
    INSTALLED = "Installed"
    ALREADY_INSTALLED = "AlreadyInstalled"


class LicenseInstallRequest(BaseModel):
    """
    Canonical signed License envelope accepted by the installation service.

    Installation does not establish cryptographic or runtime validity.
    Status, supersession, actor attribution, and audit data are controlled by
    the backend and cannot be supplied by the client.
    """

    model_config = ConfigDict(extra="forbid")

    organization_id: str = Field(
        min_length=36,
        max_length=36,
    )

    license_identifier: str = Field(
        min_length=1,
        max_length=255,
    )

    commercial_edition: CommercialEdition
    commercial_purpose: CommercialPurpose

    license_format_version: str = Field(
        min_length=1,
        max_length=50,
    )

    issued_at: datetime
    effective_at: datetime
    expires_at: datetime | None = None

    deployment_identifier: str | None = Field(
        default=None,
        max_length=255,
    )

    seat_limit: int | None = Field(
        default=None,
        ge=1,
    )

    commercial_modules: list[str] | None = None
    feature_entitlements: list[str] | None = None

    canonical_payload: dict
    canonical_payload_hash: str = Field(
        min_length=64,
        max_length=64,
        pattern=r"^[a-fA-F0-9]{64}$",
    )

    signature: str = Field(
        min_length=1,
    )

    signing_key_identifier: str = Field(
        min_length=1,
        max_length=255,
    )

    @field_validator(
        "organization_id",
        "license_identifier",
        "license_format_version",
        "deployment_identifier",
        "signature",
        "signing_key_identifier",
        mode="before",
    )
    @classmethod
    def normalize_string(
        cls,
        value,
    ):
        if value is None:
            return None

        if not isinstance(value, str):
            return value

        return value.strip()

    @field_validator(
        "commercial_modules",
        "feature_entitlements",
    )
    @classmethod
    def normalize_string_lists(
        cls,
        value: list[str] | None,
    ) -> list[str] | None:
        if value is None:
            return None

        normalized = [
            item.strip()
            for item in value
            if item.strip()
        ]

        return list(dict.fromkeys(normalized))

    @model_validator(mode="after")
    def validate_dates(self):
        if self.expires_at is not None:
            if self.expires_at <= self.effective_at:
                raise ValueError(
                    "License expiration must occur after its effective date."
                )

        return self


class LicenseInstallResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    license_id: str
    license_identifier: str
    organization_id: str
    disposition: LicenseInstallDisposition
    superseded_license_id: str | None
    audit_event_id: str | None
