USOP Engineering Development Workflow
Purpose

This document defines the standard engineering workflow used to build USOP.

The objective is not simply to write software.

The objective is to continuously improve the platform while preserving architectural integrity, maintaining engineering quality, and supporting the long-term product vision.

Every contributor should follow this workflow.

Engineering Philosophy

USOP is designed to evolve continuously.

New capabilities should extend existing architecture whenever practical rather than replacing mature components.

The platform should become simpler to extend over time—not more complicated.

Every implementation should strengthen the architecture for future providers and future capabilities.

Standard Engineering Workflow

Every implementation follows the same sequence.

Inspect

↓

Understand

↓

Extend

↓

Review

↓

Test

↓

Commit

↓

Demonstrate

Skipping steps increases technical debt and reduces confidence in future development.

Step 1 — Inspect

Before implementing anything:

Inspect the existing repository.

Understand:

Existing architecture
Existing domain models
Existing services
Existing APIs
Existing workflows
Existing tests
Existing documentation

Never assume a capability does not already exist.

The first objective is always to avoid reinventing the wheel.

Step 2 — Understand

Determine:

Why the existing implementation exists.
What architectural decisions led to it.
Which ADRs influence the design.
Which Product Constitution principles apply.

If the current implementation solves the problem adequately, extend it.

Do not replace working architecture without a compelling reason.

Step 3 — Extend

Favor extending mature components.

Prefer:

Existing services
Existing graphs
Existing provider models
Existing reconciliation logic
Existing normalization
Existing abstractions

Avoid creating parallel implementations.

Every extension should strengthen the existing architecture.

Step 4 — Review

Before testing:

Review the implementation for:

Product alignment
Architectural consistency
Provider neutrality
Naming consistency
Future extensibility
Simplicity

Ask:

"Would this still make sense when five providers exist?"

Step 5 — Test

Every implementation must include:

Unit validation
Integration validation
Regression testing
Live provider validation when available

Future capabilities should never break existing functionality.

Regression testing is mandatory before every commit.

Step 6 — Commit

Each commit should have exactly one architectural responsibility.

Examples:

Good

Introduce canonical role types
Persist live Microsoft Entra groups
Generalize membership relationships

Poor

Synchronization updates
Bug fixes
Misc improvements

Commit messages should explain architectural intent.

Step 7 — Demonstrate

Every completed capability should answer:

What problem does this solve?
How does this reduce engineering effort?
How does this improve decisions?
How would this be demonstrated to a customer?

If a capability cannot be demonstrated, question whether it belongs in the current release.

Engineering Principles

USOP follows these principles.

Architecture before implementation

Understand the design before writing code.

Evolution before replacement

Extend mature architecture whenever practical.

Avoid unnecessary rewrites.

One responsibility per commit

Each commit should implement one architectural idea.

This simplifies reviews, testing, rollback, and historical understanding.

Provider-neutral design

Model security concepts—not vendor implementations.

Providers supply information.

The canonical domain represents meaning.

Canonical normalization

Normalization preserves provider identity.

It does not resolve database relationships.

Canonical reconciliation

Reconciliation resolves provider references into canonical entities.

Shared reusable services

Avoid duplicated logic.

Generalize reusable patterns before implementing the second use case.

Security-first design

Every capability should preserve:

Least privilege
Evidence integrity
Explainability
Traceability
Historical preservation

Historical information should accumulate rather than disappear.

Future intelligence depends on historical evidence.

Demonstrable value

Every sprint should improve the customer demonstration.

Engineering progress should translate into visible product value.

Decision Checklist

Before starting implementation ask:

Does the Product Constitution support this work?
Does this move Version 1 closer to completion?
Does this reduce engineering effort?
Does this improve security decisions?
Does existing architecture already solve part of this?
Can the capability be demonstrated?

If multiple answers are "No," reconsider the implementation.

Code Standards

When modifying source code:

Prefer complete file replacements over partial snippets.
Preserve formatting consistency.
Preserve existing architectural patterns.
Keep functions cohesive.
Avoid unnecessary abstraction.
Document architectural intent.
Definition of Done

A capability is complete when:

Implementation is finished.
Tests pass.
Regression testing passes.
Documentation is updated.
The capability supports the Product Constitution.
The capability strengthens the Version 1 demonstration.
The capability is understandable by future contributors.

Only then should the work be committed.

Continuous Improvement

The engineering workflow itself should evolve over time.

However, any changes should preserve the core principles established by the Product Constitution.

The workflow exists to support engineering excellence—not to create unnecessary process.
