from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies.runtime_permission import (
    require_platform_permission,
)
from app.database.session import get_db
from app.schemas.license import (
    LicenseInstallDisposition,
    LicenseInstallRequest,
    LicenseInstallResult,
)
from app.security.license_signature_verifier import (
    LicenseSignatureVerifier,
)
from app.security.license_vendor_trust import (
    build_vendor_license_signing_key_registry,
)
from app.services.license_cryptographic_validator import (
    LicenseCryptographicValidator,
)
from app.services.license_service import (
    LicenseDeploymentBindingError,
    LicenseInstallationError,
    LicenseOrganizationConflictError,
    LicenseOrganizationNotFoundError,
    LicenseService,
)
from app.services.trusted_platform_caller import (
    TrustedPlatformCaller,
)


def get_license_cryptographic_validator(
) -> LicenseCryptographicValidator:
    """
    Return the product-controlled License verification authority.

    No customer-controlled signing material is accepted here. The default
    registry contains only release-controlled USOP vendor verification
    material.

    Tests may override this dependency with ephemeral trusted public material.
    """

    registry = build_vendor_license_signing_key_registry()

    verifier = LicenseSignatureVerifier(
        registry
    )

    return LicenseCryptographicValidator(
        verifier
    )

router = APIRouter(
    prefix=(
        "/api/v1/organizations/"
        "{organization_id}/licenses"
    ),
    tags=["Licenses"],
)


@router.post(
    "/install",
    response_model=LicenseInstallResult,
    status_code=status.HTTP_201_CREATED,
)
def install_license(
    organization_id: str,
    data: LicenseInstallRequest,
    response: Response,
    caller: TrustedPlatformCaller = Depends(
        require_platform_permission(
            "platform-administration.manage"
        )
    ),
    db: Session = Depends(get_db),
    cryptographic_validator: LicenseCryptographicValidator = Depends(
        get_license_cryptographic_validator
    ),
) -> LicenseInstallResult:
    """
    Structurally install an immutable signed License envelope.

    Actor attribution, lifecycle status, supersession, audit metadata, and
    transaction ownership are controlled by the backend.

    Cryptographic validity is required before persistence. Effective
    Subscription State remains derived elsewhere.
    """

    if (
        caller.organization_id != organization_id
        or data.organization_id != organization_id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested License installation target was not found.",
        )

    try:
        result = LicenseService(
            db,
            cryptographic_validator=(
                cryptographic_validator
            ),
        ).install(data)

    except LicenseOrganizationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except (
        LicenseOrganizationConflictError,
        LicenseDeploymentBindingError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except LicenseInstallationError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    if (
        result.disposition
        == LicenseInstallDisposition.ALREADY_INSTALLED
    ):
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_201_CREATED

    return result
