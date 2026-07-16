from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.license import (
    LicenseInstallDisposition,
    LicenseInstallRequest,
    LicenseInstallResult,
)
from app.services.license_service import (
    LicenseDeploymentBindingError,
    LicenseInstallationError,
    LicenseOrganizationConflictError,
    LicenseOrganizationNotFoundError,
    LicenseService,
)


router = APIRouter(
    prefix="/api/v1/licenses",
    tags=["Licenses"],
)


@router.post(
    "/install",
    response_model=LicenseInstallResult,
    status_code=status.HTTP_201_CREATED,
)
def install_license(
    data: LicenseInstallRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> LicenseInstallResult:
    """
    Structurally install an immutable signed License envelope.

    Actor attribution, lifecycle status, supersession, audit metadata, and
    transaction ownership are controlled by the backend.

    Installation does not assert cryptographic validity or effective
    Subscription State.
    """

    try:
        result = LicenseService(db).install(data)

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
