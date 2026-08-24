from app.security.auth.AuthenticationAdapter import AuthenticationAdapter
from app.security.auth.AuthenticationProviderRegistry import (
    AuthenticationProviderRegistry,
    build_authentication_provider_registry,
)
from app.security.auth.EntraOidcAuthenticationAdapter import EntraOidcAuthenticationAdapter
from app.security.auth.EntraOidcValidationConfig import EntraOidcValidationConfig


class FakeJwkClient:
    pass


def _config():
    return EntraOidcValidationConfig(
        tenant_id="tenant-id",
        audience="api://usop",
        required_scope="access_as_user",
    )


def test_entra_adapter_implements_provider_neutral_contract():
    adapter = EntraOidcAuthenticationAdapter(
        _config(),
        jwk_client=FakeJwkClient(),
    )
    assert isinstance(adapter, AuthenticationAdapter)
    assert adapter.provider_name == "microsoft-entra"


def test_entra_provider_name_is_canonical_and_stable():
    assert EntraOidcAuthenticationAdapter.PROVIDER_NAME == "microsoft-entra"


def test_registry_builder_is_empty_without_provider_configuration():
    registry = build_authentication_provider_registry()
    assert isinstance(registry, AuthenticationProviderRegistry)
    assert registry.provider_names() == ()


def test_registry_builder_registers_entra_when_configured():
    registry = build_authentication_provider_registry(
        entra_config=_config(),
        entra_jwk_client=FakeJwkClient(),
    )
    assert registry.provider_names() == ("microsoft-entra",)


def test_registry_creates_configured_entra_adapter():
    client = FakeJwkClient()
    registry = build_authentication_provider_registry(
        entra_config=_config(),
        entra_jwk_client=client,
    )
    adapter = registry.create("microsoft-entra")
    assert isinstance(adapter, EntraOidcAuthenticationAdapter)
    assert adapter.provider_name == "microsoft-entra"
    assert adapter.config.tenant_id == "tenant-id"
    assert adapter.config.audience == "api://usop"
    assert adapter.jwk_client is client


def test_registry_lookup_normalization_still_applies_to_entra():
    registry = build_authentication_provider_registry(
        entra_config=_config(),
        entra_jwk_client=FakeJwkClient(),
    )
    assert isinstance(
        registry.create("  MICROSOFT-ENTRA  "),
        EntraOidcAuthenticationAdapter,
    )
