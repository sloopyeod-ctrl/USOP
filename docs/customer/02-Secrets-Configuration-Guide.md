# USOP Core v1.0 - Secrets Configuration Guide

**Document:** 02-Secrets-Configuration-Guide  
**Release Track:** USOP Core v1.0 Release Candidate  
**Status:** Release Candidate Draft  
**Audience:** Security Engineers, Platform Engineers, Identity Engineers, System Administrators, Design Partners

## Purpose

This guide defines how customer-owned secrets and identity-provider credentials must be supplied to USOP Core v1.0.

The goal is to support secure, repeatable deployment without embedding credentials in source code, container images, documentation, screenshots, or release artifacts.

USOP must treat secrets as customer-owned configuration.

## Security Objective

USOP Core should support at least two deployment patterns:

1. Environment-managed secrets for smaller or controlled deployments.
2. External secret-provider references for organizations that use an enterprise secrets manager.

The selected secret source must be explicit.

A secret reference, UUID, record identifier, path, or key name must never implicitly identify the secret provider.

## Never Place Secrets In

Do not place credentials, tokens, private keys, or secret values in:

- source code;
- committed `.env` files;
- Dockerfiles;
- container images;
- `docker-compose.yml`;
- screenshots;
- tickets;
- chat messages;
- troubleshooting bundles;
- customer documentation;
- sample configuration;
- release archives.

The distributed `.env.template` must contain names and examples only, never working credentials.

## Customer-Owned Configuration

USOP configuration should distinguish non-secret identity information from secret material.

Typical non-secret values include:

- organization identifier;
- identity provider selection;
- Microsoft Entra tenant identifier;
- Microsoft Entra application/client identifier;
- secret-source mode;
- external secret-provider name;
- external secret reference.

Secret values include:

- client secrets;
- access credentials for a secret provider;
- private keys;
- bearer tokens;
- certificates containing private key material.

## Supported Secret Modes

### Mode 1 - Environment Secret

This mode is appropriate when the customer intentionally chooses to provide the Entra application secret through the runtime environment.

Conceptual example:

```dotenv
USOP_IDENTITY_PROVIDER=entra
ENTRA_TENANT_ID=<customer-tenant-id>
ENTRA_CLIENT_ID=<customer-application-id>

USOP_SECRET_SOURCE=environment
ENTRA_CLIENT_SECRET=<customer-secret>
```

The exact variable names used by the frozen USOP Core v1.0 configuration contract must be validated against the application before RC1 release.

Do not copy this conceptual block into production until the final `.env.template` is generated from the validated configuration contract.

### Mode 2 - External Secret Provider

This mode is appropriate when the customer stores credentials in an approved secrets platform.

Conceptual example:

```dotenv
USOP_IDENTITY_PROVIDER=entra
ENTRA_TENANT_ID=<customer-tenant-id>
ENTRA_CLIENT_ID=<customer-application-id>

USOP_SECRET_SOURCE=provider
USOP_SECRET_PROVIDER=keeper
ENTRA_SECRET_REFERENCE=<customer-owned-reference>
```

The important design rule is:

```text
Provider != Reference
```

The provider tells USOP how to retrieve the secret.

The reference tells that provider which secret to retrieve.

A UUID alone must never mean "Keeper."

## Secret Provider Neutrality

USOP Core should preserve a provider-neutral secret abstraction.

Customer environments may use platforms such as:

- Keeper;
- Azure Key Vault;
- AWS Secrets Manager;
- HashiCorp Vault;
- another supported customer-owned provider.

Not every provider must be available in the first customer release.

The release documentation must state exactly which providers are supported by the frozen RC artifact.

Unsupported providers must not be implied as operational.

## Microsoft Entra Credential Model

USOP Core uses customer-owned Microsoft Entra application credentials to access the Microsoft Graph permissions required by the release.

The customer is responsible for:

- creating or approving the application registration;
- assigning only the documented Microsoft Graph permissions;
- granting administrator consent where required;
- creating or providing the supported credential type;
- rotating credentials according to customer policy;
- revoking credentials when USOP is decommissioned.

USOP must not create broad Microsoft Graph permissions merely to simplify deployment.

The final required permissions will be documented in:

```text
03-Security-Deployment-Guide.md
```

after the RC security validation pass confirms the minimum working permission set.

## .env File Handling

If the environment-secret deployment mode is used, the customer-owned `.env` file must be treated as sensitive.

Recommended handling:

- create it from the distributed `.env.template`;
- restrict filesystem access to the deployment administrators and runtime account as appropriate;
- do not commit it to Git;
- do not include it in support bundles;
- do not copy it into documentation;
- do not transmit it through email or chat;
- remove it securely when the deployment is decommissioned.

The release package should include a `.gitignore` or equivalent protection that prevents accidental source-control inclusion where applicable.

## External Secret Reference Handling

A secret reference is not automatically a secret value, but it should still be treated as deployment-sensitive configuration.

References may reveal:

- record structure;
- internal naming;
- environment segmentation;
- provider usage;
- application relationships.

Do not publish customer-specific references in examples or public issue reports.

## Keeper-Oriented Deployments

Where the frozen USOP release supports Keeper, the customer should supply:

- the explicit provider value identifying Keeper;
- the customer-owned Keeper record or secret reference required by the integration;
- any Keeper access configuration required by the supported USOP secret-provider implementation.

Do not assume that any arbitrary UUID is a valid Keeper reference.

Do not place Keeper credentials inside the USOP application image.

The final Keeper-specific configuration fields must be generated from and validated against the actual USOP secret-provider implementation before RC1 freeze.

## Other Secret Managers

If additional providers are supported in RC1, each provider must have a documented configuration section containing:

- provider identifier;
- reference format;
- authentication mechanism;
- required network access;
- least-privilege expectations;
- validation procedure;
- rotation behavior;
- failure behavior.

If a provider is not validated in RC1, document it as unsupported or planned rather than leaving ambiguous placeholders.

## Secret Rotation

Secret rotation must not require a code change.

The desired operational model is:

1. customer rotates the credential in the authoritative location;
2. customer updates the environment secret or provider-held secret as required;
3. USOP reloads or restarts according to the documented release behavior;
4. provider connectivity is revalidated;
5. no application source modification occurs.

The exact reload/restart behavior must be frozen during deployment validation.

## Startup Validation

Before synchronization begins, USOP should fail safely when required secret configuration is incomplete.

Configuration validation should distinguish between:

- missing tenant identifier;
- missing application/client identifier;
- invalid secret-source mode;
- missing environment secret;
- missing external provider selection;
- missing secret reference;
- unsupported secret provider;
- secret retrieval failure;
- authentication failure.

Customer-facing errors must not echo secret values.

## Logging Requirements

USOP logs must never intentionally emit:

- client secrets;
- access tokens;
- refresh tokens;
- private keys;
- full secret-provider credentials;
- complete `.env` contents.

Where identifiers are operationally useful, logs should expose only the minimum non-secret context required for troubleshooting.

## Troubleshooting Rules

When secret configuration fails:

1. Confirm the selected secret-source mode.
2. Confirm required non-secret identifiers.
3. Confirm the secret value or reference exists.
4. Confirm external provider selection when applicable.
5. Confirm USOP can reach the external secret provider if required.
6. Confirm the secret-provider identity has only the required access.
7. Confirm the Entra credential is valid and not expired.
8. Confirm Microsoft Graph permissions and admin consent.
9. Review sanitized logs.
10. Re-run provider validation.

Do not paste the secret into a terminal command merely to test whether it works if that command will expose it in shell history.

## Example .env.template Design

The final `.env.template` should be generated only after the actual runtime configuration contract is inspected and frozen.

Its structure should resemble:

```dotenv
# -----------------------------------------------------------------------------
# USOP Core v1.0 - Customer Configuration
# -----------------------------------------------------------------------------

# Organization
USOP_ORGANIZATION_ID=

# Identity provider
USOP_IDENTITY_PROVIDER=entra

# Microsoft Entra
ENTRA_TENANT_ID=
ENTRA_CLIENT_ID=

# Secret source: environment | provider
USOP_SECRET_SOURCE=environment

# Environment mode only
ENTRA_CLIENT_SECRET=

# External provider mode only
# USOP_SECRET_PROVIDER=
# ENTRA_SECRET_REFERENCE=
```

This block is a design target, not confirmation of the final variable names.

Before customer release, RC deployment validation must reconcile this template with the actual application settings and remove any variable that is unused or incorrectly named.

## Customer Validation Checklist

Before first synchronization:

- [ ] `.env.template` contains no real secret.
- [ ] Customer `.env` is excluded from source control.
- [ ] Tenant identifier belongs to the intended customer tenant.
- [ ] Client/application identifier belongs to the intended Entra application.
- [ ] Secret-source mode is explicit.
- [ ] Only one active secret path is used for the Entra credential.
- [ ] External provider is explicit when provider mode is selected.
- [ ] Secret reference is customer-owned.
- [ ] Required Graph permissions match the Security Deployment Guide.
- [ ] Admin consent is complete where required.
- [ ] Secret values are absent from logs.
- [ ] Provider authentication succeeds.
- [ ] Initial synchronization succeeds.

## Release Freeze Requirements

Before RC1 is distributed, the final secrets contract must be validated against the exact frozen application artifact.

The release team must confirm:

- exact environment variable names;
- which values are required;
- which values are optional;
- supported secret-source modes;
- supported external secret providers;
- supported reference formats;
- credential reload/restart behavior;
- secret redaction in logs;
- configuration validation behavior;
- final `.env.template`;
- final security/network dependencies.

No secret configuration field should be documented based on assumption.

## Relationship to Other Customer Documents

Read this guide with:

- `01-Installation-Guide.md`
- `03-Security-Deployment-Guide.md`
- `07-Release-Notes.md`
- `08-Known-Limitations.md`

The Installation Guide explains deployment sequence.

This guide explains credential and secret handling.

The Security Deployment Guide defines Graph permissions, network requirements, and least-privilege expectations.

## Success Criteria

> **A customer security or platform team should be able to configure USOP credentials without embedding secrets in the release, exposing credentials during troubleshooting, or depending on undocumented developer knowledge.**

If the credential path is ambiguous, the release is not ready.
