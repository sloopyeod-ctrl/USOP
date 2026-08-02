# ADR-026: Organizational Identity Architecture

- **Status:** Accepted
- **Date:** 2026-08-02
- **Decision Makers:** USOP Architecture
- **Supersedes:** None
- **Superseded By:** None

---

# Context

USOP is designed to support enterprise, managed security provider, consulting,
multi-organization, and future SaaS deployments.

In those environments, identity names are not globally unique and must never be
treated as though they are.

A managed service provider may operate USOP across hundreds of customer
networks. Each customer may contain identities with the same display name,
username, email alias, or source-system identifier. The same real-world person
may also legitimately participate in more than one customer organization.

For example, a provider such as Booz Allen Hamilton may operate USOP across 100
customer environments. An analyst viewing "John Smith" must always know whether
that identity belongs to Company 27, Company 75, or another customer context.
The display name alone cannot establish identity or ownership.

USOP must therefore distinguish between:

- a canonical actor correlated across available evidence
- that actor's explicit presence within one Organization
- provider accounts observed within that organizational context
- governance, reviews, decisions, and knowledge owned by that Organization

This distinction is required to implement ADR-025 safely.

---

# Problem

The current Identity model represents a canonical actor without explicit
organization ownership.

Operational security objects including Accounts and Access Reviews currently
reference Identity directly.

This creates an incomplete ownership chain:

```text
Identity
    |
    +-- Account
    +-- Access Review
    +-- Reviewer Workbench
```

Because Identity is not organization-scoped, downstream governance cannot rely
on it as a tenancy anchor.

Adding `organization_id` directly to Access Review would not solve the
underlying problem.

Adding `organization_id` directly to Identity would make each canonical actor
belong to exactly one Organization and would not safely represent:

- contractors working across multiple customers
- shared service providers
- delegated administrators
- consultants operating in multiple environments
- the same real-world person appearing in multiple organizations
- duplicate display names across unrelated organizations

USOP requires a separate organizational identity boundary.

---

# Decision

USOP adopts a two-layer identity architecture.

## Canonical Identity

A Canonical Identity represents a real-world actor independent of any single
Organization.

It answers:

> Who is this actor?

A Canonical Identity may represent:

- a human
- a service identity
- an application identity
- a workload identity
- another security principal recognized by USOP

Canonical Identity correlation must never merge actors based only on display
name, username, or another weak identifier.

## Organizational Identity

An Organizational Identity represents one Canonical Identity as observed and
governed within exactly one Organization.

It answers:

> Who is this actor within this Organization?

An Organizational Identity is organization-owned and becomes the tenancy
anchor for operational security and governance.

A Canonical Identity may have zero, one, or many Organizational Identities.

Each Organizational Identity belongs to exactly one Organization.

---

# Architectural Principle

> An identity may be correlated globally, but it is observed, governed, and
> acted upon only within an explicit Organization context.

Canonical correlation must never collapse organizational ownership.

Governance must never cross organizational boundaries merely because two
Organizational Identities may represent the same underlying actor.

---

# Ownership Model

The canonical relationship becomes:

```text
Canonical Identity
        |
        +-- Organizational Identity: Company 27
        |       |
        |       +-- Provider Accounts
        |       +-- Memberships
        |       +-- Role Assignments
        |       +-- Access Reviews
        |       +-- Decisions
        |       +-- Knowledge
        |       +-- Audit History
        |
        +-- Organizational Identity: Company 75
                |
                +-- Provider Accounts
                +-- Memberships
                +-- Role Assignments
                +-- Access Reviews
                +-- Decisions
                +-- Knowledge
                +-- Audit History
```

The same display name may appear in many Organizations without ambiguity.

The same real-world actor may participate in many Organizations without
combining their governance.

---

# Identity Uniqueness

Display names are descriptive, not authoritative.

USOP must not treat any of the following as globally unique by themselves:

- display name
- username
- email alias
- source display label
- provider-local object identifier without provider and tenant context

