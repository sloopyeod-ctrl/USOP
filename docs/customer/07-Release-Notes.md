# USOP Core v1.0 - Release Notes

**Document:** 07-Release-Notes  
**Release Track:** USOP Core v1.0 Release Candidate  
**Status:** Release Candidate Draft  
**Audience:** Design Partners, Security Leaders, Security Analysts, IAM Teams, Platform Teams, Deployment Teams

## Purpose

These release notes summarize the scope, capabilities, deployment expectations, validation status, and known release boundaries of the USOP Core v1.0 Release Candidate.

This document is intended to help Design Partners understand exactly what is included in the evaluated release and what remains outside RC1 scope.

## Release Information

```text
Product: USOP Core
Release: v1.0
Release Stage: Release Candidate
Customer Program: Design Partner Validation
Build Identifier: To be frozen during RC packaging
Container/Image Identifier: To be frozen during RC packaging
Release Date: To be assigned at freeze
```

No build identifier, image digest, or release date should be considered final until the RC artifact has completed patching, regression, clean-room installation, and freeze.

## Executive Summary

USOP Core v1.0 establishes the permanent operational investigation model for the Unified Security Operations Platform.

The release is intentionally focused on identity-centered operational intelligence and the workflow required to help security professionals understand:

- what matters;
- why it matters;
- what to do next.

USOP Core is designed around Rapid Situational Awareness and a stable investigation experience that future providers and intelligence domains should inherit.

## Release Objective

RC1 exists to validate that USOP Core can be:

- securely deployed;
- configured without undocumented developer assistance;
- connected to the supported Microsoft Entra environment;
- used to identify operational priorities;
- used to guide investigations;
- used to record organizational decisions;
- trusted enough for realistic Design Partner evaluation.

RC1 is not intended to prove every future integration or intelligence domain.

It validates the permanent Core model.

## What's Included

USOP Core v1.0 includes the following product areas.

### Executive Dashboard

Provides an organization-level operational view intended to answer:

> What needs attention first?

### Investigation Workflow

Provides the primary analyst workflow from priority identification through decision and verification.

### Mission Brief

Provides immediate investigation orientation.

### Decision Intelligence

Provides evidence-backed recommendations and decision support.

### Operational Context

Provides supporting identity, graph, timeline, authorization, and exposure context where available.

### Organizational Experience

Provides relevant historical decisions and organizational knowledge.

### Organizational Decisions

Provides governed recording of organization-level dispositions and decision history.

### Review Scheduling

Supports periodic reassessment of governed decisions where available.

### Operational Pulse

Provides current synchronization and readiness information.

### Identity Intelligence

Provides the initial Core intelligence domain.

### Microsoft Entra Integration

Provides the initial supported identity-provider integration for RC1, subject to the exact frozen permission and deployment contract.

### Identity and Relationship Graphs

Provides relationship visualization and graph intelligence where supported by the frozen release.

### Attack Path and Exposure Intelligence

Provides supported exposure and relationship-based decision intelligence.

### Organizational Memory

Provides the foundation for persistent organizational learning.

## Product Governance

USOP Core v1.0 includes a formal product-governance baseline.

The following documents govern the product experience:

- `PRODUCT-DESIGN-STANDARDS.md`
- `PRODUCT-TERMINOLOGY.md`
- `VISUAL-DESIGN-SYSTEM.md`
- `PRODUCT-QUALITY-CHECKLIST.md`

These documents define how USOP should think, communicate, present information, and determine whether customer-facing capabilities are ready.

## Customer Documentation

RC1 customer documentation includes:

- `01-Installation-Guide.md`
- `02-Secrets-Configuration-Guide.md`
- `03-Security-Deployment-Guide.md`
- `04-User-Guide.md`
- `05-Design-Partner-Guide.md`
- `06-Feedback-Questionnaire.md`
- `07-Release-Notes.md`
- `08-Known-Limitations.md`

