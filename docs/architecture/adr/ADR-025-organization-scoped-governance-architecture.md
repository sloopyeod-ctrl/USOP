# ADR-025: Organization-Scoped Governance Architecture

- **Status:** Accepted
- **Date:** 2026-08-01
- **Decision Makers:** USOP Architecture
- **Supersedes:** None
- **Superseded By:** None

---

# Context

USOP exists to improve an organization's security posture.

Organizations entrust USOP with governance information representing:

- operational intent
- organizational knowledge
- access review decisions
- review campaigns
- governance history
- audit evidence
- security justification
- platform administration

Unlike synchronized provider information, these artifacts are created,
interpreted, and preserved inside USOP.

They therefore become part of the organization's intellectual property.

USOP must preserve that ownership.

As USOP evolves toward:

- enterprise deployments
- managed security providers (MSPs)
- consulting organizations
- commercial SaaS
- multi-organization deployments

organizational isolation becomes a foundational architectural requirement.

USOP must never become the source of a cross-organization information
disclosure.

---

# Problem

Inspection during RC-001.4 planning identified an architectural inconsistency.

Reviewer Workbench currently aggregates Access Reviews and Review Campaigns
without explicit organizational ownership.

The current implementation is acceptable during early single-organization
development.

It is not architecturally correct for enterprise deployment.

The inspection identified:

- AccessReview does not own organization_id.
- ReviewCampaign does not own organization_id.
- ReviewerWorkbench therefore cannot perform organization-scoped queries.
- Dashboard summaries aggregate every active review rather than reviews
  belonging to one organization.

This architecture would eventually permit incorrect governance summaries in
multi-organization deployments.

Authorization alone cannot safely solve this problem because ownership has not
been modeled.

---

# Decision

USOP adopts Organization-Scoped Governance.

Every governance artifact belongs to exactly one Organization unless explicitly
defined as Platform Global.

Organization ownership becomes part of the canonical data model rather than a
query-time filter.

Ownership precedes authorization.

Authorization protects ownership.

It does not create ownership.

---

# Architectural Principle

## USOP should never become the security concern.

Every architectural decision involving governance information must strengthen
organizational isolation rather than rely upon authorization alone.

If one organization can observe another organization's governance because of
architecture, the architecture is incorrect regardless of whether permissions
currently prevent access.

Security boundaries belong inside the architecture.

---

# Organization-Owned Artifacts

The following artifacts belong to exactly one Organization.

- Access Reviews
- Review Campaigns
- Decision Records
- Decision Knowledge
- Knowledge Assets
- Governance Policies
- Reviewer Workbench
- Platform Users
- Platform Roles
- Platform Permissions
- Audit Events
- Governance Jobs
- Organization Settings
- Review Schedules
- Commercial Licenses

These resources must expose organization ownership throughout:

- persistence
- repositories
- services
- APIs
- frontend workflows

---

# Platform-Global Components

Some platform capabilities intentionally remain organization-independent.

These include:

- Provider Registry
- Provider Catalog
- Connector Framework
- Connector Health Framework
- Connector Interfaces
- Authentication Framework
- Licensing Engine
- Canonical Intelligence Models
- Platform Version
- Platform Configuration

Platform-global components contain no customer governance.

They provide infrastructure for organizations.

They do not own organizational decisions.

---

# Organization Boundary

Organization-owned information must never become visible outside the owning
organization unless an explicitly designed cross-organization capability
requires it.

Examples include:

- MSP administration
- delegated administration
- enterprise reporting
- platform-wide operational metrics

Aggregation must always be intentional.

Aggregation is never the default behavior.

---

# Ownership Hierarchy

The canonical ownership model becomes:

```
Organization
      │
      ├──────────────┐
      │              │
Identity      Review Campaign
      │              │
      └──────┬───────┘
             │
      Access Review
             │
      Reviewer Workbench
             │
     Operational Dashboard
```

Identity ownership and governance ownership are separate architectural
relationships.

Identity participation does not implicitly establish governance ownership.

---

# Repository Rules

Repositories owning governance artifacts require organization context.

Preferred repository methods resemble:

```python
list_for_organization(
    organization_id,
)
```

rather than:

```python
list_all()
```

for organization-owned resources.

Repositories become responsible for enforcing organizational boundaries before
business logic executes.

---

# Service Rules

Services coordinate organization-scoped operations.

Services preserve ownership established by repositories.

Services must not remove organizational boundaries through aggregation or
post-processing.

---

# API Rules

Organization-owned APIs follow canonical organization routing.

Example:

```
/api/v1/organizations/{organization_id}/...
```

Examples include:

- Decision Records
- Knowledge Assets
- Platform Users
- Future Reviewer Workbench
- Future Operational Attention

Platform-global APIs remain outside organization routing.

Examples include:

```
/health

/connectors/providers

/connectors/health
```

These describe platform capability rather than customer governance.

---

# Migration Strategy

Migration proceeds through incremental architectural evolution.

Phase 1

ADR

↓

Phase 2

Governance Models

organization_id ownership

↓

Phase 3

Repositories

organization-scoped queries

↓

Phase 4

Services

organization-aware orchestration

↓

Phase 5

API Contracts

organization-scoped governance endpoints

↓

Phase 6

Frontend

Platform Operations

Reviewer Workbench

↓

Phase 7

Operational Attention

---

# Consequences

## Positive

- Eliminates future cross-organization governance exposure.
- Enables MSP deployments.
- Enables commercial SaaS.
- Strengthens auditability.
- Simplifies authorization.
- Preserves organizational ownership.
- Aligns governance with every other organization-scoped capability.

## Negative

- Governance models require migration.
- Repository APIs become organization-aware.
- Existing tests require updates.
- Existing APIs require evolution toward organization routing.
- Frontend integration pauses until ownership exists.

These costs are accepted because organizational ownership is a foundational
security requirement rather than an optional feature.

---

# Rejected Alternatives

## Authorization-only isolation

Rejected.

Authorization should protect ownership.

It must not create ownership.

---

## Query filtering without ownership

Rejected.

Filtering is not ownership.

Incorrect queries remain architecturally possible.

---

## Global Reviewer Workbench

Rejected.

Governance belongs to organizations.

Operational work belongs to the organization performing it.

---

## Deferred tenancy until commercial release

Rejected.

Architectural security boundaries become significantly more expensive to add
after customer adoption.

---

# Relationship to Existing ADRs

ADR-017 establishes Evolution Before Replacement.

ADR-019 establishes Organizational Memory.

ADR-020 establishes Decision Knowledge relationships.

ADR-021 establishes Pipeline-Based Intelligence.

ADR-023 establishes Visual Intelligence.

ADR-024 establishes Provider Registry.

ADR-025 establishes the organizational security boundary protecting every
governance capability operating inside those architectures.

Together these ADRs define both sides of USOP's trust boundary.

Provider architectures govern how information enters the platform.

Organization-Scoped Governance governs how organizational decisions remain
owned by the organization that created them.

---

# Success Criteria

ADR-025 is complete when:

- every governance artifact has explicit organization ownership
- repositories require organization context
- services preserve ownership boundaries
- organization-owned APIs require organization routing
- platform-global components remain free of customer governance
- Reviewer Workbench becomes organization-scoped
- Platform Operations displays tenant-safe operational work
- multi-organization deployments cannot expose governance information through
  architectural design

---

# Final Architectural Principle

USOP improves an organization's security posture.

It must never become the source of an organization's security incident.

Security first.

Architecture first.

Trust by design.