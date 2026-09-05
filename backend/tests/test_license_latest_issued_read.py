from datetime import UTC, datetime
from inspect import signature
from types import SimpleNamespace

import pytest
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient

from app.api.dependencies import authenticated_caller
from app.api.dependencies import runtime_permission
from app.api.v1 import licenses as license_api
from app.database.session import get_db
from app.schemas.license import LicenseLatestIssuedRead
from app.services.trusted_external_principal import (
    TrustedExternalPrincipal,
)
from app.services.trusted_platform_caller import (
    TrustedPlatformCaller,
)


ORG_ID = "00000000-0000-0000-0000-000000000001"
FOREIGN_ORG_ID = "00000000-0000-0000-0000-000000000099"


def _trusted_caller(
    organization_id: str = ORG_ID,
) -> TrustedPlatformCaller:
    return TrustedPlatformCaller(
        organization_id=organization_id,
        platform_user_id="platform-admin-user-id",
        principal=TrustedExternalPrincipal(
            identity_provider="microsoft-entra",
            external_tenant_id="entra-tenant-id",
            external_subject_id="entra-subject-id",
        ),
    )


def _license_record():
    return SimpleNamespace(
        id="license-record-id",
        organization_id=ORG_ID,
        license_identifier="USOP-LIC-READ-001",
        status="Issued",
        commercial_edition="Enterprise",
        commercial_purpose="Beta",
        license_format_version="1",
        issued_at=datetime(
            2026,
            9,
            4,
            12,
            0,
            tzinfo=UTC,
        ),
        effective_at=datetime(
            2026,
            9,
            4,
            12,
            0,
            tzinfo=UTC,
        ),
        expires_at=datetime(
            2026,
            12,
            3,
            12,
            0,
            tzinfo=UTC,
        ),
        deployment_identifier=None,
        seat_limit=25,
        commercial_modules_json=[
            "identity-foundation",
        ],
        feature_entitlements_json=[
            "license-install",
        ],
        signing_key_identifier=(
            "usop-license-root-2026-01"
        ),
        supersedes_license_id=None,
        signature="must-not-be-exposed",
        canonical_payload_json={
            "secret": "must-not-be-exposed",
        },
        canonical_payload_hash=(
            "a" * 64
        ),
    )


def test_gate_uses_only_canonical_platform_administration_permission():
    source = (
        license_api
        .get_latest_issued_license
        .__wrapped__
        if hasattr(
            license_api.get_latest_issued_license,
            "__wrapped__",
        )
        else license_api.get_latest_issued_license
    )

    import inspect

    text = inspect.getsource(source)

    assert text.count(
        '"platform-administration.manage"'
    ) == 1

    forbidden = (
        "platform-administration.read",
        "licenses.read",
        "license.read",
        "platform-administrator",
    )

    for fragment in forbidden:
        assert fragment not in text


def test_gate_browser_cannot_supply_trusted_caller_identity():
    parameters = signature(
        license_api.get_latest_issued_license
    ).parameters

    forbidden = {
        "caller_id",
        "platform_user_id",
        "external_subject_id",
        "external_tenant_id",
        "identity_provider",
        "identity_issuer",
    }

    assert forbidden.isdisjoint(parameters)


def test_gate_foreign_org_stops_before_repository_construction(
    monkeypatch,
):
    constructed = False

    class ForbiddenRepository:
        def __init__(self, db):
            nonlocal constructed
            constructed = True

            raise AssertionError(
                "Repository must not be constructed "
                "for a foreign Organization."
            )

    monkeypatch.setattr(
        license_api,
        "LicenseRepository",
        ForbiddenRepository,
    )

    with pytest.raises(HTTPException) as captured:
        license_api.get_latest_issued_license(
            organization_id=FOREIGN_ORG_ID,
            caller=_trusted_caller(ORG_ID),
            db=object(),
        )

    assert captured.value.status_code == (
        status.HTTP_404_NOT_FOUND
    )
    assert captured.value.detail == (
        "License not found."
    )
    assert constructed is False


def test_gate_missing_latest_issued_is_non_enumerating_404(
    monkeypatch,
):
    class EmptyRepository:
        def __init__(self, db):
            self.db = db

        def get_latest_issued_for_organization(
            self,
            organization_id,
        ):
            assert organization_id == ORG_ID
            return None

    monkeypatch.setattr(
        license_api,
        "LicenseRepository",
        EmptyRepository,
    )

    with pytest.raises(HTTPException) as captured:
        license_api.get_latest_issued_license(
            organization_id=ORG_ID,
            caller=_trusted_caller(),
            db=object(),
        )

    assert captured.value.status_code == (
        status.HTTP_404_NOT_FOUND
    )
    assert captured.value.detail == (
        "License not found."
    )


def test_latest_issued_read_excludes_signature_and_payload_internals(
    monkeypatch,
):
    class Repository:
        def __init__(self, db):
            self.db = db

        def get_latest_issued_for_organization(
            self,
            organization_id,
        ):
            assert organization_id == ORG_ID
            return _license_record()

    monkeypatch.setattr(
        license_api,
        "LicenseRepository",
        Repository,
    )

    result = license_api.get_latest_issued_license(
        organization_id=ORG_ID,
        caller=_trusted_caller(),
        db=object(),
    )

    assert isinstance(
        result,
        LicenseLatestIssuedRead,
    )

    payload = result.model_dump()

    assert payload["organization_id"] == ORG_ID
    assert (
        payload["license_identifier"]
        == "USOP-LIC-READ-001"
    )
    assert (
        payload["signing_key_identifier"]
        == "usop-license-root-2026-01"
    )

    forbidden = {
        "signature",
        "canonical_payload",
        "canonical_payload_json",
        "canonical_payload_hash",
    }

    assert forbidden.isdisjoint(payload)


