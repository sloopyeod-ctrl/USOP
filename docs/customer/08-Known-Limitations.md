# USOP Core v1.0 - Known Limitations

**Document:** 08-Known-Limitations
**Release:** 0.14.0-dp2-final
**Status:** Frozen Design Partner Documentation
**Audience:** Design Partners, Security Leaders, Security Analysts, IAM Teams, Platform Teams, Deployment Teams

## Purpose

This document defines the known boundaries, unsupported scenarios, planned capabilities, and release assumptions for USOP Core v1.0.

Its purpose is to prevent surprises during Design Partner evaluation.

A known limitation is not automatically a defect.

A defect is behavior that contradicts the documented release behavior.

## Release Philosophy

USOP Core v1.0 is intentionally focused.

The release establishes the permanent investigation model and validates that model in realistic customer environments.

Future versions should expand providers and intelligence domains without forcing users to relearn the core workflow.

The objective is evolution rather than replacement.

## Current Scope

RC1 is centered on identity-focused operational intelligence.

The initial supported provider focus is Microsoft Entra ID.

The supported connector behaviors, Microsoft Graph permissions, secret-provider mode, deployment requirements, and runtime assumptions documented here are reconciled against the frozen 0.14.0-dp2-final Design Partner artifact.

## Supported Provider Scope

Microsoft Entra ID is the initial provider target for RC1.

The release should not be assumed to support additional identity, cloud, infrastructure, or security providers unless the frozen Release Notes explicitly state that support.

## Planned Providers Not Yet Guaranteed in RC1

Potential future provider expansion includes:

- AWS;
- Google Cloud;
- Okta;
- SecureW2;
- GitHub;
- NetBox;
- Zabbix;
- additional enterprise identity and infrastructure providers.

These are roadmap directions.

They are not operational capabilities until included in a validated release.

## Planned Intelligence Domains

Potential future intelligence domains include:

- Threat Intelligence;
- Vulnerability Intelligence;
- Compliance Intelligence;
- Asset Intelligence;
- CIAM;
- SaaS Governance;
- Cloud Security;
- Endpoint Intelligence.

External publications and authoritative sources such as CISA KEV or DISA content may be available through future licensed extensions.

Core should not imply operational ingestion or analysis of those external publications unless the corresponding capability is licensed and enabled.

## Deployment Limitations

The supported 0.14.0-dp2-final deployment model is the frozen customer package using docker-compose.yml, the supplied Docker image archives, .env.release configuration, and no customer-side source build contexts.

Until deployment validation is complete, do not assume support for:

- every host operating system;
- every Docker version;
- every Docker Compose version;
- every container runtime;
- Kubernetes deployment;
- air-gapped deployment;
- offline installation;
- arbitrary reverse proxies;
- every enterprise ingress controller;
- every proxy configuration;
- every TLS termination pattern.

Only the patterns validated during RC deployment testing should be presented as supported.

## Host Requirements

Final CPU, memory, storage, operating system, Docker, and Compose requirements must be populated from the frozen RC artifact.

Development workstation specifications are not customer support statements.

## Network Limitations

The frozen Core v1.0 Docker release publishes only the USOP web ingress to the customer host. The default host port is TCP 8080 and may be changed through USOP_WEB_PORT.

API TCP 8000 and PostgreSQL TCP 5432 remain Docker-internal and are not customer-facing ports.

The Microsoft Entra runtime requires DNS resolution and outbound TCP 443 access to:

- login.microsoftonline.com
- graph.microsoft.com

Broad unrestricted Internet egress is not required for the Core runtime.

The bundled USOP ingress is HTTP. Network-accessible deployments require customer-controlled TLS termination ahead of USOP. Direct HTTP TCP 8080 access should be limited to an accepted local or isolated evaluation boundary.

Explicit HTTP/HTTPS proxy configuration has not been validated for the Core v1.0 Design Partner release.

IPv6-only Docker egress has not been validated as a supported deployment requirement.

Build-time access to image registries and software package repositories is separate from the frozen application runtime egress contract.