Organizational identity uniqueness must include explicit organization context.

Provider-account uniqueness must include sufficient source context, including
the provider and provider tenant or equivalent source boundary.

Canonical correlation may use stronger evidence, but correlation confidence
must remain separate from organizational ownership.

---

# Organizational Identity Rules

Every Organizational Identity:

- belongs to exactly one Organization
- references exactly one Canonical Identity
- has its own lifecycle state
- has its own governance history
- has its own access-review state
- has its own decision and knowledge context
- may reference one or more provider accounts
- must never expose governance from another Organization

A Canonical Identity may exist without an Organizational Identity while
correlation is incomplete or before organizational placement.

An Organizational Identity may not exist without an owning Organization.

---

# Account Rules

Provider Accounts are observed inside an organizational source context.

Accounts must evolve to reference Organizational Identity rather than relying
only on Canonical Identity.

The provider account relationship must preserve:

- Organization
- provider type
- provider tenant or equivalent source boundary
- external account identifier
- Organizational Identity
- optional Canonical Identity correlation through Organizational Identity

Account reconciliation must never attach an account to an Organizational
Identity owned by another Organization.

---

# Governance Rules

The following organization-owned artifacts attach to Organizational Identity
or otherwise carry explicit Organization ownership:

- Access Reviews
- Review Campaign participation
- Decision Records
- Decision Knowledge
- Knowledge Assets where identity-specific
- Governance Policies where identity-specific
- Reviewer Workbench entries
- Operational Attention
- Audit Events

Governance belongs to the Organization.

Canonical Identity correlation does not authorize cross-organization
governance access.

---

# API Rules

Operational identity APIs must evolve toward explicit Organization context.

Preferred organization-scoped routes resemble:

```text
/api/v1/organizations/{organization_id}/identities
/api/v1/organizations/{organization_id}/organizational-identities
/api/v1/organizations/{organization_id}/organizational-identities/{id}
/api/v1/organizations/{organization_id}/reviewer-workbench/dashboard
```

Platform-global correlation or administration APIs, if introduced, must be
explicitly privileged and must not become the default analyst experience.

The frontend must not render a bare identity name as sufficient operational
context.

Operational identity labels should include the Organization and expose source
context when useful.

---

# User Experience Rule

When an analyst sees an identity, the Organization must be visually clear.

A safe operational label resembles:

```text
John Smith
Organization: Company 27
Provider: Microsoft Entra ID
Source tenant: Company 27
```

This requirement prevents ambiguous identity presentation even when many
Organizations contain identities with identical names.

---

# Reconciliation Rules

Provider normalization remains platform-agnostic.

Provider-specific identifiers are normalized into USOP's canonical naming and
relationship conventions.

Reconciliation proceeds in organization context:

```text
Provider Account
        |
        v
Organizational Identity
        |
        v
Canonical Identity
```

The Organization boundary must be resolved before governance is created.

Canonical correlation may occur later and must not delay or weaken
organization isolation.

When correlation confidence is insufficient, USOP should preserve separate
Canonical Identities rather than risk incorrectly merging actors.

False separation is safer than cross-organization governance contamination.

---

# Security Boundary

USOP should never be the security concern.

Identity correlation must not create a path for:

- cross-organization review visibility
- cross-organization decision visibility
- cross-organization knowledge visibility
- cross-organization account attachment
- cross-organization audit contamination
- accidental MSP customer data aggregation

Aggregation across Organizations must be explicitly designed, authorized,
audited, and presented as cross-organization activity.

Aggregation is never the default.

---

# Migration Strategy

Implementation proceeds through small, regression-protected slices.

## Phase 1 — Architecture

Adopt ADR-026.

## Phase 2 — Organizational Identity Foundation

Introduce the Organizational Identity model, schema, repository, service, and
tests without removing existing Identity relationships.

## Phase 3 — Organization Placement

Create Organizational Identities for existing operational identities using
explicit migration rules.