def test_latest_issued_route_contract_is_exact():
    expected = (
        "/api/v1/organizations/"
        "{organization_id}/licenses/latest-issued"
    )

    route = next(
        route
        for route in license_api.router.routes
        if route.path == expected
    )

    assert route.methods == {"GET"}

    response_field = route.response_field
    assert response_field is not None

    assert (
        route.response_model
        is LicenseLatestIssuedRead
    )


def test_schema_does_not_claim_effective_subscription_state():
    fields = set(
        LicenseLatestIssuedRead.model_fields
    )

    forbidden = {
        "subscription_state",
        "is_active",
        "commercially_effective",
        "grace_period",
        "seat_allocation",
    }

    assert forbidden.isdisjoint(fields)

def _http_app():
    app = FastAPI()
    app.include_router(
        license_api.router
    )
    return app


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
        def __init__(self, db):
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


def test_http_latest_issued_without_bearer_token_is_401(
    monkeypatch,
):
    constructed = False

    class ForbiddenRepository:
        def __init__(self, db):
            nonlocal constructed
            constructed = True

            raise AssertionError(
                "Repository must not be constructed "
                "before authentication."
            )

    monkeypatch.setattr(
        license_api,
        "LicenseRepository",
        ForbiddenRepository,
    )

    app = _http_app()

    app.dependency_overrides[
        get_db
    ] = lambda: object()

    client = TestClient(
        app,
        raise_server_exceptions=True,
    )

    response = client.get(
        f"/api/v1/organizations/"
        f"{ORG_ID}/licenses/latest-issued"
    )

    assert response.status_code == 401
    assert constructed is False


def test_http_latest_issued_permission_denial_is_403(
    monkeypatch,
):
    constructed = False

    class ForbiddenRepository:
        def __init__(self, db):
            nonlocal constructed
            constructed = True

            raise AssertionError(
                "Repository must not be constructed "
                "after authorization denial."
            )

    monkeypatch.setattr(
        license_api,
        "LicenseRepository",
        ForbiddenRepository,
    )

    _install_runtime_authorization(
        monkeypatch,
        allowed=False,
    )

    app = _http_app()

    app.dependency_overrides[
        authenticated_caller
        .get_authenticated_platform_caller
    ] = _trusted_caller

    app.dependency_overrides[
        get_db
    ] = lambda: object()

    client = TestClient(
        app,
        raise_server_exceptions=True,
    )

    response = client.get(
        f"/api/v1/organizations/"
        f"{ORG_ID}/licenses/latest-issued"
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Caller is not authorized "
        "for this operation."
    )
    assert constructed is False


def test_http_latest_issued_authorized_returns_safe_200(
    monkeypatch,
):
    class Repository:
        def __init__(self, db):
            self.db = db

        def get_latest_issued_for_organization(
            self,
            organization_id,
        ):
            assert organization_id == ORG_ID
            return _license_record()

    monkeypatch.setattr(
        license_api,
        "LicenseRepository",
        Repository,
    )

    _install_runtime_authorization(
        monkeypatch,
        allowed=True,
    )

    app = _http_app()

    app.dependency_overrides[
        authenticated_caller
        .get_authenticated_platform_caller
    ] = _trusted_caller

    app.dependency_overrides[
        get_db
    ] = lambda: object()

    client = TestClient(
        app,
        raise_server_exceptions=True,
    )

    response = client.get(
        f"/api/v1/organizations/"
        f"{ORG_ID}/licenses/latest-issued"
    )

    assert response.status_code == 200

    payload = response.json()

    assert (
        payload["license_identifier"]
        == "USOP-LIC-READ-001"
    )
    assert (
        payload["signing_key_identifier"]
        == "usop-license-root-2026-01"
    )

    forbidden = {
        "signature",
        "canonical_payload",
        "canonical_payload_json",
        "canonical_payload_hash",
        "subscription_state",
        "is_active",
        "commercially_effective",
    }

    assert forbidden.isdisjoint(payload)


def test_http_latest_issued_missing_is_404(
    monkeypatch,
):
    class EmptyRepository:
        def __init__(self, db):
            self.db = db

        def get_latest_issued_for_organization(
            self,
            organization_id,
        ):
            assert organization_id == ORG_ID
            return None

    monkeypatch.setattr(
        license_api,
        "LicenseRepository",
        EmptyRepository,
    )

    _install_runtime_authorization(
        monkeypatch,
        allowed=True,
    )

    app = _http_app()

    app.dependency_overrides[
        authenticated_caller
        .get_authenticated_platform_caller
    ] = _trusted_caller

    app.dependency_overrides[
        get_db
    ] = lambda: object()

    client = TestClient(
        app,
        raise_server_exceptions=True,
    )

    response = client.get(
        f"/api/v1/organizations/"
        f"{ORG_ID}/licenses/latest-issued"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "License not found."
    )