The exact release package should include all eight documents before customer distribution.

## Security Highlights

The RC process requires validation of:

- customer-owned credential handling;
- no secrets embedded in source or release artifacts;
- provider-neutral secret-source design;
- least-privilege Microsoft Graph permissions;
- documented network requirements;
- container image provenance;
- patch review before freeze;
- secret redaction in logs;
- documented persistence and backup boundaries;
- clean-room installation.

The Microsoft Graph application permission contract for the frozen Core connector is:

- User.Read.All
- GroupMember.Read.All
- RoleManagement.Read.Directory

These permissions require administrator consent and were independently validated against the exact Core connector operations. Directory.Read.All, Group.Read.All, Application.Read.All, and Device.Read.All are not required by the validated Core v1.0 workflow.

The Microsoft Entra connector uses the stable Microsoft Graph v1.0 direct-membership collection.

A known Microsoft Graph v1.0 limitation can omit service principals from GET /groups/{id}/members. USOP Core v1.0 therefore does not claim complete service-principal group-membership visibility.

The release does not use Microsoft Graph beta APIs as a production workaround and does not substitute transitive membership for direct relationship semantics.

Ports, image identifiers, and remaining outbound-destination requirements must still be populated from the frozen release artifact before RC1 distribution.

## Deployment Highlights

The supported customer deployment model is Docker-based.

The final RC package is expected to contain or reference:

- pinned container images;
- Docker Compose configuration;
- `.env.template`;
- version identifier;
- checksums;
- customer documentation;
- sample configuration where appropriate.

The exact host requirements and runtime versions will be frozen during deployment validation.

## Supported Initial Provider

The initial RC1 focus is Microsoft Entra ID.

The final release documentation must identify the exact supported connector capabilities and minimum Graph permission set.

No unsupported provider should be presented as operational in RC1.

## Product Evolution

USOP Core is intended to remain the permanent operational foundation of the platform.

Future releases may expand provider coverage and intelligence depth without requiring users to relearn the core investigation model.

Potential future provider expansion includes:

- AWS;
- Google Cloud;
- Okta;
- SecureW2;
- GitHub;
- NetBox;
- Zabbix;
- additional enterprise identity and infrastructure providers.

Potential future intelligence expansion includes:

- threat intelligence;
- vulnerability intelligence;
- compliance intelligence;
- asset intelligence;
- CIAM;
- SaaS governance;
- cloud security;
- endpoint intelligence.

A future capability should not be treated as available until it appears in the applicable release documentation.

## Architecture and Product Principles

RC1 preserves the following established principles:

- backend intelligence remains the source of truth;
- operational truth is not fabricated;
- deterministic intelligence is preferred before opaque automation;
- organization-aware governance;
- evolution before replacement;
- progressive disclosure;
- one primary question per major page;
- Rapid Situational Awareness;
- stable investigation workflows;
- organizational decisions and memory remain explicit.

## Material Authorization Changes

A material authorization delta must create a new analyst decision opportunity.

A prior decision, exception, temporary assignment, eligible assignment, PIM activation state, or scheduled review window must not silently suppress a new material privilege change.

This behavior remains part of the Core governance model and must survive RC validation.

## Review Scheduling

Organizations may use governed review intervals for accepted decisions and exceptions.

Scheduled reassessment does not replace immediate review of new material authorization changes.

## Release Validation Requirements

Before RC1 is delivered to a Design Partner, the frozen artifact must pass the final release-validation sequence.

At minimum:

- backend dependency review and patching;
- frontend dependency review and patching;
- container base-image review and patching;
- backend regression tests;
- frontend build;
- frontend lint;
- container build;
- container startup;
- health endpoint validation;
- Microsoft Entra authentication;
- supported synchronization;
- investigation workflow validation;
- decision recording validation;
- Organizational Experience validation;
- Operational Pulse validation;
- secret redaction review;
- clean-room installation using customer documentation only.

## Clean-Room Requirement

