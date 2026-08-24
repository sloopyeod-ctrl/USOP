import inspect

from app.security.auth.AuthenticationAdapter import AuthenticationAdapter
from app.security.auth.AuthenticationProviderRegistry import (
    AuthenticationProviderRegistry,
    build_authentication_provider_registry,
)
from app.security.auth.EntraOidcAuthenticationAdapter import (
    EntraOidcAuthenticationAdapter,
)
from app.security.auth.EntraOidcValidationConfig import (
    EntraOidcValidationConfig,
)


class FakeJwkClient:
    pass


def _config():
    return EntraOidcValidationConfig(
        tenant_id="tenant-id",
        audience="api://usop",
        required_scope="access_as_user",
    )


def _source(obj):
    return inspect.getsource(obj)


def test_gate_entra_is_only_authentication_adapter():
    assert issubclass(
        EntraOidcAuthenticationAdapter,
        AuthenticationAdapter,
    )

    source = _source(EntraOidcAuthenticationAdapter)

    forbidden = (
        "TrustedPlatformCaller",
        "TrustedCallerIdentityService",
        "PlatformRuntimeAuthorizationService",
        "PlatformUserRepository",
        "LicenseRepository",
        "grant_permission",
        "assign_role",
        ".commit(",
        ".rollback(",
    )

    for token in forbidden:
        assert token not in source


def test_gate_entra_provider_identity_is_canonical():
    assert (
        EntraOidcAuthenticationAdapter.PROVIDER_NAME
        == "microsoft-entra"
    )

    adapter = EntraOidcAuthenticationAdapter(
        _config(),
        jwk_client=FakeJwkClient(),
    )

    assert adapter.provider_name == "microsoft-entra"


def test_gate_registry_builder_registers_nothing_without_configuration():
    registry = build_authentication_provider_registry()

    assert registry.provider_names() == ()
    assert registry.create("microsoft-entra") is None


def test_gate_registry_builder_registers_only_configured_entra():
    registry = build_authentication_provider_registry(
        entra_config=_config(),
        entra_jwk_client=FakeJwkClient(),
    )

    assert registry.provider_names() == (
        "microsoft-entra",
    )


def test_gate_registry_builder_does_not_authenticate():
    source = _source(
        build_authentication_provider_registry
    )

    assert ".authenticate(" not in source
    assert "TrustedPlatformCaller" not in source
    assert "TrustedCallerIdentityService" not in source
    assert "PlatformRuntimeAuthorizationService" not in source


def test_gate_registry_builder_does_not_own_platform_user_lifecycle():
    source = _source(
        build_authentication_provider_registry
    )

    forbidden = (
        "PlatformUserRepository",
        "activate(",
        "reactivate(",
        "suspend(",
        "disable(",
    )

    for token in forbidden:
        assert token not in source


def test_gate_registry_builder_does_not_own_licensing_or_seats():
    source = _source(
        build_authentication_provider_registry
    )

    assert "LicenseRepository" not in source
    assert "SeatRepository" not in source


def test_gate_entra_registration_preserves_registry_type():
    registry = build_authentication_provider_registry(
        entra_config=_config(),
        entra_jwk_client=FakeJwkClient(),
    )

    assert isinstance(
        registry,
        AuthenticationProviderRegistry,
    )


def test_gate_factory_returns_fresh_adapter_instances():
    registry = build_authentication_provider_registry(
        entra_config=_config(),
        entra_jwk_client=FakeJwkClient(),
    )

    first = registry.create("microsoft-entra")
    second = registry.create("microsoft-entra")

    assert first is not second
    assert isinstance(
        first,
        EntraOidcAuthenticationAdapter,
    )
    assert isinstance(
        second,
        EntraOidcAuthenticationAdapter,
    )


def test_gate_provider_specific_config_does_not_enter_base_contract():
    source = _source(AuthenticationAdapter)

    assert "tenant_id" not in source
    assert "audience" not in source
    assert "jwks" not in source.lower()
    assert "microsoft" not in source.lower()
    assert "entra" not in source.lower()


def test_gate_registry_core_remains_provider_neutral():
    source = _source(AuthenticationProviderRegistry)

    assert "EntraOidcAuthenticationAdapter" not in source
    assert "Microsoft" not in source
    assert "Okta" not in source
    assert "Google" not in source
    assert "SecureW2" not in source