Ambiguous records must not be silently assigned.

## Phase 4 — Account Evolution

Add Organizational Identity ownership to Accounts.

Preserve compatibility during migration.

## Phase 5 — Governance Evolution

Add explicit Organization and Organizational Identity ownership to Access
Reviews and related governance artifacts.

## Phase 6 — Review Campaign and Workbench

Make Review Campaigns and Reviewer Workbench organization-scoped.

## Phase 7 — API Evolution

Introduce canonical organization-scoped identity and governance routes.

## Phase 8 — Frontend Evolution

Display Organization context consistently across analyst and administration
workflows.

## Phase 9 — Legacy Removal

Remove obsolete global operational assumptions only after complete regression,
migration, and compatibility validation.

---

# Migration Safety Requirements

Migration scripts must:

- create backups or provide reversible database migrations
- avoid silent organization assignment
- stop when ownership cannot be resolved safely
- preserve source identifiers and audit history
- maintain referential integrity
- provide deterministic backfill results
- record or report unresolved records
- support rollback
- be validated against multi-organization test fixtures

No migration may infer Organization from display name alone.

---

# Consequences

## Positive

- Makes Organization the explicit operational security boundary.
- Supports MSP deployments across hundreds of customer environments.
- Prevents identity-name ambiguity.
- Allows one real-world actor to participate in multiple Organizations.
- Keeps governance separate even when canonical correlation exists.
- Preserves provider independence.
- Enables safe future SaaS and delegated-administration capabilities.
- Reduces future refactoring by correcting ownership before additional
  governance features are built.

## Negative

- Introduces another identity relationship.
- Requires staged model and API migration.
- Requires account and governance backfills.
- Requires broader regression coverage.
- Requires frontend identity labels to include Organization context.
- Makes reconciliation logic more explicit.

These costs are accepted because identity ownership and tenant isolation are
foundational security requirements.

---

# Rejected Alternatives

## Add organization_id directly to Identity

Rejected.

This would force each canonical actor into one Organization and would not model
cross-organization participation safely.

## Add organization_id only to Access Review

Rejected.

This would patch governance without fixing the missing identity ownership
boundary.

## Treat provider account as the organizational identity

Rejected.

Accounts are provider-specific observations.

Organizational Identity is provider-independent and may relate to multiple
accounts.

## Use display name or email for organization placement

Rejected.

These identifiers are not globally reliable and may be duplicated, recycled,
or shared.

## Defer identity tenancy until MSP deployment

Rejected.

Every additional account, review, decision, and connector built on the current
assumption would increase migration risk and cost.

---

# Relationship to Existing ADRs

ADR-017 establishes Evolution Before Replacement.

ADR-019 establishes Organizational Memory.

ADR-020 establishes canonical Decision Knowledge relationships.

ADR-021 establishes Pipeline-Based Intelligence.

ADR-024 establishes provider-independent connector registration.

ADR-025 establishes Organization-Scoped Governance.

ADR-026 establishes the identity ownership boundary required to implement
ADR-025 safely.

Provider architecture controls how external identity evidence enters USOP.

Organizational Identity Architecture controls how that evidence is placed,
governed, and presented within an Organization.

---

# Success Criteria

ADR-026 is complete when:

- Canonical Identity and Organizational Identity are separate concepts
- each Organizational Identity belongs to exactly one Organization
- a Canonical Identity may participate in multiple Organizations
- Accounts are organization-scoped through Organizational Identity
- Access Reviews are organization-scoped through explicit ownership
- Review Campaigns and Reviewer Workbench are organization-scoped
- operational APIs require Organization context
- analyst views always present Organization context
- duplicate display names across Organizations remain unambiguous
- canonical correlation cannot merge governance across Organizations
- multi-organization tests prove isolation by construction

---

# Final Architectural Principle

The same name does not mean the same identity.

The same person does not mean the same governance.

Organization context is mandatory.

Security first.

Isolation by design.

Trust through explicit ownership.