The customer release is not ready until a clean host can be deployed using only the frozen release package and customer-facing documentation.

The clean-room installation must not rely on:

- developer workstation state;
- source-tree secrets;
- undocumented environment variables;
- development database contents;
- prior local container state;
- VS Code;
- developer coaching.

Any undocumented dependency discovered during clean-room validation must be corrected before freeze.

## Release Freeze

After the RC artifact passes patching, regression, clean-room deployment, and final validation, the artifact becomes frozen.

After freeze, changes to any of the following require validation to be reopened:

- application code;
- dependency versions;
- container images;
- deployment configuration;
- `.env` contract;
- supported secret providers;
- Graph permissions;
- network requirements;
- persistence behavior;
- deployment-critical documentation.

The artifact delivered to Design Partners must be the exact artifact that passed final validation.

## Upgrade Notes

RC1 upgrade behavior will be finalized during deployment packaging.

The final release documentation must define:

- supported upgrade source versions;
- required backup steps;
- container replacement sequence;
- database migration behavior;
- configuration-contract changes;
- rollback procedure.

If upgrade from an earlier development build is not supported, state that clearly.

## Rollback Notes

Rollback behavior will be frozen with the deployment package.

At minimum, rollback guidance must identify:

- application/container rollback;
- database compatibility expectations;
- configuration rollback;
- persistent-data considerations;
- post-rollback health validation.

Do not assume that replacing a container image alone is always sufficient.

## Design Partner Expectations

Design Partners should evaluate the release according to:

```text
05-Design-Partner-Guide.md
```

and record structured results using:

```text
06-Feedback-Questionnaire.md
```

The goal is to validate:

- deployment quality;
- security review quality;
- Rapid Situational Awareness;
- decision quality;
- operational trust;
- performance;
- documentation;
- willingness to continue using USOP.

## Support and Issue Reporting

When reporting an issue, include:

- release version;
- build/image identifier;
- affected page or workflow;
- expected behavior;
- observed behavior;
- operational impact;
- reproduction steps;
- sanitized logs or screenshots where appropriate.

Do not submit:

- client secrets;
- access tokens;
- private keys;
- complete `.env` files;
- secret-provider credentials.

## Known Limitations

Known release boundaries and limitations are documented separately in:

```text
08-Known-Limitations.md
```

Design Partners should review that document before classifying expected RC1 behavior as a defect.

## Not Included Unless Explicitly Frozen Into RC1

Unless the final frozen documentation states otherwise, RC1 should not be assumed to include operational support for:

- every planned provider;
- every planned intelligence domain;
- every secret manager;
- every proxy or ingress pattern;
- every operating system;
- every container runtime;
- every external archival provider;
- every enterprise reporting capability.

Release Notes describe validated capabilities, not roadmap aspirations.

## Documentation Accuracy Requirement

Before freeze, all references in these Release Notes must be reconciled with the exact RC artifact.

Remove or correct any capability statement that is not supported by the frozen release.

Populate:

- final build identifier;
- final image identifiers/digests;
- release date;
- supported host/runtime requirements;
- final Microsoft Graph permission set;
- final network requirements;
- final upgrade/rollback behavior.

No customer-facing release claim should be based on assumption.

## Relationship to Other Customer Documents

Read these Release Notes with:

- `01-Installation-Guide.md`
- `02-Secrets-Configuration-Guide.md`
- `03-Security-Deployment-Guide.md`
- `04-User-Guide.md`
- `05-Design-Partner-Guide.md`
- `06-Feedback-Questionnaire.md`
- `08-Known-Limitations.md`

Together, these documents define the customer experience for the evaluated release.

## Release Success Criteria

> **USOP Core v1.0 RC1 is ready for Design Partner delivery only when the exact frozen artifact can be securely installed, validated, understood, and used through the documented investigation workflow without undocumented developer assistance.**

If the Release Notes cannot accurately describe the frozen artifact, the release is not ready.
