from __future__ import annotations

import inspect
from datetime import UTC, datetime, timedelta

import pytest
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
)

from app.api.dependencies import authenticated_caller
from app.api.dependencies import runtime_permission
from app.api.v1 import licenses as license_api
from app.database.session import get_db
from app.domain.commercial_edition import CommercialEdition
from app.domain.commercial_purpose import CommercialPurpose
from app.schemas.license import LicenseInstallRequest
from app.services.license_cryptographic_validator import (
    LicenseCryptographicValidator,
    LicensePayloadSignatureError,
)
from app.services.trusted_external_principal import (
    TrustedExternalPrincipal,
)
from app.services.trusted_platform_caller import (
    TrustedPlatformCaller,
)
from license_authority.issuance import (
    LicenseIssuanceRequest,
    LicenseIssuanceService,
)
from license_authority.signing_key import (
    load_license_authority_signing_key,
)


ORG_ID = "00000000-0000-0000-0000-000000000001"


def _trusted_caller() -> TrustedPlatformCaller:
    return TrustedPlatformCaller(
        organization_id=ORG_ID,
        platform_user_id="platform-admin-user-id",
        principal=TrustedExternalPrincipal(
            identity_provider="microsoft-entra",
            external_tenant_id="entra-tenant-id",
            external_subject_id="entra-subject-id",
        ),
    )


def _issued_license() -> LicenseInstallRequest:
    private_key = ec.generate_private_key(
        ec.SECP256R1()
    )

    private_pem = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )

    authority_key = load_license_authority_signing_key(
        key_identifier="authorization-test-key",
        private_key_pem=private_pem,
    )

    now = datetime(
        2026,
        9,
        3,
        12,
        0,
        tzinfo=UTC,
    )

    issued = LicenseIssuanceService(
        authority_key
    ).issue(
        LicenseIssuanceRequest(
            organization_id=ORG_ID,
            commercial_edition=(
                CommercialEdition.ENTERPRISE
            ),
            commercial_purpose=(
                CommercialPurpose.BETA
            ),
            issued_at=now,
            effective_at=now,
            expires_at=(
                now + timedelta(days=30)
            ),
            deployment_identifier=None,
            seat_limit=10,
            commercial_modules=(),
            feature_entitlements=(),
        )
    )

    return LicenseInstallRequest(
        **issued.model_dump(
            mode="python"
        )
    )


def test_license_install_declares_canonical_platform_admin_permission():
    source = inspect.getsource(
        license_api.install_license
    )

    assert (
        '"platform-administration.manage"'
        in source
    )
    assert (
        "TrustedPlatformCaller"
        in source
    )
    assert (
        "require_platform_permission"
        in source
    )
    assert (
        "caller.organization_id != organization_id"
        in source
    )
    assert (
        "data.organization_id != organization_id"
        in source
    )


def test_license_install_caller_is_not_part_of_request_schema():
    fields = (
        LicenseInstallRequest
        .model_fields
    )

    assert "caller" not in fields
    assert "actor" not in fields
    assert "platform_user_id" not in fields


def test_authorized_route_passes_license_to_service_without_browser_actor(
    monkeypatch,
):
    captured = {}

    class FakeResult:
        disposition = (
            license_api
            .LicenseInstallDisposition
            .INSTALLED
        )

    class FakeService:
        def __init__(
            self,
            db,
            *,
            cryptographic_validator,
        ):
            captured["db"] = db
            captured[
                "cryptographic_validator"
            ] = cryptographic_validator

        def install(
            self,
            request,
        ):
            captured["request"] = request
            return FakeResult()

    monkeypatch.setattr(
        license_api,
        "LicenseService",
        FakeService,
    )

    request = _issued_license()
    caller = _trusted_caller()
    validator = object()
    response = type(
        "ResponseStub",
        (),
        {"status_code": None},
    )()

    result = license_api.install_license(
        organization_id=ORG_ID,
        data=request,
        response=response,
        caller=caller,
        db=object(),
        cryptographic_validator=validator,
    )

    assert result.disposition == (
        license_api
        .LicenseInstallDisposition
        .INSTALLED
    )
    assert captured["request"] is request
    assert (
        captured["cryptographic_validator"]
        is validator
    )


def test_authorized_admin_still_requires_cryptographic_validation():
    request = _issued_license()

    class RejectingVerifier:
        def verify(
            self,
            *,
            canonical_payload,
            signature,
            signing_key_identifier,
        ):
            raise RuntimeError(
                "verification should be adapted "
                "through validator"
            )

    class RejectingValidator:
        def validate(
            self,
            request,
        ):
            raise LicensePayloadSignatureError(
                "License signature verification failed."
            )

    validator = RejectingValidator()

    with pytest.raises(
        LicensePayloadSignatureError
    ):
        validator.validate(
            request
        )


def test_license_endpoint_signature_exposes_caller_as_dependency_only():
    signature = inspect.signature(
        license_api.install_license
    )

    caller_parameter = (
        signature.parameters["caller"]
    )

    assert (
        caller_parameter.annotation
        is TrustedPlatformCaller
    )

    assert (
        "Depends"
        in repr(
            caller_parameter.default
        )
    )


def test_license_install_request_rejects_browser_supplied_actor():
    request = _issued_license()

    payload = request.model_dump(
        mode="python"
    )

    payload["actor"] = (
        "browser-controlled-attacker"
    )

    with pytest.raises(Exception):
        LicenseInstallRequest(
            **payload
        )

def _http_app():
    app = FastAPI()
    app.include_router(
        license_api.router
    )
    return app


