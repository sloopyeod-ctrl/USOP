# USOP Core - Secrets Configuration Guide

**Document:** 02-Secrets-Configuration-Guide
**Release:** 0.14.0-dp2-final
**Release Stage:** Design Partner Release Candidate
**Status:** Frozen Design Partner Documentation
**Audience:** Security Engineers, Platform Engineers, Identity Engineers, System Administrators, Design Partners

## Purpose

This guide defines the validated customer-owned secret and Microsoft Entra configuration contract for USOP Core 0.14.0-dp2-final.

USOP secrets must remain customer-owned configuration and must not be embedded in source code, container images, documentation, screenshots, or distributed release artifacts.

## Supported Secret Provider

The only operationally supported secret provider in this Design Partner release is USOP_SECRET_PROVIDER=env.

Customer secret values are supplied through the runtime environment file used by Docker Compose.

USOP preserves a provider-neutral secret-provider architecture for future releases.

Keeper, Azure Key Vault, AWS Secrets Manager, HashiCorp Vault, and other external secret managers are not operationally supported by 0.14.0-dp2-final.

Do not configure an unsupported provider merely because its name appears in architecture, source abstractions, or future-product documentation.

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

The distributed `.env.release.example` must contain configuration names and placeholders only, never working credentials.

## Customer-Owned Configuration

The Design Partner package contains .env.release.example.

Create the customer-owned runtime configuration by copying it to .env.release.

Do not place working credentials into .env.release.example.

## Frozen Environment Contract

The customer deployment requires the following configuration values:

POSTGRES_DB=<customer-database-name>
POSTGRES_USER=<customer-database-user>
POSTGRES_PASSWORD=<customer-generated-high-entropy-password>

USOP_SECRET_PROVIDER=env

MS_GRAPH_TENANT_ID=<customer-entra-tenant-id>
MS_GRAPH_CLIENT_ID=<graph-application-client-id>
MS_GRAPH_CLIENT_SECRET=<graph-application-client-secret>

USOP_AUTH_ENTRA_TENANT_ID=<entra-tenant-id-for-usop-callers>
USOP_AUTH_ENTRA_AUDIENCE=<usop-api-audience>
USOP_AUTH_ENTRA_REQUIRED_SCOPE=access_as_user

USOP_WEB_PORT=8080

Values shown inside angle brackets are descriptive placeholders and must be replaced with customer-owned configuration.

## Secret Classification

POSTGRES_PASSWORD and MS_GRAPH_CLIENT_SECRET are secret values and must be protected accordingly.

Tenant identifiers, application identifiers, API audience values, scope names, database names, database usernames, and port numbers are configuration values but should still be handled according to customer deployment policy.

## Supported Secret Mode

USOP Core 0.14.0-dp2-final supports environment-managed secrets through USOP_SECRET_PROVIDER=env.

External secret-provider retrieval is not operationally supported in this release.

The provider-neutral secret architecture remains a future compatibility boundary and does not imply current support for Keeper or another external secret manager.

## Microsoft Entra Trust Boundaries

USOP Core uses Microsoft Entra for two distinct security relationships.

These configuration groups must remain explicit even when they use the same Microsoft Entra tenant.

## Outbound Microsoft Graph Authentication

USOP authenticates to Microsoft Graph using:

MS_GRAPH_TENANT_ID
MS_GRAPH_CLIENT_ID
MS_GRAPH_CLIENT_SECRET

These values identify the customer-owned application credential used for supported Microsoft Graph collection.

The customer is responsible for:

- creating or approving the Microsoft Graph application registration;
- granting only the permissions documented for this release;
- granting administrator consent where required;
- generating and protecting the client secret;
- rotating or revoking the credential according to customer policy.

USOP must not request broader Microsoft Graph permissions merely to simplify deployment.

Required Graph permissions are documented in 03-Security-Deployment-Guide.md.

## Inbound USOP API Authentication

Protected USOP API operations validate delegated Microsoft Entra access tokens using:

USOP_AUTH_ENTRA_TENANT_ID
USOP_AUTH_ENTRA_AUDIENCE
USOP_AUTH_ENTRA_REQUIRED_SCOPE

The validated required delegated scope for this release is:

access_as_user

The inbound authentication configuration defines which tenant may issue tokens, which audience the token must target, and which delegated scope must be present.

Do not automatically substitute MS_GRAPH_CLIENT_ID for USOP_AUTH_ENTRA_AUDIENCE.

Do not automatically alias MS_GRAPH_TENANT_ID to USOP_AUTH_ENTRA_TENANT_ID in configuration.

