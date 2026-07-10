# ADR-018: Canonical Relationship Model

* **Status:** Accepted
* **Date:** 2026-07-10
* **Decision Owners:** USOP Engineering
* **Scope:** Canonical security domain model and relationship architecture

---

## Context

USOP is evolving from an identity synchronization platform into a provider-independent Security Intelligence Platform.

Previous architectural decisions established canonical security entities including:

* Identity
* Account
* Group
* Role
* Permission

As live synchronization expands beyond Microsoft Entra, additional providers will introduce many different relationship models.

Examples include:

* Microsoft Entra Group Memberships
* Microsoft Entra Directory Role Assignments
* AWS IAM Role Trust Relationships
* AWS IAM Group Memberships
* Okta Group Memberships
* SailPoint Identity Relationships
* Kubernetes RBAC Bindings
* Linux Group Memberships
* Active Directory Nested Groups

Although every provider models these relationships differently, the underlying security concepts are fundamentally the same.

USOP should not preserve provider-specific relationship formats beyond the connector layer.

Instead, connectors should translate provider data into one canonical relationship model before normalization, reconciliation, persistence, graph construction, and intelligence processing.

This follows the architectural direction established by previous decisions emphasizing provider independence, canonical modeling, and evolution before replacement.

---

## Decision

USOP will represent all security relationships using a canonical relationship model.

Every relationship shall identify the originating security principal using:

* `subject_type`
* `subject_id`

The value stored in `subject_type` shall be validated using the canonical `PrincipalType` domain vocabulary.

Relationship targets remain explicit.

Examples:

### Membership

```text
subject_type
subject_id
group_id
```

### Role Assignment

```text
subject_type
subject_id
role_id
```

Future relationship types will follow the same pattern.

Examples include:

* Application Ownership
* Secret Usage
* Certificate Usage
* Administrative Unit Membership
* Device Assignment
* Workload Relationships

---

## Canonical Principal Vocabulary

The canonical application vocabulary is defined by `PrincipalType`.

Current values include:

* Account
* ServicePrincipal
* Device
* Group
* Workload
* ExternalPrincipal

Additional principal types may be introduced in future architectural decisions when required.

The database continues storing string values rather than database enums to preserve flexibility and simplify provider expansion.

---

## Architectural Principle

Relationships describe how canonical security principals interact with canonical security resources.

Provider-specific terminology must remain inside connector implementations.

The domain model owns security concepts.

---

## Canonical Relationship Flow

```text
Provider

↓

Connector Translation

↓

Canonical Relationship

↓

Normalization

↓

Reconciliation

↓

PostgreSQL

↓

Identity Graph

↓

Decision Intelligence

↓

Analyst Workspace
```

Every future connector shall follow this flow.

---

## Relationship Examples

Microsoft Entra User

↓

Member Of

↓

Security Group

becomes

```text
subject_type = Account
subject_id = <account-id>
group_id = <group-id>
```

---

Microsoft Entra Service Principal

↓

Member Of

↓

Security Group

becomes

```text
subject_type = ServicePrincipal
subject_id = <service-principal-id>
group_id = <group-id>
```

---

Nested Group

↓

Member Of

↓

Parent Group

becomes

```text
subject_type = Group
subject_id = <child-group-id>
group_id = <parent-group-id>
```

The relationship model remains unchanged.

Only the principal type changes.

---

## Decision Drivers

This decision is intended to:

* establish one canonical relationship architecture
* eliminate provider-specific relationship models
* support future identity providers without schema redesign
* simplify graph traversal
* simplify reconciliation
* simplify connector development
* reduce future database migrations
* support nested relationships
* support non-human identities
* improve long-term maintainability

---

## Consequences

### Positive

* One canonical relationship model across the platform
* Consistent graph construction
* Reusable reconciliation logic
* Reusable relationship traversal
* Simpler future connectors
* Easier provider expansion
* Cleaner intelligence layer
* Reduced technical debt

### Trade-offs

* Connectors perform additional translation work.
* The canonical model is intentionally more abstract than individual provider APIs.
* Relationship implementations require disciplined adherence to the domain model.

These trade-offs are considered acceptable because they significantly improve long-term extensibility.

---

## Evolution Strategy

Relationship tables should evolve toward the canonical relationship model rather than introducing provider-specific structures.

Existing implementations may migrate incrementally while preserving compatibility.

The preferred sequence is:

1. Introduce canonical domain vocabulary.
2. Generalize persistence models.
3. Migrate existing data safely.
4. Extend connectors.
5. Extend normalization.
6. Extend reconciliation.
7. Extend graph processing.
8. Build intelligence on top of the canonical model.

---

## Related ADRs

* ADR-004: Identity Graph
* ADR-013: Identity Correlation
* ADR-014: Shared Synchronization Pipeline
* ADR-017: Evolution Before Replacement

---

## Summary

USOP shall represent security relationships using one provider-independent canonical model.

Connectors translate provider-specific relationship data into canonical relationships.

Normalization validates the canonical model.

Reconciliation persists canonical relationships.

Graph services consume canonical relationships.

Decision Intelligence operates exclusively on canonical relationships.

This architecture allows Microsoft Entra, Active Directory, AWS IAM, Okta, SailPoint, Kubernetes, Linux, and future providers to participate in one consistent Security Knowledge Graph without redesigning the domain model.