def _json_payload(
    request: LicenseInstallRequest,
) -> dict:
    return request.model_dump(
        mode="json"
    )


def _install_runtime_authorization(
    monkeypatch,
    *,
    allowed: bool,
):
    class AuthorizationResult:
        def __init__(
            self,
            *,
            organization_id,
            platform_user_id,
            permission_key,
        ):
            self.allowed = allowed
            self.organization_id = organization_id
            self.platform_user_id = platform_user_id
            self.permission_key = permission_key

    class RuntimeAuthorization:
        def __init__(
            self,
            db,
        ):
            self.db = db

        def evaluate(
            self,
            *,
            organization_id,
            platform_user_id,
            permission_key,
        ):
            return AuthorizationResult(
                organization_id=organization_id,
                platform_user_id=platform_user_id,
                permission_key=permission_key,
            )

    monkeypatch.setattr(
        runtime_permission,
        "PlatformRuntimeAuthorizationService",
        RuntimeAuthorization,
    )


def test_http_valid_license_without_bearer_token_is_rejected_before_service(
    monkeypatch,
):
    constructed = False

    class ForbiddenService:
        def __init__(
            self,
            *args,
            **kwargs,
        ):
            nonlocal constructed
            constructed = True

            raise AssertionError(
                "LicenseService must not be "
                "constructed before authentication."
            )

    monkeypatch.setattr(
        license_api,
        "LicenseService",
        ForbiddenService,
    )

    app = _http_app()

    app.dependency_overrides[
        get_db
    ] = lambda: object()

    app.dependency_overrides[
        license_api.get_license_cryptographic_validator
    ] = lambda: object()

    client = TestClient(
        app,
        raise_server_exceptions=True,
    )

    response = client.post(
        f"/api/v1/organizations/"
        f"{ORG_ID}/licenses/install",
        json=_json_payload(
            _issued_license()
        ),
    )

    assert response.status_code == 401
    assert (
        response.json()["detail"]
        == "Bearer token is required."
    )
    assert constructed is False


def test_http_runtime_permission_denial_is_403_before_license_service(
    monkeypatch,
):
    constructed = False

    class ForbiddenService:
        def __init__(
            self,
            *args,
            **kwargs,
        ):
            nonlocal constructed
            constructed = True

            raise AssertionError(
                "LicenseService must not be "
                "constructed after authorization denial."
            )

    monkeypatch.setattr(
        license_api,
        "LicenseService",
        ForbiddenService,
    )

    _install_runtime_authorization(
        monkeypatch,
        allowed=False,
    )

    app = _http_app()

    app.dependency_overrides[
        authenticated_caller.get_authenticated_platform_caller
    ] = _trusted_caller

    app.dependency_overrides[
        get_db
    ] = lambda: object()

    app.dependency_overrides[
        license_api.get_license_cryptographic_validator
    ] = lambda: object()

    client = TestClient(
        app,
        raise_server_exceptions=True,
    )

    response = client.post(
        f"/api/v1/organizations/"
        f"{ORG_ID}/licenses/install",
        json=_json_payload(
            _issued_license()
        ),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Caller is not authorized "
        "for this operation."
    )
    assert constructed is False


def test_http_authorized_caller_reaches_license_service(
    monkeypatch,
):
    reached = False

    class ReachedService:
        def __init__(
            self,
            db,
            *,
            cryptographic_validator,
        ):
            assert db is not None
            assert cryptographic_validator is not None

        def install(
            self,
            request,
        ):
            nonlocal reached
            reached = True

            raise license_api.LicenseInstallationError(
                "authorized caller "
                "reached licensing layer"
            )

    monkeypatch.setattr(
        license_api,
        "LicenseService",
        ReachedService,
    )

    _install_runtime_authorization(
        monkeypatch,
        allowed=True,
    )

    app = _http_app()

    app.dependency_overrides[
        authenticated_caller.get_authenticated_platform_caller
    ] = _trusted_caller

    app.dependency_overrides[
        get_db
    ] = lambda: object()

    app.dependency_overrides[
        license_api.get_license_cryptographic_validator
    ] = lambda: object()

    client = TestClient(
        app,
        raise_server_exceptions=True,
    )

    response = client.post(
        f"/api/v1/organizations/"
        f"{ORG_ID}/licenses/install",
        json=_json_payload(
            _issued_license()
        ),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "authorized caller "
        "reached licensing layer"
    )
    assert reached is True


def test_http_cross_organization_license_target_fails_before_service(
    monkeypatch,
):
    constructed = False

    class ForbiddenService:
        def __init__(
            self,
            *args,
            **kwargs,
        ):
            nonlocal constructed
            constructed = True

            raise AssertionError(
                "Cross-Organization request "
                "must fail before LicenseService."
            )

    monkeypatch.setattr(
        license_api,
        "LicenseService",
        ForbiddenService,
    )

    _install_runtime_authorization(
        monkeypatch,
        allowed=True,
    )

    app = _http_app()

    app.dependency_overrides[
        authenticated_caller.get_authenticated_platform_caller
    ] = _trusted_caller

    app.dependency_overrides[
        get_db
    ] = lambda: object()

    app.dependency_overrides[
        license_api.get_license_cryptographic_validator
    ] = lambda: object()

    client = TestClient(
        app,
        raise_server_exceptions=True,
    )

    response = client.post(
        "/api/v1/organizations/"
        "00000000-0000-0000-0000-000000000099"
        "/licenses/install",
        json=_json_payload(
            _issued_license()
        ),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Requested License installation "
        "target was not found."
    )
    assert constructed is False
