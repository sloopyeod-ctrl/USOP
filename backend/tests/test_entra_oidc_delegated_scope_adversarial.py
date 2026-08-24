from __future__ import annotations

import inspect

from app.api.dependencies import authenticated_caller
from app.security.auth.EntraOidcAuthenticationAdapter import (
    EntraOidcAuthenticationAdapter,
)
from app.security.auth.EntraOidcValidationConfig import (
    EntraOidcValidationConfig,
)
from app.services.trusted_external_principal import (
    TrustedExternalPrincipal,
)


def test_gate_scope_requirement_is_provider_configuration():
    signature = inspect.signature(
        EntraOidcValidationConfig
    )

    assert "required_scope" in signature.parameters

    config = EntraOidcValidationConfig(
        tenant_id="tenant",
        audience="api://usop",
        required_scope="access_as_user",
    )

    assert config.required_scope == "access_as_user"


def test_gate_scope_configuration_has_no_default_bypass():
    parameter = inspect.signature(
        EntraOidcValidationConfig
    ).parameters["required_scope"]

    assert parameter.default is inspect.Parameter.empty


def test_gate_adapter_owns_delegated_scope_validation():
    source = inspect.getsource(
        EntraOidcAuthenticationAdapter.authenticate
    )

    assert '"scp"' in source
    assert "required_scope" in source


def test_gate_scope_match_is_discrete_not_substring():
    source = inspect.getsource(
        EntraOidcAuthenticationAdapter.authenticate
    )

    assert ".split()" in source
    assert "frozenset(" in source

    forbidden = (
        "required_scope in delegated_scope_claim",
        "delegated_scope_claim.find(",
        "startswith(",
        "endswith(",
    )

    for fragment in forbidden:
        assert fragment not in source


def test_gate_roles_cannot_replace_delegated_scope():
    source = inspect.getsource(
        EntraOidcAuthenticationAdapter.authenticate
    )

    assert 'payload,\n            "scp",' in source
    assert '"roles"' not in source
    assert "'roles'" not in source


def test_gate_scope_is_not_hard_coded_in_adapter():
    source = inspect.getsource(
        EntraOidcAuthenticationAdapter
    )

    assert '"access_as_user"' not in source
    assert "'access_as_user'" not in source


def test_gate_scope_is_required_by_http_auth_configuration():
    source = inspect.getsource(
        authenticated_caller._authentication_configuration
    )

    assert "usop_auth_entra_required_scope" in source
    assert "required_scope=required_scope" in source


def test_gate_missing_scope_configuration_fails_with_other_auth_config():
    source = inspect.getsource(
        authenticated_caller._authentication_configuration
    )

    assert (
        "if not tenant_id or not audience or not required_scope:"
        in source
    )


def test_gate_scope_does_not_enter_trusted_principal_identity():
    source = inspect.getsource(
        TrustedExternalPrincipal
    )

    assert "scope" not in source.lower()
    assert "permission" not in source.lower()
    assert "role" not in source.lower()


def test_gate_scope_validation_does_not_grant_platform_authorization():
    source = inspect.getsource(
        EntraOidcAuthenticationAdapter
    )

    forbidden = (
        "TrustedPlatformCaller",
        "PlatformRuntimeAuthorizationService",
        "PlatformUserRepository",
        "PlatformRoleAssignment",
        "PlatformPermission",
        "grant_permission",
        "assign_role",
        "seat_allocated",
        "LicenseRepository",
        ".commit(",
        ".rollback(",
    )

    for fragment in forbidden:
        assert fragment not in source


def test_gate_scope_policy_remains_separate_from_graph_credentials():
    source = inspect.getsource(
        authenticated_caller._authentication_configuration
    )

    assert "MS_GRAPH" not in source
    assert "ms_graph" not in source


def test_gate_scope_is_checked_after_verified_decode():
    source = inspect.getsource(
        EntraOidcAuthenticationAdapter.authenticate
    )

    decode_position = source.index("payload = jwt.decode(")
    scope_position = source.index(
        'delegated_scope_claim = self._required_text('
    )
    principal_position = source.index(
        "return TrustedExternalPrincipal("
    )

    assert decode_position < scope_position < principal_position
