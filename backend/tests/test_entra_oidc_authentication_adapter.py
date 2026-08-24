from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from app.security.auth.EntraOidcAuthenticationAdapter import (
    EntraOidcAuthenticationAdapter,
    EntraOidcAuthenticationError,
)
from app.security.auth.EntraOidcValidationConfig import (
    EntraOidcValidationConfig,
)


TENANT = "11111111-2222-3333-4444-555555555555"
AUDIENCE = "api://usop-test-api"
REQUIRED_SCOPE = "access_as_user"
ISSUER = f"https://login.microsoftonline.com/{TENANT}/v2.0"
NOW = datetime.now(UTC).replace(microsecond=0)

PRIVATE_KEY = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
PUBLIC_KEY = PRIVATE_KEY.public_key()

OTHER_PRIVATE_KEY = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)


class StaticJwkClient:
    def __init__(self, key=PUBLIC_KEY, error=None):
        self.key = key
        self.error = error

    def get_signing_key_from_jwt(self, token):
        if self.error:
            raise self.error
        return SimpleNamespace(key=self.key)


def config():
    return EntraOidcValidationConfig(
        tenant_id=TENANT,
        audience=AUDIENCE,
        required_scope=REQUIRED_SCOPE,
    )


def claims(**overrides):
    values = {
        "aud": AUDIENCE,
        "exp": NOW + timedelta(minutes=10),
        "iat": NOW - timedelta(minutes=1),
        "iss": ISSUER,
        "nbf": NOW - timedelta(minutes=1),
        "oid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        "tid": TENANT,
        "ver": "2.0",
        "scp": REQUIRED_SCOPE,
    }
    values.update(overrides)
    return values


def encode(payload=None, *, key=PRIVATE_KEY, algorithm="RS256", headers=None):
    final_headers = {"kid": "test-key-1"}
    if headers:
        final_headers.update(headers)
    return jwt.encode(
        claims() if payload is None else payload,
        key,
        algorithm=algorithm,
        headers=final_headers,
    )


def adapter(jwk_client=None):
    return EntraOidcAuthenticationAdapter(
        config(),
        jwk_client=jwk_client or StaticJwkClient(),
    )


def test_valid_signed_token_returns_trusted_external_principal():
    principal = adapter().authenticate(
        encode(),
        now=NOW,
    )

    assert principal.identity_provider == "microsoft-entra"
    assert principal.external_tenant_id == TENANT
    assert (
        principal.external_subject_id
        == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    )
    assert principal.issuer == ISSUER
    assert principal.authenticated_at == NOW


def test_wrong_audience_fails_closed():
    token = encode(claims(aud="api://another-api"))

    with pytest.raises(EntraOidcAuthenticationError):
        adapter().authenticate(token)


def test_wrong_issuer_fails_closed():
    token = encode(
        claims(
            iss="https://login.microsoftonline.com/"
            "99999999-9999-9999-9999-999999999999/v2.0"
        )
    )

    with pytest.raises(EntraOidcAuthenticationError):
        adapter().authenticate(token)


def test_wrong_tenant_fails_closed_even_with_expected_issuer():
    token = encode(
        claims(
            tid="99999999-9999-9999-9999-999999999999"
        )
    )

    with pytest.raises(EntraOidcAuthenticationError):
        adapter().authenticate(token)


def test_wrong_signature_fails_closed():
    token = encode(key=OTHER_PRIVATE_KEY)

    with pytest.raises(EntraOidcAuthenticationError):
        adapter().authenticate(token)


def test_expired_token_fails_closed():
    token = encode(
        claims(
            exp=NOW - timedelta(seconds=1)
        )
    )

    with pytest.raises(EntraOidcAuthenticationError):
        adapter().authenticate(token)


def test_future_nbf_fails_closed():
    token = encode(
        claims(
            nbf=NOW + timedelta(minutes=10)
        )
    )

    with pytest.raises(EntraOidcAuthenticationError):
        adapter().authenticate(token)


@pytest.mark.parametrize("claim_name", ["oid", "tid"])
def test_missing_identity_claims_fail_closed(claim_name):
    payload = claims()
    payload.pop(claim_name)

    with pytest.raises(EntraOidcAuthenticationError):
        adapter().authenticate(encode(payload))


def test_v1_token_is_rejected():
    token = encode(
        claims(ver="1.0")
    )

    with pytest.raises(EntraOidcAuthenticationError):
        adapter().authenticate(token)


def test_algorithm_substitution_is_rejected_before_key_resolution():
    symmetric_secret = "not-a-valid-usop-rsa-key"
    token = jwt.encode(
        claims(),
        symmetric_secret,
        algorithm="HS256",
        headers={"kid": "symmetric-key"},
    )
    client = StaticJwkClient()

    with pytest.raises(
        EntraOidcAuthenticationError,
        match="algorithm",
    ):
        EntraOidcAuthenticationAdapter(
            config(),
            jwk_client=client,
        ).authenticate(token)


def test_missing_kid_is_rejected():
    token = jwt.encode(
        claims(),
        PRIVATE_KEY,
        algorithm="RS256",
        headers={"typ": "JWT"},
    )

    # PyJWT may generate no kid unless explicitly provided.
    with pytest.raises(EntraOidcAuthenticationError):
        adapter().authenticate(token)


def test_jwks_resolution_failure_fails_closed():
    token = encode()
    failing_client = StaticJwkClient(
        error=RuntimeError("network/key failure")
    )

    with pytest.raises(
        EntraOidcAuthenticationError,
        match="signing key",
    ):
        adapter(failing_client).authenticate(token)


def test_config_uses_tenant_specific_issuer_and_jwks():
    cfg = config()

    assert cfg.issuer == ISSUER
    assert TENANT in cfg.jwks_uri
    assert "common" not in cfg.jwks_uri
    assert "organizations" not in cfg.jwks_uri