## Microsoft Graph Permissions

The frozen Core v1.0 Microsoft Entra connector requires these Microsoft Graph application permissions:

- User.Read.All
- GroupMember.Read.All
- RoleManagement.Read.Directory

Administrator consent is required.

The validated Core connector does not require Directory.Read.All, Group.Read.All, Application.Read.All, or Device.Read.All.

The permission matrix was validated against the exact connector operations and selected properties used by the release.

Microsoft Graph API behavior remains an external dependency. Permission sufficiency does not guarantee that every Microsoft Graph endpoint returns every possible directory object type in every API version.

### Service-Principal Group Membership

USOP Core v1.0 does not claim complete service-principal group-membership visibility.

The frozen connector collects direct group membership from Microsoft Graph v1.0 GET /groups/{id}/members. Microsoft documents a known issue in which service principals are not listed as group members through that v1.0 operation.

Release validation reproduced the limitation against a live Microsoft Entra tenant. A service principal directly assigned to the validation group was absent from GET /groups/{id}/members but was visible through GET /groups/{id}?$expand=members as #microsoft.graph.servicePrincipal.

USOP does not use the beta Graph endpoint as a production workaround.

USOP also does not treat $expand=members as an authoritative replacement for the paginated direct-membership collection, and it does not substitute transitiveMembers for direct relationship semantics.

Until a stable, paginated, least-privilege collection strategy is validated, absence of a service-principal membership edge in USOP is not proof that the relationship is absent from Microsoft Entra.

## Secret Provider Limitations

USOP Core 0.14.0-dp2-final operationally supports only environment-managed secret configuration through:

USOP_SECRET_PROVIDER=env

External secret-provider retrieval is not supported in this Design Partner release.

Potential future providers include:

- Keeper;
- Azure Key Vault;
- AWS Secrets Manager;
- HashiCorp Vault;
- other customer-owned secret providers.

Their presence in architecture or future-product planning does not imply current operational support.

## Environment Secret Mode

The customer-owned .env.release file is the validated runtime configuration mechanism for this release.

Customers are responsible for protecting that file, restricting access, excluding it from source control, and rotating secrets according to local policy.

## Credential Rotation

A normal Docker Compose restart was validated during clean-room acceptance and preserved database schema, service health, and readiness.

This does not mean every credential can be hot-reloaded without recreating or restarting the affected service.

For rotated credentials, update the authoritative customer credential, update .env.release, recreate or restart the affected USOP service, and verify health and provider connectivity.

## Authentication and User Access

The customer-facing release must accurately document the supported platform-user authentication model.

If enterprise SSO, federation, RBAC extensions, or additional authentication mechanisms are not validated in RC1, they must not be implied as supported.

## Organizational Memory Boundaries

USOP preserves organizational decisions and knowledge required by its workflows.

Organizational Experience supports analyst judgment.

Historical decisions must not silently suppress new material security changes.

A new material authorization delta must create a new analyst decision opportunity.

## PIM and Eligible Role Assignment Limitation

USOP Core governance requires material privilege changes to create a new analyst decision opportunity even when an assignment is eligible, temporary, or activated through Microsoft Entra Privileged Identity Management.

DP2 live validation proved material role-assignment collection, authorization-event generation, and pending analyst work-item generation for the authorization states available in the validation tenant.

PIM-specific eligible assignment collection, activation-state collection, and temporary activation lifecycle behavior were not independently live-validated for 0.14.0-dp2-final.

Customers should therefore not interpret this Design Partner release as proof of complete Microsoft Entra PIM lifecycle coverage.

When PIM or equivalent authorization state becomes available to USOP, prior decisions, exceptions, or scheduled reviews must not silently suppress a new material privilege change.

## Review Scheduling Boundaries

Review schedules support periodic reassessment of accepted decisions and governed exceptions.

Scheduled review windows do not suppress immediate review of new material authorization changes.

## Data Authority Boundaries

USOP does not replace authoritative source systems.

Examples include:

- Microsoft Entra ID;
- Microsoft Graph;
- customer secret platforms;
- external security products;
- authoritative cloud or infrastructure systems.

USOP may normalize and persist operational state needed for its own workflows, but source-system authority remains external.

## Storage and Archival Limitations

The final RC documentation must distinguish between:

- active USOP application storage;
- organizational memory retained by USOP;
- customer-controlled external archival;
- source-system data that remains external.

Provider-neutral customer-controlled archival is part of the long-term design direction.

If external archival is not operational in RC1, it must be documented as unavailable rather than implied as complete.

## Backup and Restore

A logical PostgreSQL backup and restore procedure was validated for 0.14.0-dp2-final.

Release validation restored the logical backup into an isolated PostgreSQL environment and verified the expected schema and recovery canary.

This validation establishes the supported logical PostgreSQL recovery path for the frozen Design Partner artifact.

It does not establish support for every customer-specific backup platform, storage product, filesystem snapshot mechanism, volume snapshot implementation, disaster-recovery topology, or enterprise retention workflow.

Do not assume that copying container files alone produces a valid backup.

The persistent PostgreSQL data and customer-owned deployment configuration remain part of the customer recovery boundary.

Customers integrating USOP into an enterprise backup or disaster-recovery platform should validate that integration against their own recovery objectives.

## Upgrade Limitations

Release validation for 0.14.0-dp2-final proved a controlled database migration compatibility scenario.

The validated procedure downgraded the PostgreSQL schema by one Alembic revision and then re-upgraded to the frozen head revision with validation data preserved.

This proves the tested one-revision migration path. It does not establish support for upgrades from arbitrary development builds, arbitrary historical USOP releases, or unknown future schema versions.

Customers should use only upgrade procedures explicitly documented for the source and target release involved.

## Rollback Limitations

The validated rollback evidence is limited to the tested one-revision Alembic downgrade and re-upgrade sequence with data preservation.

Rollback may involve more than replacing an application image.

Database migrations, configuration-contract changes, persistent application state, and release-specific image compatibility may affect rollback behavior.

The 0.14.0-dp2-final validation does not establish arbitrary cross-version application or database rollback support.

Only rollback or restoration behavior explicitly validated for the applicable frozen release should be treated as supported.

## UI Limitations

The customer release may contain intentional progressive disclosure and compact panels.

Collapsed information is not necessarily unavailable.

The interface should prioritize operational decisions over exhaustive detail.

If an expected capability is not visible, first confirm whether it exists behind supported expansion or detail controls before classifying the behavior as missing.

## Screenshot and Documentation Drift

Screenshots are intentionally not embedded in the 0.14.0-dp2-final Design Partner User Guide.

The live frozen USOP interface is the authoritative visual reference for this release.

This avoids distributing screenshots that may become stale, expose demonstration identifiers, or diverge from the exact customer deployment.

Future screenshots must be generated from the corresponding frozen release artifact and maintained as release-controlled documentation.

A screenshot from a development build, older release, or unrelated validation environment must not be presented as authoritative customer documentation.

## Performance Expectations

Final performance expectations must be based on validation, not intuition.

Performance characteristics for 0.14.0-dp2-final remain Design Partner evaluation targets, including:

- dashboard responsiveness;
- investigation load time;
- graph responsiveness;
- synchronization performance;
- container resource usage;
- database behavior.

No unsupported performance SLA should be implied.

## Scale Limitations

The maximum validated organization size, identity count, graph size, synchronization volume, and decision-history volume must be determined through RC validation.

Until measured, do not claim unlimited enterprise scale.

## Error Handling Limitations

Customer-facing error states should explain the problem, operational impact, and next action.

If a failure still exposes implementation-heavy output or requires developer-only troubleshooting, it should be treated as an RC readiness issue.

## Logging Limitations

Logs must not intentionally expose secrets.

However, customers remain responsible for protecting their local logging systems and access to container logs.

The final release should document known logging destinations and retention assumptions.

## Monitoring Limitations

