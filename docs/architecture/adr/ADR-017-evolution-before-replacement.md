# ADR-017: Evolution Before Replacement

- **Status:** Accepted
- **Date:** 2026-07-09
- **Decision Owners:** USOP Engineering
- **Scope:** Platform architecture and development practices

---

## Context

USOP is evolving from an identity governance proof of concept into a modular security intelligence and operations platform.

As the platform grows, new capabilities may appear to require new services, engines, frameworks, or architectural layers. However, USOP already contains functioning capabilities that may solve all or part of the same problem.

During Sprint 10.1, the Connector Framework v2 work initially appeared to require a new normalization framework.

An inspection of the existing backend identified an established synchronization pipeline containing:

- `SynchronizationEngine`
- `NormalizationEngine`
- `ReconciliationEngine`
- `IdentityGraphService`
- `GraphDifferenceEngine`
- `ChangeEventEngine`
- `AuditService`

Creating another normalization framework would have duplicated responsibilities and introduced competing implementations.

Instead, Connector Framework v2 was integrated into the existing synchronization pipeline by replacing the legacy connector entry point with the new `ConnectorManager` and provider contracts.

This preserved the existing downstream architecture while modernizing how external providers enter the platform.

---

## Decision

USOP will follow an **Evolution Before Replacement** engineering principle.

Before creating a new subsystem or replacing an existing architectural component, development must follow this sequence:

1. Inspect the existing implementation.
2. Identify its current responsibilities.
3. Determine whether the requested capability already exists in whole or in part.
4. Extend or modernize the existing implementation when practical.
5. Replace the implementation only when it cannot reasonably evolve.
6. Avoid maintaining competing systems that own the same responsibility.

Replacement must be an intentional architectural decision rather than the default response to a new requirement.

---

## Decision Drivers

This decision is intended to:

- preserve previous engineering investment,
- reduce duplicated responsibilities,
- limit unnecessary technical debt,
- maintain architectural consistency,
- reduce regression risk,
- simplify testing,
- preserve understandable data flows,
- and keep the platform easier to maintain.

---

## Architectural Principle

The preferred USOP development sequence is:

```text
Inspect
   ↓
Understand
   ↓
Extend
   ↓
Modernize
   ↓
Replace only when necessary