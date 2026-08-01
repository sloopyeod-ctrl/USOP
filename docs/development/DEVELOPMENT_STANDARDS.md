# USOP Development Standards

## Purpose

This document defines the mandatory engineering standards for the Unified
Security Operations Platform.

These standards establish the rules contributors must follow.

The detailed engineering process is defined in:

docs/engineering/Development-Workflow.md

The standards answer:

> What rules must USOP engineering follow?

The workflow answers:

> How should those rules be applied during implementation?

---

# Platform Engineering Philosophy

USOP is engineered as a commercial Enterprise Security Decision Platform.

It is not a collection of disconnected features.

Every contribution must reinforce the platform architecture rather than
increase technical debt.

Every significant change should improve at least one of the following:

- Analyst effort
- Explainability
- Auditability
- Scalability
- Decision quality
- Organizational knowledge
- Cognitive load
- Architectural consistency

If a change improves none of these, it belongs on the roadmap rather than in the
current release.

---

# Mandatory Standards

## Inspect Before Implement

Before adding a subsystem, service, engine, page, API, schema, model, or
provider:

1. Inspect the existing implementation.
2. Identify current responsibilities.
3. Determine whether the capability already exists in whole or in part.
4. Extend or modernize existing architecture where practical.
5. Create a new component only when the existing architecture cannot
   reasonably own the responsibility.

Parallel implementations that own the same responsibility are prohibited
unless explicitly approved by an ADR.

## Evolution Before Replacement

Existing architecture should evolve whenever practical.

Replacement is an architectural decision, not the default response to a new
requirement.

## Architecture Before Implementation

Significant implementation begins only after the canonical architectural path
is understood.

Long-term architectural changes require an ADR before code is written.

## Backend Owns Business Logic

Security meaning belongs in backend domain logic.

The frontend renders prepared intelligence.

React must not become a second source of business logic.

## Controllers Remain Thin

Controllers accept requests, validate transport contracts, invoke services,
translate known errors, and return response models.

Controllers must not own persistence orchestration, domain calculations,
security interpretation, transaction rules, or provider-specific logic.

## Services Coordinate

Services coordinate application workflows.

They must not become oversized intelligence engines or duplicate canonical
domain rules.

## Models Own Persistence

Models define persistence structure.

Repositories own persistence access.

## Builders Construct Deterministic Intelligence

Builders have one responsibility, produce deterministic output, avoid
persistence and transport logic, and compose through pipelines.

## Providers Remain Vendor-Isolated

Providers retrieve and normalize facts from authoritative external systems.

Shared platform layers must remain provider-neutral.

## Authoritative Systems Remain Authoritative

USOP consumes authoritative systems.

USOP does not silently replace them as the source of truth.

## Human Accountability Is Mandatory

USOP prepares decisions.

Humans make decisions.

Material security decisions must preserve human attribution, evidence,
explainability, auditability, and historical context.

## Trust but Verify

A recorded decision does not prove remediation.

Risk changes only after authoritative synchronization verifies the resulting
state.

Decision Recorded
    â†“
Pending Verification
    â†“
Verified Remediation

## Material Authorization Changes Require Review

Material privilege changes must create analyst work.

Existing acceptance, governance intervals, temporary assignment, eligibility,
or PIM activation must not silently suppress new material authorization deltas.

## Visual Intelligence Is Architectural

Every screen should answer:

- What am I seeing?
- Why does it matter?
- What should I do next?

Interfaces must prioritize Eyes Before Mouse, Read Less Understand More,
Progressive Disclosure, explainability, operational priority, and 10â€“20 second
scan comprehension.

## Build Two, Extract One

Do not prematurely abstract frontend components.

Build two implementations, observe the shared pattern, and then extract one
shared component.

## One Responsibility per Commit

Each commit must represent one architectural responsibility.

Commits must be small, reviewable, testable, reversible, and clearly named.

## Regression Before Commit

Applicable regression testing is mandatory before every commit.

Code compiling successfully is not sufficient.

## Review the Exact Delta

Before commit, contributors must inspect status, whitespace, statistics, and
the complete working or staged diff.

The commit must contain only the intended architectural responsibility.

## Documentation Is Part of Implementation

Standards define rules.

Workflow defines process.

ADRs define long-term architectural decisions.

Specifications define detailed contracts.

Documentation must not duplicate another document's responsibility.

## Avoid Premature Optimization

Prefer clarity, correctness, and architectural consistency.

Future-proof stable seams.

Do not implement speculative systems.

## Protect Backward Compatibility

Existing API, provider, schema, persistence, and frontend contracts must remain
stable unless an intentional migration is approved.

## Deterministic Behavior

The platform should prefer deterministic behavior for provider enumeration,
intelligence construction, narrative output, API ordering, synchronization
results, tests, and operational summaries.

---

# Code Quality Standards

Source code should prioritize:

- Readability
- Explicit naming
- Cohesive functions
- Single responsibility
- Consistent formatting
- Type clarity
- Testability
- Maintainability

Avoid:

- Clever but opaque code
- Oversized services
- Business logic inside presentation
- Hidden side effects
- Duplicate constants
- Duplicate sources of truth
- Silent fallback behavior
- Unexplained compatibility aliases
- Unbounded abstraction

---

# Definition of Done

A change is complete only when:

- The implementation works
- Relevant ADRs are followed
- Focused tests pass
- Applicable full regression tests pass
- Browser or runtime behavior is verified when relevant
- The exact Git delta is reviewed
- Whitespace checks pass
- Documentation is current
- The commit has one responsibility
- The product benefit is explainable
- The repository remains clean except for intentionally excluded files

---

# Guiding Principle

> Build software that is easy to extend, easy to understand, and difficult to
> break.

The long-term integrity of the platform is more important than short-term
feature velocity.