The current operational monitoring model includes the application health endpoint, container state, synchronization state, and Operational Pulse where supported.

If direct integration with external monitoring platforms is not validated in RC1, it should not be implied as supported.

## Reporting Limitations

Enterprise reporting, executive exports, scheduled reporting, or other future reporting capabilities may not be part of RC1 unless explicitly listed in the frozen Release Notes.

## AI and Automation Boundaries

USOP Core should not be assumed to provide an autonomous AI analyst unless that capability is explicitly released.

Decision Intelligence is intended to remain explainable and governed.

Automation must not silently replace required analyst decisions for material security changes.

## Licensing and Extension Boundaries

Future capabilities may be delivered as optional licensed extensions.

Core may support linking external publications or capabilities without operationalizing them.

A licensed extension may be required before USOP ingests, analyzes, correlates, or acts on certain external intelligence sources.

The frozen customer package must state which capabilities are included under the evaluated license.

## Design Partner Program Boundaries

Design Partners are evaluating the product.

They are not expected to:

- patch the application independently;
- modify the source code;
- broaden Entra permissions beyond the documented release;
- bypass security controls to make the product work;
- redistribute release artifacts outside the participating organization;
- expose secrets during troubleshooting.

Unexpected behavior should be reported through the Design Partner process.

## Known Limitation vs Defect

Use this distinction:

### Known Limitation

A behavior or capability boundary that is accurately documented and accepted for RC1.

### Defect

Behavior that:

- contradicts the documented release;
- breaks a supported workflow;
- exposes incorrect operational truth;
- creates a security or data-integrity risk;
- prevents supported deployment or normal use.

## Reporting Unexpected Behavior

When reporting an unexpected condition, provide:

```text
Release Version:
Build / Image Identifier:
Page / Workflow:
Expected Behavior:
Observed Behavior:
Operational Impact:
Reproduction Steps:
Sanitized Evidence:
```

Do not include:

- client secrets;
- access tokens;
- refresh tokens;
- private keys;
- complete `.env` files;
- secret-provider credentials.

## Customer Responsibilities

The customer remains responsible for:

- host operating system security;
- Docker/runtime security;
- firewall and egress policy;
- DNS;
- TLS certificates and ingress where applicable;
- Entra application ownership;
- Graph permission approval;
- credential rotation;
- secret-provider security;
- backup policy;
- retention policy;
- access to logs and persistent storage;
- local vulnerability and patch management.

USOP should not require weakening these controls.

## Design Partner Release Review

This document has been reconciled against the frozen 0.14.0-dp2-final Design Partner artifact and the completed clean-room validation evidence.

Remove any limitation that no longer applies.

Add any limitation discovered during:

- dependency patching;
- regression testing;
- container validation;
- clean-room installation;
- performance validation;
- security review;
- Design Partner packaging.

Populate final statements for:

- supported providers;
- supported secret providers;
- host requirements;
- runtime versions;
- ports;
- network destinations;
- Graph permissions;
- scale boundaries;
- performance expectations;
- backup/restore;
- upgrade/rollback;
- authentication model;
- known UI limitations.

## Relationship to Other Customer Documents

Read this document with:

- `01-Installation-Guide.md`
- `02-Secrets-Configuration-Guide.md`
- `03-Security-Deployment-Guide.md`
- `04-User-Guide.md`
- `05-Design-Partner-Guide.md`
- `06-Feedback-Questionnaire.md`
- `07-Release-Notes.md`

Release Notes explain what RC1 includes.

This document explains the boundaries of that release.

## Limitation Management Principle

> **Customers should encounter documented boundaries, not surprises.**

If a limitation can materially affect deployment, security, trust, or the investigation workflow, it must be documented before the release is distributed.

## Release Success Criteria

> **USOP Core v1.0 RC1 is ready for Design Partner delivery only when its supported capabilities and known boundaries are both documented accurately enough that a customer can evaluate the product without discovering material surprises through trial and error.**

If an important limitation is known but undocumented, the release is not ready.