A deployment may intentionally use the same Entra tenant for both trust boundaries, but the configuration fields and security purposes remain separate.

Missing or invalid inbound authentication configuration causes protected API access to fail closed.

## .env.release File Handling

The customer-owned .env.release file contains deployment-sensitive configuration and secret values.

Required handling:

- create it from the distributed .env.release.example;
- restrict filesystem access to authorized deployment administrators;
- do not commit it to Git or another source repository;
- do not include it in support bundles;
- do not copy it into documentation or screenshots;
- do not transmit it through ordinary email or chat;
- remove it securely when the deployment is decommissioned.

The distributed .env.release.example must never contain working credentials.

## External Secret Providers

External secret-provider retrieval is not supported by 0.14.0-dp2-final.

Keeper, Azure Key Vault, AWS Secrets Manager, HashiCorp Vault, and similar providers remain future architecture targets only.

Do not configure an external secret reference or provider identifier in this release.

## Secret Rotation

Secret rotation does not require an application source-code change.

For this release, the validated operational sequence is:

1. rotate the credential in the authoritative customer system;
2. update the corresponding value in .env.release;
3. recreate or restart the affected USOP service using the customer Compose deployment;
4. verify platform health and provider connectivity;
5. confirm that no secret value appears in logs.

A normal Docker Compose restart was validated during clean-room acceptance and preserved database schema, service health, and readiness.

## Startup Validation

Before startup, validate the customer configuration with:

docker compose -f docker-compose.yml --env-file .env.release config

The command must succeed before installation continues.

Required values must not be left blank or replaced with fake placeholder values merely to satisfy Compose.

Customer-facing errors and logs must not echo secret values.

## Logging Requirements

USOP logs must never intentionally emit:

- client secrets;
- access tokens;
- refresh tokens;
- private keys;
- database passwords;
- complete .env.release contents.

Identifiers should be exposed only when they are non-secret and operationally necessary.

## Troubleshooting Rules

When credential or authentication configuration fails:

1. confirm that .env.release was created from the supplied template;
2. confirm all required values are populated without printing their values;
3. confirm USOP_SECRET_PROVIDER=env;
4. distinguish outbound MS_GRAPH_* configuration from inbound USOP_AUTH_ENTRA_* configuration;
5. confirm Microsoft Graph permissions and administrator consent;
6. confirm the Graph client secret is valid and not expired;
7. confirm the inbound API audience and delegated access_as_user scope;
8. verify required network and DNS access;
9. review sanitized logs only;
10. re-run health and connectivity validation.

Do not paste secret values directly into terminal commands when doing so would expose them in shell history.

## Customer Validation Checklist

Before first operational synchronization, confirm:

- [ ] .env.release was created from the supplied .env.release.example.
- [ ] .env.release contains no CHANGE_ME placeholders.
- [ ] .env.release is excluded from source control.
- [ ] POSTGRES_DB is customer controlled.
- [ ] POSTGRES_USER is customer controlled.
- [ ] POSTGRES_PASSWORD is unique and high entropy.
- [ ] USOP_SECRET_PROVIDER=env.
- [ ] MS_GRAPH_TENANT_ID belongs to the intended customer tenant.
- [ ] MS_GRAPH_CLIENT_ID identifies the approved Graph application.
- [ ] MS_GRAPH_CLIENT_SECRET is valid and protected.
- [ ] Required Microsoft Graph permissions match the Security Deployment Guide.
- [ ] Microsoft Graph administrator consent is complete where required.
- [ ] USOP_AUTH_ENTRA_TENANT_ID identifies the intended inbound-authentication tenant.
- [ ] USOP_AUTH_ENTRA_AUDIENCE identifies the USOP API audience.
- [ ] USOP_AUTH_ENTRA_REQUIRED_SCOPE=access_as_user.
- [ ] Outbound Graph configuration and inbound USOP API authentication remain explicit trust boundaries.
- [ ] docker compose configuration validation succeeds.
- [ ] No secret values appear in logs.
- [ ] /health returns HTTP 200 after deployment.
- [ ] /ready returns HTTP 200 after deployment.

## Validated Release Behavior

The frozen 0.14.0-dp2-final package was clean-room installed using customer-style configuration and the shipped Docker image archives.

The validation confirmed:

- required environment values were enforced by Docker Compose;
- environment-managed secret configuration was accepted;
- PostgreSQL initialized successfully;
- migrations completed successfully;
- API and Web became healthy;
- /health returned HTTP 200;
- /ready returned HTTP 200;
- a normal Docker Compose restart preserved schema and service readiness.

No real customer or developer secret values are included in this document.

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
